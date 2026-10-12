"""Create the HACS zip_release asset from a verified local frontend build."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
component=root/'custom_components/weltlage'
manifest=json.loads((component/'manifest.json').read_text())
built=json.loads((component/'frontend/build.json').read_text())
if manifest['version']!=built['version']:raise SystemExit('Version mismatch: run npm run build')
for f in ['weltlage-card.js','satellite-worker.js','cesium/Workers/createTaskProcessorWorker.js','cesium/Widgets/widgets.css']:
 if not (component/'frontend'/f).is_file():raise SystemExit('Missing generated asset: '+f)
with ZipFile(root/'weltlage.zip','w',ZIP_DEFLATED) as z:
 for f in sorted(component.rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ('.pyc','.pyo'):z.write(f,f.relative_to(component))
print('HACS asset: weltlage.zip')
