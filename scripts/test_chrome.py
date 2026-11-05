import os
import subprocess
import tempfile

td = tempfile.mkdtemp()
html_file = os.path.join(td, 'test.html')
png_file = os.path.join(td, 'test.png')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html><html><body style="background:#070a13;color:#38bdf8;padding:50px;"><h1>INSTANT SCREENSHOT</h1></body></html>')

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
cmd = [
    chrome,
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--run-all-compositor-stages-before-draw',
    f'--user-data-dir={td}',
    f'--screenshot={png_file}',
    '--window-size=1200,675',
    'file:///' + html_file.replace('\\', '/')
]
res = subprocess.run(cmd, capture_output=True, timeout=10)
print('Return code:', res.returncode)
print('PNG exists:', os.path.exists(png_file))
if os.path.exists(png_file):
    print('Size:', os.path.getsize(png_file))

