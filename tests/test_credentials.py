import json
import tempfile
from pathlib import Path
from unittest import TestCase
import bootstrap
from weltlage_backend.credentials import read_local_credentials

class CredentialsTests(TestCase):
 def test_absent_file_is_optional(self):
  self.assertEqual(read_local_credentials('/nonexistent/weltlage_credentials.json'),{})
 def test_only_supported_string_credentials_are_imported(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'credentials.json';p.write_text(json.dumps({'tomtom_api_key':' TEST-FIXTURE ','client_secret':'unused','other':'ignored'}))
   self.assertEqual(read_local_credentials(p),{'tomtom_api_key':'TEST-FIXTURE'})
 def test_errors_do_not_include_content(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'credentials.json'
   for text in ['{secret-fixture',json.dumps({'tomtom_api_key':123}),json.dumps({'tomtom_api_key':'fixture\nsecret'}),'x'*21000]:
    p.write_text(text)
    with self.assertRaises(ValueError) as e:read_local_credentials(p)
    self.assertNotIn('fixture',str(e.exception));self.assertNotIn('secret',str(e.exception))
