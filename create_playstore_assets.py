"""
Generate official Google Play Store graphic assets for CleanSnap:
1. High-res Icon (512x512 PNG)
2. Feature Graphic (1024x500 PNG) - Solid background, large crisp typography, no broken glyphs
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

def get_font(font_name: str, size: int):
    path = os.path.join("C:/Windows/Fonts", font_name)
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_checkmark(draw, x, y, size=14, color=(52, 211, 153)):
    # Draw a clean vector checkmark
    draw.line([(x, y + size * 0.5), (x + size * 0.35, y + size * 0.85)], fill=color, width=3)
    draw.line([(x + size * 0.35, y + size * 0.85), (x + size, y + size * 0.15)], fill=color, width=3)

def create_playstore_icon():
    size = (512, 512)
    img = Image.new("RGB", size, (11, 17, 32)) # Solid dark background #0B1120
    draw = ImageDraw.Draw(img)

    # Outer rounded background
    draw.rounded_rectangle([16, 16, 496, 496], radius=96, fill=(19, 31, 55), outline=(37, 99, 235), width=6)

    # Shield polygon
    shield_pts = [
        (256, 90),
        (390, 145),
        (390, 295),
        (256, 420),
        (122, 295),
        (122, 145)
    ]
    draw.polygon(shield_pts, fill=(30, 41, 59), outline=(16, 185, 129), width=7)

    # Camera body inside shield
    draw.rounded_rectangle([185, 210, 327, 315], radius=18, fill=(56, 189, 248))
    # Camera top hump
    draw.rounded_rectangle([225, 188, 287, 215], radius=8, fill=(37, 99, 235))
    # Lens outer
    draw.ellipse([212, 222, 300, 308], fill=(15, 23, 42), outline=(248, 250, 252), width=5)
    # Lens inner
    draw.ellipse([234, 244, 278, 288], fill=(16, 185, 129))
    # Lens flare
    draw.ellipse([260, 248, 274, 262], fill=(255, 255, 255))

    img.save("playstore_icon_512.png", "PNG")
    print("Created playstore_icon_512.png")
    return img

def create_feature_graphic():
    size = (1024, 500)
    # Solid deep dark background
    img = Image.new("RGB", size, (11, 17, 32))
    draw = ImageDraw.Draw(img)

    # Fonts
    font_brand = get_font("segoeuib.ttf", 54)
    font_sub = get_font("segoeuib.ttf", 22)
    font_bullet = get_font("segoeui.ttf", 19)
    font_bullet_bold = get_font("segoeuib.ttf", 19)
    font_card_head = get_font("segoeuib.ttf", 20)
    font_item_title = get_font("segoeuib.ttf", 20)
    font_item_sub = get_font("segoeui.ttf", 16)
    font_tag = get_font("segoeuib.ttf", 14)
    font_btn = get_font("segoeuib.ttf", 22)

    # Sleek dark blue radial lighting
    for y in range(500):
        wave = math.sin(y / 500 * math.pi)
        r = int(11 + 10 * wave)
        g = int(17 + 25 * wave)
        b = int(32 + 65 * wave)
        draw.line([(0, y), (1024, y)], fill=(r, g, b))

    # Add CleanSnap logo icon
    icon = Image.open("playstore_icon_512.png").convert("RGBA")
    icon_mini = icon.resize((74, 74), Image.Resampling.LANCZOS)
    img.paste(icon_mini, (48, 44), icon_mini)

    # Left Section: Typography
    draw.text((136, 46), "CleanSnap", font=font_brand, fill=(248, 250, 252))
    draw.text((50, 134), "EXIF & Privacy Metadata Stripper", font=font_sub, fill=(56, 189, 248))

    # Accent divider line
    draw.line([(50, 172), (500, 172)], fill=(37, 99, 235), width=2)

    bullets = [
        ("Permanently removes GPS coordinates", (226, 232, 240)),
        ("Scrubs camera serials, lens IDs & tags", (203, 213, 225)),
        ("100% Lossless video container cleaning", (203, 213, 225)),
        ("Direct Android Gallery Share integration", (203, 213, 225)),
        ("100% Offline • Zero cloud uploads", (52, 211, 153)),
    ]

    start_y = 196
    for text, color in bullets:
        # Draw clean glowing bullet dot
        draw.ellipse([50, start_y + 4, 60, start_y + 14], fill=(16, 185, 129))
        f = font_bullet_bold if "100%" in text else font_bullet
        draw.text((72, start_y - 2), text, font=f, fill=color)
        start_y += 42

    # Right Section: App Window Mockup
    card_x1, card_y1, card_x2, card_y2 = 540, 36, 980, 464
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=22, fill=(19, 31, 55), outline=(59, 130, 246), width=2)

    # Top header bar inside mockup
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y1 + 54], radius=20, fill=(26, 41, 71))
    draw.text((card_x1 + 24, card_y1 + 16), "Protected Media Queue", font=font_card_head, fill=(241, 245, 249))

    # Badge in mockup header
    draw.rounded_rectangle([card_x2 - 130, card_y1 + 12, card_x2 - 18, card_y1 + 42], radius=8, fill=(6, 78, 59), outline=(5, 150, 105), width=1)
    draw.text((card_x2 - 114, card_y1 + 18), "2 Files Safe", font=font_tag, fill=(52, 211, 153))

    # Item 1: Photo
    it1_y = card_y1 + 72
    draw.rounded_rectangle([card_x1 + 18, it1_y, card_x2 - 18, it1_y + 84], radius=14, fill=(30, 41, 59), outline=(51, 65, 85), width=1)
    # JPG badge
    draw.rounded_rectangle([card_x1 + 30, it1_y + 15, card_x1 + 86, it1_y + 69], radius=10, fill=(37, 99, 235))
    draw.text((card_x1 + 42, it1_y + 26), "JPG", font=font_tag, fill=(255, 255, 255))
    draw.text((card_x1 + 102, it1_y + 16), "Vacation_Photo.jpg", font=font_item_title, fill=(248, 250, 252))
    # Vector checkmark
    draw_checkmark(draw, card_x1 + 102, it1_y + 48, size=15, color=(52, 211, 153))
    draw.text((card_x1 + 124, it1_y + 47), "GPS & Camera Scrubbed", font=font_item_sub, fill=(52, 211, 153))

    # Item 2: Video
    it2_y = it1_y + 98
    draw.rounded_rectangle([card_x1 + 18, it2_y, card_x2 - 18, it2_y + 84], radius=14, fill=(30, 41, 59), outline=(51, 65, 85), width=1)
    # MP4 badge
    draw.rounded_rectangle([card_x1 + 30, it2_y + 15, card_x1 + 86, it2_y + 69], radius=10, fill=(16, 185, 129))
    draw.text((card_x1 + 40, it2_y + 26), "MP4", font=font_tag, fill=(255, 255, 255))
    draw.text((card_x1 + 102, it2_y + 16), "Family_Video.mp4", font=font_item_title, fill=(248, 250, 252))
    # Vector checkmark
    draw_checkmark(draw, card_x1 + 102, it2_y + 48, size=15, color=(56, 189, 248))
    draw.text((card_x1 + 124, it2_y + 47), "Lossless Stream Copy", font=font_item_sub, fill=(56, 189, 248))

    # Action Button
    btn_y = it2_y + 104
    draw.rounded_rectangle([card_x1 + 18, btn_y, card_x2 - 18, btn_y + 64], radius=16, fill=(37, 99, 235))
    btn_text = "Clean & Protect All Files"
    draw.text((card_x1 + 86, btn_y + 17), btn_text, font=font_btn, fill=(255, 255, 255))

    img.save("playstore_feature_graphic_1024x500.png", "PNG")
    print("Created crystal clear playstore_feature_graphic_1024x500.png (1024x500)")

if __name__ == "__main__":
    create_playstore_icon()
    create_feature_graphic()
