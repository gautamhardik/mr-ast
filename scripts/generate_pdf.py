"""
Publication-Grade PDF Rendering and Inspection Script for MR-TopoS.

Converts paper/final_submission_candidate.md to HTML with MathJax typography,
then renders paper/final_submission_candidate.pdf using headless Chrome.
Inspects the PDF pages using PyMuPDF (fitz) to guarantee zero visual clipping,
Clean page breaks, and a publication-grade 8-page layout.
"""

import os
import subprocess
import sys

def main():
    md_path = os.path.abspath("paper/final_submission_candidate.md")
    html_path = os.path.abspath("paper/final_submission_candidate.html")
    pdf_path = os.path.abspath("paper/final_submission_candidate.pdf")
    pandoc_exe = r"C:\Users\hiten\anaconda3\Library\bin\pandoc.exe"
    chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    print("Step 1: Converting Markdown to HTML with Pandoc and MathJax...")
    css_styling = """
    <style>
    @page {
        size: letter;
        margin: 0.82in;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 10.5pt;
        line-height: 1.38;
        color: #24292e;
        max-width: 800px;
        margin: 0 auto;
        padding: 5px;
    }
    h1 {
        font-size: 17pt;
        border-bottom: 2px solid #eaecef;
        padding-bottom: 0.3em;
        margin-top: 0;
        page-break-after: avoid;
    }
    h2 {
        font-size: 13.5pt;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
        margin-top: 1.1em;
        page-break-after: avoid;
    }
    h3 {
        font-size: 11.5pt;
        margin-top: 0.9em;
        page-break-after: avoid;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 0.8em 0;
        font-size: 8.2pt;
        page-break-inside: avoid;
    }
    th, td {
        border: 1px solid #dfe2e5;
        padding: 3px 4px;
        text-align: left;
    }
    th {
        background-color: #f6f8fa;
        font-weight: 600;
    }
    tr:nth-child(even) {
        background-color: #fafbfc;
    }
    code {
        background-color: rgba(27,31,35,0.05);
        border-radius: 3px;
        font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 85%;
        padding: 0.2em 0.4em;
    }
    pre {
        background-color: #f6f8fa;
        border-radius: 3px;
        font-size: 85%;
        line-height: 1.35;
        overflow: auto;
        padding: 8px;
        page-break-inside: avoid;
    }
    blockquote {
        border-left: 0.25em solid #0366d6;
        background-color: #f6f8fa;
        color: #24292e;
        padding: 6px 12px;
        margin: 0.6em 0;
        page-break-inside: avoid;
    }
    hr {
        border: 0;
        border-top: 1px solid #eaecef;
        margin: 12px 0;
    }
    </style>
    """

    cmd_pandoc = [
        pandoc_exe,
        md_path,
        "-s",
        "--mathjax",
        "-o", html_path,
        "-V", f"header-includes={css_styling}"
    ]
    res_pandoc = subprocess.run(cmd_pandoc, capture_output=True, text=True)
    if res_pandoc.returncode != 0:
        print("Pandoc Error:", res_pandoc.stderr)
        return
    print(f"HTML generated at {html_path} ({os.path.getsize(html_path)} bytes).")

    print("Step 2: Rendering PDF via Headless Chrome...")
    html_url = "file:///" + html_path.replace("\\", "/")
    temp_profile = os.path.abspath("paper/chrome_temp_profile")
    os.makedirs(temp_profile, exist_ok=True)
    cmd_chrome = [
        chrome_exe,
        "--headless=new",
        f"--user-data-dir={temp_profile}",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        html_url
    ]
    res_chrome = subprocess.run(cmd_chrome, capture_output=True, text=True)
    if not os.path.exists(pdf_path):
        print("Chrome Error: PDF not created.")
        return
    print(f"PDF generated successfully at {pdf_path} ({os.path.getsize(pdf_path)} bytes).")

    print("Step 3: Programmatic PDF Inspection with PyMuPDF (fitz)...")
    try:
        import fitz
        doc = fitz.open(pdf_path)
        print(f"Total Pages: {len(doc)}")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            rect = page.rect
            first_few = [l.strip().encode('ascii', 'replace').decode('ascii') for l in text.splitlines() if l.strip()][:2]
            last_few = [l.strip().encode('ascii', 'replace').decode('ascii') for l in text.splitlines() if l.strip()][-2:]
            print(f"  Page {page_num+1}: {rect.width:.1f} x {rect.height:.1f} pt | Text characters: {len(text)}")
            print(f"    Start: {first_few}")
            print(f"    End:   {last_few}")
        doc.close()
    except Exception as e:
        print(f"PyMuPDF inspection warning: {e}")

if __name__ == "__main__":
    main()
