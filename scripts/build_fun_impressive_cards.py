"""
Build Fun, Impressive, Uncroppable Kaggle Cards and Thumbnails for MR-AST.

Generates:
1. Exact 560x280 (1x) and 1120x560 (2x Retina) Kaggle Card Image.
2. Centered safe-zone composition ensuring 0% cropping on rounded corners or responsive containers.
3. Multiple visual variants:
   - Mascot Branded (Charming 3D Gemma Cyber-Robot Agent + Glowing AST + Badges)
   - Mascot Clean Art (Pure 3D Mascot Artwork, no text overlay)
   - Quantum Core Branded (Epic 3D Holographic Tree + Knapsack Reactor Core)
   - Quantum Core Clean Art (Pure 3D Sci-Fi Key Art)
   - Square Thumbnail (1024x1024 and 560x560 for avatars & feeds)
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.makedirs('paper/figures', exist_ok=True)

# Upstream paths from image-generator subagents
p_mascot_wide = r'C:\Users\hiten\.gemini\antigravity\brain\bcb8822d-5e62-4199-8766-fbe0c3955413\mr_ast_fun_mascot_wide_1793913862237.jpg'
p_mascot_sq = r'C:\Users\hiten\.gemini\antigravity\brain\bcb8822d-5e62-4199-8766-fbe0c3955413\mr_ast_fun_mascot_square_1793913883791.jpg'
p_quantum_wide = r'C:\Users\hiten\.gemini\antigravity\brain\bcb8822d-5e62-4199-8766-fbe0c3955413\mr_ast_quantum_core_wide_1793913879722.jpg'

# 1. Copy raw high-res master art to paper/figures/
shutil.copy(p_mascot_wide, 'paper/figures/art_mascot_wide.jpg')
shutil.copy(p_mascot_sq, 'paper/figures/art_mascot_square.jpg')
shutil.copy(p_quantum_wide, 'paper/figures/art_quantum_wide.jpg')
print("Copied master 3D artwork to paper/figures/")

def crop_to_2_to_1(im):
    """Crop 16:9 image to exact 2:1 aspect ratio centered."""
    w, h = im.size
    target_h = w // 2
    top = (h - target_h) // 2
    return im.crop((0, top, w, top + target_h))

def try_load_font(size, bold=False):
    # Try standard system fonts
    font_paths = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf"
    ]
    if bold:
        font_paths = [
            "C:\\Windows\\Fonts\\segoeuib.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\calibrib.ttf"
        ] + font_paths
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_branded_card(base_cropped_1120x560, out_prefix, subtitle_text):
    """
    Renders safe-zone typography and glowing badges onto the 1120x560 2x retina canvas,
    then downsamples with Lanczos to exact 560x280.
    """
    canvas = base_cropped_1120x560.copy().convert("RGBA")
    w, h = canvas.size # 1120, 560

    # Create an overlay layer for subtle atmospheric vignetting around borders to protect text
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Dark gradient scrim on the left/top to make white text pop without obscuring the character
    for x in range(w):
        # subtle dark gradient from left to right (70% opacity at x=0 fading to 0% at x=650)
        if x < 650:
            alpha = int(160 * (1.0 - (x / 650.0)**1.2))
            draw_ov.line([(x, 0), (x, h)], fill=(10, 14, 23, alpha))

    # Dark vignette on the bottom 100px for the footer pill
    for y in range(h - 120, h):
        alpha = int(180 * ((y - (h - 120)) / 120.0)**1.2)
        draw_ov.line([(0, y), (w, y)], fill=(10, 14, 23, alpha))

    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    # Fonts
    font_title = try_load_font(56, bold=True)
    font_badge = try_load_font(18, bold=True)
    font_sub = try_load_font(20, bold=False)
    font_pill = try_load_font(18, bold=True)

    # Safe Zone: All text starts at x=55, well inside the 1120 canvas (safe from rounded corners!)
    x_start = 55
    y_start = 45

    # 1. Google Gemma 4 Badge (Glowing pill)
    badge_text = "GOOGLE GEMMA 4 DEVELOPER AGENT"
    bbox_badge = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox_badge[2] - bbox_badge[0] + 28
    bh = bbox_badge[3] - bbox_badge[1] + 16

    # Draw glassmorphic badge background
    badge_bg = Image.new("RGBA", (bw, bh), (22, 27, 38, 220))
    draw_bg = ImageDraw.Draw(badge_bg)
    draw_bg.rounded_rectangle([0, 0, bw-1, bh-1], radius=14, outline=(161, 66, 244, 220), width=2)
    canvas.paste(badge_bg, (x_start, y_start), badge_bg)
    draw.text((x_start + 14, y_start + 7), badge_text, font=font_badge, fill=(216, 180, 254))

    # 2. Main Title: MR-AST with glowing cyan drop shadow
    y_title = y_start + bh + 14
    # Shadow
    for dx, dy, col in [(-2, -2, (14, 165, 233, 100)), (3, 3, (15, 23, 42, 220)), (0, 0, (56, 189, 248, 150))]:
        draw.text((x_start + dx, y_title + dy), "MR-AST", font=font_title, fill=col)
    # Foreground text
    draw.text((x_start, y_title), "MR-AST", font=font_title, fill=(255, 255, 255))

    # 3. Subtitle
    y_sub = y_title + 68
    draw.text((x_start, y_sub), subtitle_text, font=font_sub, fill=(203, 213, 225))
    draw.text((x_start, y_sub + 28), "Multi-Resolution Context Selection", font=font_sub, fill=(148, 163, 184))

    # 4. Safe Bottom Metrics Pill
    y_pill = h - 68
    pills = [
        ("+16.6 pp Recall", (56, 189, 248)),
        ("1.55x Full Code", (192, 132, 252)),
        ("-28.3% Latency", (52, 211, 153))
    ]
    cur_x = x_start
    for ptext, pcol in pills:
        pbbox = draw.textbbox((0, 0), ptext, font=font_pill)
        pw = pbbox[2] - pbbox[0] + 20
        ph = pbbox[3] - pbbox[1] + 12
        pbg = Image.new("RGBA", (pw, ph), (15, 23, 42, 200))
        pdraw = ImageDraw.Draw(pbg)
        pdraw.rounded_rectangle([0, 0, pw-1, ph-1], radius=8, outline=pcol, width=1)
        canvas.paste(pbg, (cur_x, y_pill), pbg)
        draw.text((cur_x + 10, y_pill + 5), ptext, font=font_pill, fill=(255, 255, 255))
        cur_x += pw + 12

    # Save 1120x560 (2x retina)
    out_retina = f"paper/figures/{out_prefix}_1120x560.png"
    canvas_rgb = canvas.convert("RGB")
    canvas_rgb.save(out_retina, quality=95)
    print(f"Saved {out_retina} (1120x560)")

    # Save exact 560x280 (1x downscaled with Lanczos)
    out_560 = f"paper/figures/{out_prefix}_560x280.png"
    im_560 = canvas_rgb.resize((560, 280), Image.Resampling.LANCZOS)
    im_560.save(out_560, quality=95)
    print(f"Saved {out_560} (560x280)")

def main():
    # 1. Process Mascot (Robot Developer Agent)
    im_mascot = Image.open('paper/figures/art_mascot_wide.jpg')
    mascot_2to1_1120 = crop_to_2_to_1(im_mascot).resize((1120, 560), Image.Resampling.LANCZOS)
    
    # Clean Art (No text overlay)
    mascot_clean_560 = mascot_2to1_1120.resize((560, 280), Image.Resampling.LANCZOS)
    mascot_clean_560.save('paper/figures/kaggle_card_clean_mascot_560x280.png')
    mascot_2to1_1120.save('paper/figures/kaggle_card_clean_mascot_1120x560.png')
    print("Saved clean mascot 560x280 and 1120x560")

    # Branded Art (With safe-zone typography)
    create_branded_card(
        mascot_2to1_1120,
        out_prefix="kaggle_card_mascot",
        subtitle_text="Budget-Constrained Software Engineering Agents"
    )

    # Set as canonical kaggle_card_560x280.png
    shutil.copy('paper/figures/kaggle_card_mascot_560x280.png', 'paper/figures/kaggle_card_560x280.png')
    shutil.copy('paper/figures/kaggle_card_mascot_1120x560.png', 'paper/figures/kaggle_card_1120x560.png')
    print("Updated canonical paper/figures/kaggle_card_560x280.png with Mascot design!")

    # 2. Process Quantum Core (Sci-Fi Hologram Tree)
    im_quantum = Image.open('paper/figures/art_quantum_wide.jpg')
    quantum_2to1_1120 = crop_to_2_to_1(im_quantum).resize((1120, 560), Image.Resampling.LANCZOS)

    quantum_clean_560 = quantum_2to1_1120.resize((560, 280), Image.Resampling.LANCZOS)
    quantum_clean_560.save('paper/figures/kaggle_card_clean_quantum_560x280.png')
    quantum_2to1_1120.save('paper/figures/kaggle_card_clean_quantum_1120x560.png')
    print("Saved clean quantum core 560x280 and 1120x560")

    create_branded_card(
        quantum_2to1_1120,
        out_prefix="kaggle_card_quantum",
        subtitle_text="4-Tier AST Lattice & Knapsack Context Compilation"
    )

    # 3. Square Thumbnails (for avatars, profile & feeds)
    im_mascot_sq = Image.open('paper/figures/art_mascot_square.jpg')
    im_mascot_sq.resize((800, 800), Image.Resampling.LANCZOS).save('paper/figures/thumbnail_mascot_800x800.png')
    im_mascot_sq.resize((560, 560), Image.Resampling.LANCZOS).save('paper/figures/thumbnail_mascot_560x560.png')
    shutil.copy('paper/figures/thumbnail_mascot_800x800.png', 'paper/figures/thumbnail.png')
    print("Saved square thumbnails (800x800, 560x560)")

    # 4. High-Res Widescreen 1920x1080 Banners for Writeup Header
    im_mascot.resize((1920, 1080), Image.Resampling.LANCZOS).save('paper/figures/banner_mascot_1920x1080.png')
    im_quantum.resize((1920, 1080), Image.Resampling.LANCZOS).save('paper/figures/banner_quantum_1920x1080.png')
    shutil.copy('paper/figures/banner_mascot_1920x1080.png', 'paper/figures/banner.png')
    print("Updated canonical paper/figures/banner.png with 1920x1080 Mascot hero banner!")

if __name__ == '__main__':
    main()

