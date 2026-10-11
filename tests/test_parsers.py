import json
import unittest
from bootstrap import parsers as p

NOW = 1735732800.0
SOURCE = {"name": "Testfeed", "publisher": "Test", "url": "https://example.org/feed", "language": "de", "region": "world", "category": "politik"}


def rss(items):
    return ("<rss><channel>" + items + "</channel></rss>").encode()


class ParserTests(unittest.TestCase):
    def test_plain_text_removes_scripts_and_bounds_text(self):
        self.assertEqual(p.plain("<p>A &amp; B</p><script>alert(1)</script><style>x</style> C"), "A & B C")
        self.assertEqual(len(p.plain("x" * 1000)), 320)

    def test_link_validation_and_missing_links(self):
        self.assertEqual(p.safe_url("", SOURCE["url"]), "")
        for value in ("javascript:alert(1)", "https://user:pw@example.org/", "https://example.org/\nsecret"):
            self.assertEqual(p.safe_url(value), "")
        self.assertEqual(p.safe_url("/story", SOURCE["url"]), "https://example.org/story")
        self.assertEqual(p.parse_news(rss("<item><title>No link</title></item>"), "test", SOURCE, NOW), [])

    def test_xml_rejects_html_dtd_utf16_and_broken_rss(self):
        payload = '<!DOCTYPE rss [<!ENTITY x "oops">]><rss><channel/></rss>'
        for body in (b"<html/>", b"<rss/>", b"<rss>", payload.encode(), payload.encode("utf-16")):
            with self.subTest(body=body[:20]), self.assertRaises(ValueError):
                p.xml_root(body)
        with self.assertRaises(ValueError):
            p.xml_root(b"x" * (p.MAX_BYTES + 1))

    def test_rss_regions_topics_and_publication_date(self):
        body = rss('<item><title>Serbien: neue Energie-Pipeline</title><link>/story</link><description><![CDATA[<b>Belgrad</b> &amp; Schweiz]]></description><pubDate>Wed, 01 Jan 2025 11:00:00 GMT</pubDate></item>')
        article = p.parse_news(body, "test", SOURCE, NOW)[0]
        self.assertEqual(article["published"], NOW - 3600)
        self.assertEqual(article["summary"], "Belgrad & Schweiz")
        self.assertTrue({"world", "rs", "ch", "balkan", "europa"} <= set(article["regions"]))
        self.assertEqual(article["category"], "energie")

    def test_atom_missing_and_future_dates_are_not_invented(self):
        body = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Example</title><link href="/a"/><published>2025-01-01T13:00:00Z</published></entry><entry><title>Other</title><link href="/b"/><updated>2025-01-01T11:00:00</updated></entry></feed>'
        articles = p.parse_news(body, "test", SOURCE, NOW)
        self.assertEqual(len(articles), 2)
        self.assertTrue(all(a["published"] is None and a["first_seen"] == NOW for a in articles))

    def test_deduplication_and_retention(self):
        title = "Long identical headline about an international event"
        a = p.parse_news(rss(f'<item><title>{title}</title><link>https://example.org/a?utm_source=x</link></item>'), "a", SOURCE, NOW)[0]
        b = {**a, "url": "https://example.org/a?utm_source=y#x", "sources": [{"id": "b", "name": "B", "url": "https://example.org/a"}], "regions": ["world", "ch"]}
        c = {**a, "id": "old", "title": "Old story", "url": "https://example.org/old", "first_seen": NOW - 73 * 3600}
        merged = p.merge_news([a, b, c], NOW)
        self.assertEqual(len(merged), 1)
        self.assertEqual({s["id"] for s in merged[0]["sources"]}, {"a", "b"})
        self.assertIn("ch", merged[0]["regions"])
        self.assertEqual(len(a["sources"]), 1)

    def test_identical_titles_only_merge_near_in_time(self):
        a = p.parse_news(rss('<item><title>Long identical title about a repeating international event</title><link>/a</link></item>'), "a", SOURCE, NOW)[0]
        b = {**a, "id": "b", "url": "https://example.org/b", "first_seen": NOW - 13 * 3600}
        self.assertEqual(len(p.merge_news([a, b], NOW)), 2)

    def test_attack_on_refineries_is_conflict_and_energy_in_cyrillic(self):
        body = rss('<item><title>Напади на рафинерије нафте; разговори о изборима</title><link>/attack</link></item>')
        article = p.parse_news(body, "test", SOURCE, NOW)[0]
        self.assertEqual(article["category"], "konflikte")
        self.assertEqual(article["topics"], ["konflikte", "energie", "politik"])

    def test_cached_and_deduplicated_articles_keep_multiple_topics(self):
        a = {"id": "a", "title": "Attack on oil refinery", "summary": "", "url": "https://example.org/a", "first_seen": NOW, "published": None, "category": "energie", "regions": ["world"], "sources": [{"id": "a"}]}
        b = {**a, "summary": "Government election", "sources": [{"id": "b"}]}
        article = p.merge_news([a, b], NOW)[0]
        self.assertEqual(article["category"], "konflikte")
        self.assertEqual(article["topics"], ["konflikte", "energie", "politik"])
        self.assertNotIn("topics", a)

    def test_usgs_magnitude_dates_and_coordinates(self):
        def feature(ident, mag=4.5, ts=NOW - 3600, coords=None):
            return {"id": ident, "properties": {"mag": mag, "time": ts * 1000, "place": "Serbia", "url": "https://earthquake.usgs.gov/test"}, "geometry": {"coordinates": coords or [20, 44, 10]}}
        body = json.dumps({"type": "FeatureCollection", "features": [feature("valid"), feature("small", 4.4), feature("old", ts=NOW - 90000), feature("bad", coords=[200, 100]), None]})
        events = p.parse_usgs(body, NOW)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["severity"], "information")
        self.assertIn("rs", events[0]["regions"])
        self.assertEqual(events[0]["expires"], NOW - 3600 + 86400)
        with self.assertRaises(ValueError):
            p.parse_usgs(b"[]", NOW)

    def test_gdacs_no_duplicate_earthquakes_green_or_expired(self):
        def item(ident, kind="FL", level="Orange", end="2025-01-02T00:00:00Z"):
            return f'<item><title>Flood in Serbia</title><link>https://gdacs.org/{ident}</link><g:eventtype>{kind}</g:eventtype><g:eventid>{ident}</g:eventid><g:alertlevel>{level}</g:alertlevel><g:fromdate>2025-01-01T00:00:00Z</g:fromdate><g:todate>{end}</g:todate><g:iso3>SRB</g:iso3><p:point>44 20</p:point></item>'
        body = ('<rss xmlns:g="https://www.gdacs.org" xmlns:p="http://www.georss.org/georss"><channel>' + item("yes") + item("eq", "EQ") + item("green", level="Green") + item("expired", end="2024-12-31T00:00:00Z") + '</channel></rss>').encode()
        events = p.parse_gdacs(body, NOW)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["severity"], "orange")
        self.assertEqual(events[0]["latitude"], 44)
        self.assertIn("rs", events[0]["regions"])

    def test_gdacs_long_running_event_with_future_end_is_kept(self):
        body = rss('<item><title>Drought</title><eventtype>DR</eventtype><alertlevel>Red</alertlevel><fromdate>2024-01-01T00:00:00Z</fromdate><todate>2025-02-01T00:00:00Z</todate></item><item><title>No dates</title><eventtype>DR</eventtype><alertlevel>Red</alertlevel></item>')
        events = p.parse_gdacs(body, NOW)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["kind"], "Dürre")


if __name__ == "__main__":
    unittest.main()
