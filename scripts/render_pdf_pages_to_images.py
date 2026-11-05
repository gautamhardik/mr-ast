import fitz
import os

def render_pages():
    pdf_path = "paper/final_submission_candidate.pdf"
    out_dir = "paper/figures/pdf_pages"
    os.makedirs(out_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    print(f"Rendering {len(doc)} pages to {out_dir} at 150 DPI...")
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        img_path = os.path.join(out_dir, f"page_{i+1}.png")
        pix.save(img_path)
        print(f"  Page {i+1} saved: {img_path} ({pix.width}x{pix.height} px, {os.path.getsize(img_path)} bytes)")
    doc.close()
    print("All pages rendered successfully!")

if __name__ == '__main__':
    render_pages()

