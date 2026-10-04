"""
Generate official Google Play Store graphic assets for CleanSnap:
1. High-res Icon (512x512 PNG)
2. Feature Graphic (1024x500 PNG)
"""
from PIL import Image, ImageDraw, ImageFont
import math

def create_playstore_icon():
    size = (512, 512)
    img = Image.new("RGBA", size, (11, 17, 32, 255)) # Dark slate background #0B1120
    draw = ImageDraw.Draw(img)

    # Draw rounded background rect with subtle border
    draw.rounded_rectangle([16, 16, 496, 496], radius=96, fill=(19, 31, 55, 255), outline=(37, 99, 235, 120), width=4)

    # Shield polygon (center = 256, 256)
    shield_pts = [
        (256, 100),
        (380, 150),
        (380, 290),
        (256, 410),
        (132, 290),
        (132, 150)
    ]
    draw.polygon(shield_pts, fill=(30, 41, 59, 255), outline=(16, 185, 129, 255), width=6)

    # Camera body inside shield
    draw.rounded_rectangle([190, 215, 322, 315], radius=16, fill=(56, 189, 248, 255))
    # Camera top hump
    draw.rounded_rectangle([226, 195, 286, 220], radius=8, fill=(37, 99, 235, 255))
    # Lens outer
    draw.ellipse([216, 225, 296, 305], fill=(15, 23, 42, 255), outline=(248, 250, 252, 200), width=4)
    # Lens inner
    draw.ellipse([236, 245, 276, 285], fill=(16, 185, 129, 255))
    # Sparkle / flare
    draw.ellipse([260, 248, 272, 260], fill=(255, 255, 255, 240))

    img.save("playstore_icon_512.png", "PNG")
    print("Created playstore_icon_512.png (512x512)")

def create_feature_graphic():
    size = (1024, 500)
    img = Image.new("RGBA", size, (11, 17, 32, 255))
    draw = ImageDraw.Draw(img)

    # Gradient subtle lines or backdrop glow
    for y in range(500):
        alpha = int(40 * math.sin(y / 500 * math.pi))
        draw.line([(0, y), (1024, y)], fill=(37, 99, 235, alpha))

    # Decorative card on the right
    draw.rounded_rectangle([620, 70, 940, 430], radius=24, fill=(19, 31, 55, 255), outline=(51, 65, 85, 255), width=2)
    # Mini UI card items
    draw.rounded_rectangle([645, 110, 915, 180], radius=12, fill=(30, 41, 59, 255))
    draw.text((665, 125), "📸 Vacation_Photo.jpg", fill=(248, 250, 252, 255))
    draw.text((665, 150), "✓ GPS & Camera Scrubbed", fill=(16, 185, 129, 255))

    draw.rounded_rectangle([645, 200, 915, 270], radius=12, fill=(30, 41, 59, 255))
    draw.text((665, 215), "🎬 Family_Video.mp4", fill=(248, 250, 252, 255))
    draw.text((665, 240), "✓ Lossless Stream Copy", fill=(56, 189, 248, 255))

    draw.rounded_rectangle([645, 310, 915, 390], radius=16, fill=(37, 99, 235, 255))
    draw.text((710, 338), "✨ 100% Offline & Private", fill=(255, 255, 255, 255))

    # Left branding text
    draw.text((80, 130), "CleanSnap", fill=(248, 250, 252, 255))
    draw.text((80, 180), "EXIF & Privacy Metadata Stripper", fill=(56, 189, 248, 255))
    draw.text((80, 240), "• Permanently remove GPS locations & timestamps", fill=(148, 163, 184, 255))
    draw.text((80, 270), "• 100% Lossless video container cleaning", fill=(148, 163, 184, 255))
    draw.text((80, 300), "• Works with Photos, Videos & Gallery Sharing", fill=(148, 163, 184, 255))
    draw.text((80, 330), "• Zero cloud uploads, zero data collection", fill=(16, 185, 129, 255))

    img.save("playstore_feature_graphic_1024x500.png", "PNG")
    print("Created playstore_feature_graphic_1024x500.png (1024x500)")

if __name__ == "__main__":
    create_playstore_icon()
    create_feature_graphic()
