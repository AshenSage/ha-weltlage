import json
import re
import time
from pathlib import Path
from unittest import TestCase
from bootstrap import coordinator_module
coordinator_module()
from weltlage_backend.cameras import parse_cameras, camera_image_url, nearest_cameras

class CameraTests(TestCase):
    def test_fixed_image_origins_and_paths(self):
        valid={"london":"https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.02151.jpg","finland":"https://weathercam.digitraffic.fi/C0150301.jpg","bc":"https://www.drivebc.ca/images/92.jpg"}
        for provider,url in valid.items():
            self.assertEqual(camera_image_url(url,provider),url)
            for bad in [url.replace('https:','http:'),url.replace('https://','https://x:y@'),re.sub(r'\.jpe?g$','.svg',url),url.replace('https://','https://127.0.0.1/'),url.replace('https://','https://evil.example/'),url.replace('/images/','/secret/') if provider=='bc' else url+'../secret']:
                self.assertIsNone(camera_image_url(bad,provider))
        self.assertIsNone(camera_image_url('https://www.drivebc.ca:8443/images/92.jpg','bc'))

    def test_tfl_available_camera_metadata_and_untrusted_images(self):
        row={"id":"one","commonName":"<script>x</script> A406", "lat":51.5,"lon":0,"additionalProperties":[{"key":"available","value":"true"},{"key":"imageUrl","value":"https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.02151.jpg"}]}
        items=parse_cameras(json.dumps([row,row]).encode(),'london',10000)
        self.assertEqual(len(items),1);self.assertEqual(items[0]['name'],'A406');self.assertIsNone(items[0]['observed']);self.assertIn('TfL',items[0]['credit'])
        row['additionalProperties'][1]['value']='https://evil.example/a.jpg'
        self.assertEqual(parse_cameras(json.dumps([row]).encode(),'london',10000),[])

    def test_fintraffic_only_collecting_presets(self):
        row={"geometry":{"coordinates":[24,60]},"properties":{"name":"Road","collectionStatus":"GATHERING","presets":[{"id":"C0150301","inCollection":True},{"id":"C0150302","inCollection":False}]}}
        body=lambda:json.dumps({'features':[row]}).encode()
        self.assertEqual(len(parse_cameras(body(),'finland',10000)),1)
        row['properties']['collectionStatus']='INACTIVE';self.assertEqual(parse_cameras(body(),'finland',10000),[])

    def test_drivebc_coordinates_and_status(self):
        bc={"id":92,"location":{"coordinates":[-122,49]},"name":"Bridge","is_on":True,"should_appear":True,"last_update_modified":"2026-10-11T08:00:00-07:00","credit":"Partner"}
        self.assertIn('Partner',parse_cameras(json.dumps([bc]).encode(),'bc',time.time())[0]['credit'])
        bc['marked_stale']=True;self.assertEqual(parse_cameras(json.dumps([bc]).encode(),'bc',time.time()),[])

    def test_nearest_camera_cap_preserves_finite_positions(self):
        items=[{'latitude':50+i*.01,'longitude':0,'id':i} for i in range(1000)]
        selected=nearest_cameras(items,50,0,600);self.assertEqual(len(selected),600);self.assertEqual(selected[0]['id'],0)
        for provider in ['london','finland','bc']:
            with self.assertRaises(ValueError):parse_cameras(b'{}',provider,10000)
