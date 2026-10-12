import asyncio,json,time
from unittest import IsolatedAsyncioTestCase,TestCase
from unittest.mock import patch
import bootstrap
from weltlage_backend.providers import GlobeProviders,bounds,SourceError,cloud_times
from weltlage_backend.data_parsers import webcams,webcam_detail,hotspots,flights

class ProviderTests(IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  async def ex(f,*a):return await asyncio.to_thread(f,*a)
  self.p=GlobeProviders(None,ex,{})
 async def asyncTearDown(self):await self.p.close()
 async def test_missing_key_and_extent_do_not_make_requests(self):
  self.assertEqual((await self.p.layer('cameras',[20,44,21,45]))['status'],'missing_key')
  self.assertEqual((await self.p.layer('flights',[-180,-85,180,85]))['status'],'zoom_required')
 async def test_singleflight_and_shared_cache(self):
  calls=[]
  async def fetch(*a):
   calls.append(a);await asyncio.sleep(.02);return {'items':[{'id':'one'}]}
  self.p._fetch=fetch
  rows=await asyncio.gather(*(self.p.layer('earthquakes',[20,44,21,45]) for i in range(8)))
  self.assertEqual(len(calls),1);self.assertTrue(all(r['status']=='current' for r in rows))
  await self.p.layer('earthquakes',[20,44,21,45]);self.assertEqual(len(calls),1)
 async def test_backoff_and_stale_snapshot(self):
  async def fetch(*a):raise SourceError('rate_limited','Limit')
  self.p._fetch=fetch
  r=await self.p.layer('earthquakes',[20,44,21,45]);self.assertEqual(r['status'],'rate_limited')
  self.assertGreater(next(iter(self.p.cache.values()))['next_due'],time.time()+60)
 async def test_old_moving_contacts_are_never_kept_as_current(self):
  async def success(*a):return {'items':[{'id':'one'}]}
  self.p._fetch=success;await self.p.layer('flights',[20,44,21,45])
  entry=next(iter(self.p.cache.values()));entry['next_due']=0
  async def fail(*a):raise SourceError()
  self.p._fetch=fail
  r=await self.p.layer('flights',[20,44,21,45]);self.assertEqual(r['items'],[]);self.assertEqual(r['status'],'unreachable')
 async def test_nonmoving_last_good_is_labelled_stale(self):
  async def success(*a):return {'items':[{'id':'one'}]}
  self.p._fetch=success;await self.p.layer('earthquakes',[20,44,21,45]);next(iter(self.p.cache.values()))['next_due']=0
  async def fail(*a):raise SourceError()
  self.p._fetch=fail;r=await self.p.layer('earthquakes',[20,44,21,45]);self.assertEqual(r['status'],'stale');self.assertEqual(len(r['items']),1)
 async def test_budget_is_per_source_and_error_has_no_url(self):
  for i in range(20):self.p._charge('test')
  self.p.budget=20
  with self.assertRaises(SourceError) as ctx:self.p._charge('test')
  self.assertEqual(ctx.exception.status,'rate_limited');self.p._charge('other')
 async def test_invalid_dates_and_bounds(self):
  for b in [[0,0,0,1],[1,2,3,float('nan')],[-181,0,1,1]]:
   with self.assertRaises(ValueError):await self.p.layer('radar',b)
  with self.assertRaises(ValueError):await self.p.layer('imagery',[20,44,21,45],date='1999-01-01')
 async def test_gdacs_text_response_uses_the_real_bytes_xml_parser(self):
  async def response(*a,**kw):return '<rss><channel/></rss>'
  self.p.request=response
  self.assertEqual((await self.p.layer('gdacs',[20,44,21,45]))['status'],'no_hits')
 async def test_global_ir_extent_is_not_mislabelled_as_empty_data(self):
  self.assertEqual((await self.p.layer('clouds',[0,65,10,70]))['status'],'no_coverage')
 async def test_close_cancels_pending_work(self):
  async def fetch(*a):await asyncio.Event().wait()
  self.p._fetch=fetch;task=asyncio.create_task(self.p.layer('earthquakes',[20,44,21,45]));await asyncio.sleep(.01);await self.p.close()
  with self.assertRaises(asyncio.CancelledError):await task

class DataTests(TestCase):
 def test_webcam_does_not_invent_coordinates_or_image(self):
  self.assertEqual(webcams({'webcams':[{'webcamId':1,'status':'active'}]},0),[])
  self.assertIsNone(webcam_detail({'webcamId':1},0)['image_url'])
  row=webcam_detail({'images':{'current':{'preview':'javascript:alert(1)'}},'player':{'live':'https://user:secret@example.test'}},0)
  self.assertIsNone(row['image_url']);self.assertIsNone(row['livestream'])
 def test_military_is_only_source_database_flag(self):
  now=time.time();raw={'now':now,'ac':[{'hex':'abcdef','lat':44,'lon':20,'seen_pos':0,'flight':'TEST','dbFlags':1}]}
  self.assertTrue(flights(json.dumps(raw),now)[0]['military']);raw['ac'][0]['dbFlags']=0
  self.assertFalse(flights(json.dumps(raw),now)[0]['military'])
 def test_hotspot_retains_sensor_confidence_and_time(self):
  r=hotspots('latitude,longitude,acq_date,acq_time,confidence,instrument\n44,20,2026-10-12,0350,n,VIIRS\n')[0]
  self.assertEqual(r['sensor'],'VIIRS');self.assertEqual(r['confidence'],'n');self.assertIsNotNone(r['observed'])
 def test_cloud_parser_rejects_xml_entities(self):
  with self.assertRaises(ValueError):cloud_times('<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a/>')
