import importlib
import json
from unittest import TestCase
import bootstrap

i = importlib.import_module("weltlage_backend.intel")
NOW = 1791726000
ORBIT = {"OBJECT_NAME":"Synthetic orbit", "OBJECT_ID":"DEMO", "NORAD_CAT_ID":99999, "EPOCH":"2026-10-11T12:00:00", "MEAN_MOTION":15.48, "ECCENTRICITY":.001, "INCLINATION":51.6, "RA_OF_ASC_NODE":86, "ARG_OF_PERICENTER":248, "MEAN_ANOMALY":111, "BSTAR":.00018, "MEAN_MOTION_DOT":.00009, "MEAN_MOTION_DDOT":0}


class IntelTests(TestCase):
    def test_flight_url_is_fixed_host_bounded_and_coarse(self):
        self.assertEqual(i.flight_url(44.3,20.7), ("https://api.adsb.lol/v2/point/45/20/250",45,20))
        for lat, lon in [(91,0),(0,-181),(float('nan'),0),("https://evil.example",0)]:
            with self.assertRaises(ValueError): i.flight_url(lat,lon)

    def test_flights_require_fresh_positions_and_convert_units(self):
        aircraft={"hex":"abc123","flight":" DEMO ","lat":44,"lon":20,"seen_pos":10,"alt_baro":10000,"gs":100}
        items=i.parse_flights(json.dumps({"now":NOW*1000,"ac":[aircraft,{**aircraft,"hex":"abc124","seen_pos":150},{**aircraft,"hex":"abc125","lat":95},{**aircraft,"hex":"bad link"}]}),NOW)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]["observed"],NOW-10)
        self.assertEqual(items[0]["altitude_m"],3048)
        self.assertEqual(items[0]["speed_kmh"],185)
        self.assertEqual(items[0]["name"],"DEMO")

    def test_old_or_invalid_flight_snapshots_are_rejected(self):
        for payload in [{"now":NOW-121,"ac":[]},{"now":NOW+61,"ac":[]},{"ac":[]},[]]:
            with self.assertRaises(ValueError): i.parse_flights(json.dumps(payload),NOW)
        self.assertEqual(i.parse_flights(json.dumps({"now":NOW,"ac":[]}),NOW),[])

    def test_satellite_epoch_and_elements_are_checked(self):
        self.assertEqual(len(i.parse_satellites(json.dumps([ORBIT]),NOW)),1)
        for change in [{"EPOCH":"2020-01-01T00:00:00"},{"ECCENTRICITY":1},{"MEAN_MOTION":0},{"BSTAR":None},{"NORAD_CAT_ID":1.5}]:
            with self.assertRaises(ValueError): i.parse_satellites(json.dumps([{**ORBIT,**change}]),NOW)
        self.assertEqual(i.parse_satellites('[]',NOW),[])
