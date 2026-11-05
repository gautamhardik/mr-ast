from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1200, 'height': 675})
        page.set_content('''
        <html>
        <body style="background:#0f172a; color:#f8fafc; display:flex; align-items:center; justify-content:center; height:100vh; font-family:sans-serif;">
            <h1 style="color:#38bdf8;">Playwright Ready</h1>
        </body>
        </html>
        ''')
        page.screenshot(path='paper/figures/test_playwright.png')
        browser.close()
    print('PLAYWRIGHT SUCCESS')
except Exception as e:
    print('PLAYWRIGHT ERROR:', e)

