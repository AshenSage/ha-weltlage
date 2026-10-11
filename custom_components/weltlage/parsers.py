"""Pure parsers: untrusted feeds are converted to bounded plain-text objects."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
import math
import re
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
import xml.etree.ElementTree as ET

from .const import MAX_BYTES, MAX_ARTICLES, RETENTION_HOURS


class _PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag in ("p", "br", "div", "li") and not self.hidden:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.hidden:
            self.hidden -= 1
        elif tag in ("p", "div", "li"):
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain(value, limit=320):
    parser = _PlainText()
    parser.feed(str(value or "")[:16000])
    text = re.sub(r"\s+", " ", unescape("".join(parser.parts))).strip()
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def safe_url(value, base=""):
    try:
        value = str(value or "").strip()
        if not value or any(ord(c) < 32 for c in value):
            return ""
        value = urljoin(base, value)
        p = urlsplit(value)
        if p.scheme.lower() not in ("https", "http") or not p.hostname or p.username or p.password:
            return ""
        if any(ord(c) < 32 for c in value):
            return ""
        return value[:2000]
    except ValueError:
        return ""


def canonical_url(value):
    p = urlsplit(value)
    pairs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in ("fbclid", "gclid")]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), urlencode(pairs), ""))


def stamp(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = parsedate_to_datetime(str(value).strip())
        except (ValueError, TypeError, OverflowError):
            return None
    if dt.tzinfo is None:
        # Do not invent a timezone for a broken publisher timestamp.
        return None
    try:
        return dt.timestamp()
    except (ValueError, OverflowError):
        return None


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat() if ts is not None else None


def local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def field(node, *names):
    for name in names:
        for child in node:
            if local(child.tag) == name.lower():
                return "".join(child.itertext()).strip()
    return ""


def xml_root(body):
    if len(body) > MAX_BYTES:
        raise ValueError("Feed ist zu gross")
    # Null removal also detects declarations in UTF-16/UTF-32 XML.
    if re.search(br"<!\s*(DOCTYPE|ENTITY)\b", body.replace(b"\x00", b""), re.I):
        raise ValueError("XML mit DTD/Entities wird nicht verarbeitet")
    try:
        root = ET.fromstring(body)
    except ET.ParseError as err:
        raise ValueError("Ungültiger XML-Feed") from err
    if local(root.tag) not in ("rss", "feed", "rdf"):
        raise ValueError("Antwort ist kein RSS-/Atom-Feed")
    if local(root.tag) == "rss" and not any(local(n.tag) == "channel" for n in root):
        raise ValueError("RSS-Feed hat keinen Channel")
    return root


_REGION_WORDS = {
    "ch": r"\b(?:schweiz\w*|swiss\w*|switzerland|suisse|svajcarsk\w*|швајцар\w*|oberbipp|bern|zürich|zurich)\b",
    "rs": r"\b(?:serbi\w*|srbij\w*|срби\w*|belgrad\w*|beograd\w*|београд\w*|arandjelovac|aranđelovac|аранђеловац|šumadij\w*|шумади\w*)\b",
    "balkan": r"\b(?:balkan\w*|балкан\w*|kosov\w*|косов\w*|bosni\w*|босн\w*|kroati\w*|croati\w*|hrvatsk\w*|хрват\w*|montenegr\w*|crna gora|црна гора|alban\w*|албан\w*|mazedon\w*|macedon\w*)\b",
    "europa": r"\b(?:europa\w*|europe\w*|европ\w*|european|deutschland|german\w*|frankreich|france|french|italien|italy|italian|österreich|austria|ukraine|ukrain\w*|украјин\w*|polen|poland|spanien|spain|britain|british|london|russia|russland)\b",
}
_TOPICS = [
    ("konflikte", r"\b(?:krieg\w*|war|wars|missile\w*|attack\w*|angriff\w*|waffenstillstand|ceasefire|military|militär\w*|invasion|ракет\w*|напад\w*|рат|рата|рату|сукоб\w*)\b"),
    ("natur", r"\b(?:earthquake\w*|erdbeben|flood\w*|überschwemm\w*|hurricane\w*|unwetter\w*|wildfire\w*|waldbrand\w*|поплав\w*|земљотрес\w*|олуј\w*)\b"),
    ("energie", r"\b(?:energie\w*|energy|oil|gas|fuel|diesel|erdöl|ölpreis\w*|strom\w*|pipeline\w*|lieferkett\w*|supply chain\w*|shipping|trade route\w*|нафт\w*|енерг\w*|горив\w*|дизел\w*)\b"),
    ("wirtschaft", r"\b(?:econom\w*|wirtschaft\w*|inflation|tariff\w*|zoll\w*|zölle|central bank\w*|interest rate\w*|економ\w*|инфлац\w*|царин\w*)\b"),
    ("technik", r"\b(?:technology|technolog\w*|cyber\w*|artificial intelligence|künstliche intelligenz|технолог\w*)\b"),
    ("politik", r"\b(?:election\w*|wahl\w*|diplom\w*|government\w*|regierung\w*|parlament\w*|president\w*|präsident\w*|minister\w*|избор\w*|председник\w*|влада|владе|влади|владу|владом|диплом\w*)\b"),
]


def classify_topics(text, source):
    """Keep every keyword match; primary topic follows the order above."""
    topics = [name for name, pattern in _TOPICS if re.search(pattern, text, re.I)]
    return topics or [source.get("category", "politik")]


def classify(text, source):
    text = text.lower()
    regions = {"world"}
    if source.get("region") not in (None, "world"):
        regions.add(source["region"])
    for region, pattern in _REGION_WORDS.items():
        if re.search(pattern, text, re.I):
            regions.add(region)
    if {"ch", "rs", "balkan"} & regions:
        regions.add("europa")
    if "rs" in regions:
        regions.add("balkan")
    category = classify_topics(text, source)[0]
    return sorted(regions), category


def parse_news(body, source_id, source, now):
    root = xml_root(body)
    items = [n for n in root.iter() if local(n.tag) in ("item", "entry")][:50]
    result = []
    for node in items:
        title = plain(field(node, "title"), 240)
        url = field(node, "link")
        for child in node:
            if local(child.tag) == "link" and child.get("href") and child.get("rel", "alternate") == "alternate":
                url = child.get("href")
                break
        url = safe_url(url, source["url"])
        if not title or not url:
            continue
        summary = plain(field(node, "description", "summary", "encoded", "content"))
        published = stamp(field(node, "pubdate", "published", "date", "updated"))
        if published is not None and (published > now + 300 or published < 0):
            published = None
        regions, category = classify(title + " " + summary, source)
        result.append({
            "id": sha256(canonical_url(url).encode()).hexdigest()[:20],
            "title": title, "summary": summary, "url": url,
            "published": published, "first_seen": now,
            "regions": regions, "category": category,
            "topics": classify_topics(title + " " + summary, source), "language": source.get("language", ""),
            "sources": [{"id": source_id, "name": source.get("publisher", source["name"]), "url": url}],
        })
    return result


def merge_news(items, now):
    valid = [dict(a) for a in items if now - (a.get("published") or a.get("first_seen", 0)) <= RETENTION_HOURS * 3600]
    valid.sort(key=lambda a: (a.get("published") or a.get("first_seen", 0)), reverse=True)
    by_url, by_title, result = {}, {}, []
    for a in valid:
        # Reclassify last-good cached articles too, including after a HTTP 304.
        a["topics"] = classify_topics(a["title"] + " " + a.get("summary", ""), {"category": a.get("category", "politik")})
        a["category"] = a["topics"][0]
        url = canonical_url(a["url"])
        title = re.sub(r"[^\w]+", " ", a["title"].lower()).strip()
        match = by_url.get(url)
        other = by_title.get(title) if len(title) >= 30 else None
        if match is None and other is not None and abs((a.get("published") or a["first_seen"]) - (other.get("published") or other["first_seen"])) < 12 * 3600:
            match = other
        if match is not None:
            match["sources"] = list({s["id"]: s for s in match["sources"] + a["sources"]}.values())
            match["regions"] = sorted(set(match["regions"] + a["regions"]))
            combined = set(match["topics"] + a["topics"])
            ordered = [name for name, _ in _TOPICS if name in combined]
            match["topics"] = ordered + sorted(combined - set(ordered))
            match["category"] = match["topics"][0]
            match["first_seen"] = min(match["first_seen"], a["first_seen"])
            continue
        a["sources"] = list(a["sources"])
        by_url[url] = a
        by_title[title] = a
        result.append(a)
    return result[:MAX_ARTICLES]


def number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def parse_usgs(body, now):
    obj = json.loads(body)
    if not isinstance(obj, dict) or obj.get("type") != "FeatureCollection" or not isinstance(obj.get("features"), list):
        raise ValueError("Ungültige USGS-Antwort")
    result = []
    for item in obj["features"][:200]:
        if not isinstance(item, dict):
            continue
        p = item.get("properties") or {}
        geometry = item.get("geometry") or {}
        if not isinstance(geometry, dict):
            continue
        coords = geometry.get("coordinates") or []
        if not isinstance(p, dict) or not isinstance(coords, list):
            continue
        mag, ts = number(p.get("mag")), number(p.get("time"))
        if mag is None or mag < 4.5 or ts is None or len(coords) < 2:
            continue
        ts /= 1000
        lon, lat = number(coords[0]), number(coords[1])
        if lat is None or lon is None or not -90 <= lat <= 90 or not -180 <= lon <= 180 or ts > now + 300 or now - ts > 86400:
            continue
        title = f"Erdbeben M {mag:.1f} · {plain(p.get('place'), 160)}"
        regions, _ = classify(title, {})
        result.append({"id": f"usgs_{item.get('id', '')}", "title": title, "source": "USGS", "source_id": "usgs", "kind": "Erdbeben", "published": ts, "expires": ts + 86400, "latitude": lat, "longitude": lon, "magnitude": mag, "severity": "information", "regions": regions, "url": safe_url(p.get("url")), "summary": "Erfasstes Erdbeben; keine Erdbebenvorhersage."})
    return sorted(result, key=lambda h: h["published"], reverse=True)[:60]


def parse_gdacs(body, now):
    root = xml_root(body)
    result = []
    kinds = {"FL": "Überschwemmung", "TC": "Tropischer Wirbelsturm", "VO": "Vulkan", "DR": "Dürre", "WF": "Waldbrand", "TS": "Tsunami"}
    for node in [n for n in root.iter() if local(n.tag) == "item"][:150]:
        kind = field(node, "eventtype").upper()
        # Earthquakes have a single source (USGS), avoiding duplicate event counts.
        if kind == "EQ":
            continue
        level = field(node, "alertlevel").lower()
        if level not in ("orange", "red"):
            continue
        start = stamp(field(node, "fromdate", "pubdate"))
        end = stamp(field(node, "todate"))
        if end is not None and end < now:
            continue
        if start is not None and start > now + 300:
            continue
        if end is None and (start is None or now - start > 30 * 86400):
            continue
        country = plain(field(node, "country"), 80)
        title = plain(field(node, "title"), 240)
        regions, _ = classify(country + " " + title, {})
        code = field(node, "iso3", "countryiso3").upper()
        if code == "CHE":
            regions = sorted(set(regions + ["ch", "europa"]))
        elif code == "SRB":
            regions = sorted(set(regions + ["rs", "balkan", "europa"]))
        lat = lon = None
        for child in node.iter():
            if local(child.tag) == "point":
                parts = (child.text or "").split()
                if len(parts) == 2:
                    lat, lon = number(parts[0]), number(parts[1])
        ident = field(node, "eventid", "guid") or title
        result.append({"id": "gdacs_" + sha256(ident.encode()).hexdigest()[:16], "title": title or kinds.get(kind, "Naturereignis"), "source": "GDACS", "source_id": "gdacs", "kind": kinds.get(kind, "Naturereignis"), "published": start, "expires": end, "latitude": lat, "longitude": lon, "severity": level, "regions": regions, "country": country, "url": safe_url(field(node, "link")), "summary": plain(field(node, "description"))})
    return result[:40]
