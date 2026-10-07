import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

# EXACT DIMENSIONS FOR OFFICE DEPOT / OFFICE MAX
# 3.625" x 2.125" at 300 DPI = 1088 x 638 pixels
WIDTH = 1088
HEIGHT = 638

# Color Palette - Luxury Dark
DARK_BG = (10, 16, 23)          # #0a1017 deep slate
DARK_ACCENT = (14, 34, 24)      # forest dark
GREEN_PRIMARY = (21, 128, 61)   # #15803d
GREEN_BRIGHT = (34, 197, 94)    # #22c55e
GREEN_LIGHT = (74, 222, 128)    # #4ade80
GOLD = (245, 158, 11)           # #f59e0b
GOLD_LIGHT = (252, 211, 77)     # #fcd34d
WHITE = (255, 255, 255)
GRAY_100 = (243, 244, 246)
GRAY_300 = (209, 213, 219)
GRAY_400 = (156, 163, 175)
DARK_CARD = (17, 24, 39)        # #111827
DARK_CARD_BORDER = (55, 65, 81)

# Fonts
font_title = ImageFont.truetype("segoeuib.ttf", 36)
font_subtitle = ImageFont.truetype("segoeuib.ttf", 13)
font_h2 = ImageFont.truetype("segoeuib.ttf", 25)
font_body_bold = ImageFont.truetype("segoeuib.ttf", 18)
font_body = ImageFont.truetype("segoeui.ttf", 15)
font_small_bold = ImageFont.truetype("segoeuib.ttf", 13)
font_small = ImageFont.truetype("segoeui.ttf", 12)
font_tiny_bold = ImageFont.truetype("segoeuib.ttf", 11)

# QR Code setup: WhatsApp direct
qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=1&format=png&data=https%3A%2F%2Fwa.me%2F12546121399"
qr_path = "qr_wa.png"
if not os.path.exists(qr_path):
    try:
        urllib.request.urlretrieve(qr_url, qr_path)
    except Exception as e:
        print("QR download note:", e)

# Helper: draw gradient background
def create_background(dark=True):
    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG if dark else (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    if dark:
        # Subtle horizontal gradient
        for x in range(WIDTH):
            ratio = x / WIDTH
            r = int(DARK_BG[0] * (1 - ratio) + DARK_ACCENT[0] * ratio)
            g = int(DARK_BG[1] * (1 - ratio) + DARK_ACCENT[1] * ratio)
            b = int(DARK_BG[2] * (1 - ratio) + DARK_ACCENT[2] * ratio)
            draw.line([(x, 0), (x, HEIGHT)], fill=(r, g, b))
            
        # Luxury diagonal geometric stripe
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        o_draw = ImageDraw.Draw(overlay)
        o_draw.polygon([
            (WIDTH - 320, 0),
            (WIDTH, 0),
            (WIDTH, HEIGHT),
            (WIDTH - 140, HEIGHT)
        ], fill=(21, 128, 61, 45))
        o_draw.line([(WIDTH - 320, 0), (WIDTH - 140, HEIGHT)], fill=(34, 197, 94, 220), width=3)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    else:
        # Clean white subtle gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            c = int(255 * (1 - ratio) + 245 * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(c, c, c))
            
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        o_draw = ImageDraw.Draw(overlay)
        o_draw.polygon([
            (WIDTH - 300, 0),
            (WIDTH, 0),
            (WIDTH, HEIGHT),
            (WIDTH - 120, HEIGHT)
        ], fill=(21, 128, 61, 20))
        o_draw.line([(WIDTH - 300, 0), (WIDTH - 120, HEIGHT)], fill=(21, 128, 61, 180), width=3)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img

# Helper: Draw vector leaf emblem
def draw_leaf_icon(draw, cx, cy, size=24, dark=True):
    draw.ellipse([cx - size, cy - size, cx + size, cy + size], fill=(21, 128, 61, 200))
    points = [
        (cx, cy - size + 4),
        (cx + size - 4, cy - 2),
        (cx + size - 6, cy + size - 6),
        (cx, cy + size - 4),
        (cx - size + 6, cy + size - 6),
        (cx - size + 4, cy - 2)
    ]
    draw.polygon(points, fill=GREEN_BRIGHT if dark else (21, 128, 61))
    draw.line([(cx, cy - size + 6), (cx, cy + size - 6)], fill=WHITE, width=2)

# Helper: Draw vector checkmark
def draw_vector_checkmark(draw, x, y, size=22, box_color=GREEN_PRIMARY, check_color=WHITE):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=5, fill=box_color)
    draw.line([(x + 5, y + 11), (x + 9, y + 16)], fill=check_color, width=2)
    draw.line([(x + 9, y + 16), (x + 17, y + 6)], fill=check_color, width=2)

# Helper: Draw vector phone handset icon
def draw_phone_icon(draw, x, y, bg_color=GREEN_PRIMARY):
    draw.rounded_rectangle([x, y, x + 28, y + 28], radius=6, fill=bg_color)
    # White handset curve
    draw.ellipse([x + 8, y + 6, x + 20, y + 22], outline=WHITE, width=2)
    draw.rectangle([x + 13, y + 9, x + 22, y + 19], fill=bg_color)
    draw.ellipse([x + 7, y + 5, x + 12, y + 11], fill=WHITE)
    draw.ellipse([x + 16, y + 17, x + 21, y + 23], fill=WHITE)

# Helper: Draw vector star icon
def draw_star_icon(draw, x, y, bg_color=GOLD):
    draw.rounded_rectangle([x, y, x + 28, y + 28], radius=6, fill=bg_color)
    cx = x + 14
    cy = y + 14
    draw.polygon([
        (cx, cy - 8), (cx + 2, cy - 2), (cx + 8, cy - 2),
        (cx + 3, cy + 2), (cx + 5, cy + 8), (cx, cy + 4),
        (cx - 5, cy + 8), (cx - 3, cy + 2), (cx - 8, cy - 2),
        (cx - 2, cy - 2)
    ], fill=WHITE)

# Helper: Draw vector email envelope icon
def draw_mail_icon(draw, x, y, bg_color=(30, 41, 59)):
    draw.rounded_rectangle([x, y, x + 28, y + 28], radius=6, fill=bg_color)
    draw.rectangle([x + 6, y + 8, x + 22, y + 20], outline=WHITE, width=2)
    draw.line([(x + 6, y + 8), (x + 14, y + 14)], fill=WHITE, width=2)
    draw.line([(x + 22, y + 8), (x + 14, y + 14)], fill=WHITE, width=2)


# ========================================================
# 1. LUXURY DARK - FRONT CARD
# ========================================================
def generate_dark_front(output_filename="Rodriguez_LawnCare_Card_FRONT.png"):
    img = create_background(dark=True)
    draw = ImageDraw.Draw(img)
    
    safe_left = 68
    safe_top = 58
    safe_right = WIDTH - 68
    safe_bottom = HEIGHT - 58
    
    # 1. Logo Leaf Badge
    draw_leaf_icon(draw, safe_left + 24, safe_top + 26, size=24, dark=True)
    
    # 2. Brand Name
    text_x = safe_left + 64
    draw.text((text_x, safe_top + 4), "RODRIGUEZ", fill=WHITE, font=font_title)
    bbox = draw.textbbox((text_x, safe_top + 4), "RODRIGUEZ ", font=font_title)
    draw.text((bbox[2], safe_top + 4), "LAWNCARE", fill=GREEN_BRIGHT, font=font_title)
    
    # 3. Tagline
    draw.text((text_x + 2, safe_top + 50), "LANDSCAPING & GROUNDS MAINTENANCE", fill=GOLD, font=font_subtitle)
    
    # Insured Badge on Top Right
    badge_w = 205
    badge_h = 32
    badge_x = safe_right - badge_w
    badge_y = safe_top + 10
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=16, fill=(30, 41, 59), outline=GOLD, width=1)
    draw.text((badge_x + 18, badge_y + 8), "COMMERCIALLY INSURED", fill=GOLD_LIGHT, font=font_tiny_bold)
    
    # Divider line
    draw.line([(safe_left, safe_top + 80), (safe_right - 230, safe_top + 80)], fill=(55, 65, 81), width=2)
    
    # Subheading
    draw.text((safe_left, safe_top + 98), "Residential & Commercial Lawn Maintenance", fill=WHITE, font=font_body_bold)
    
    # Contacts
    items_y = safe_top + 146
    line_gap = 48
    
    # 1. Direct & WhatsApp
    draw_phone_icon(draw, safe_left, items_y, bg_color=GREEN_PRIMARY)
    draw.text((safe_left + 38, items_y - 2), "Direct Call & WhatsApp:", fill=GREEN_LIGHT, font=font_small_bold)
    draw.text((safe_left + 38, items_y + 16), "(254) 612-1399", fill=WHITE, font=font_body_bold)
    
    # 2. 24/7 AI Line
    y2 = items_y + line_gap
    draw_star_icon(draw, safe_left, y2, bg_color=GOLD)
    draw.text((safe_left + 38, y2 - 2), "24/7 AI Booking & Estimate Line:", fill=GOLD_LIGHT, font=font_small_bold)
    draw.text((safe_left + 38, y2 + 16), "(254) 852-8163", fill=WHITE, font=font_body_bold)
    
    # 3. Email
    y3 = y2 + line_gap
    draw_mail_icon(draw, safe_left, y3, bg_color=(30, 41, 59))
    draw.text((safe_left + 38, y3 - 2), "Email Inquiries:", fill=GRAY_400, font=font_small_bold)
    draw.text((safe_left + 38, y3 + 16), "arizmendir754@gmail.com", fill=WHITE, font=font_body_bold)
    
    # Bottom Service Area Banner
    banner_y = safe_bottom - 46
    draw.rounded_rectangle([safe_left, banner_y, safe_right - 230, banner_y + 40], radius=8, fill=(15, 33, 24), outline=GREEN_PRIMARY, width=1)
    draw.text((safe_left + 16, banner_y + 11), "Serving: Killeen • Harker Heights • Copperas Cove • Belton", fill=GREEN_LIGHT, font=font_small_bold)
    
    # QR Code Card Container (Right Side)
    qr_w = 175
    qr_h = 175
    card_x = safe_right - qr_w
    card_y = safe_top + 95
    
    draw.rounded_rectangle([card_x - 14, card_y - 12, card_x + qr_w + 14, card_y + qr_h + 60], radius=14, fill=WHITE)
    
    if os.path.exists(qr_path):
        qr = Image.open(qr_path).convert("RGBA")
        qr = qr.resize((qr_w, qr_h), Image.Resampling.LANCZOS)
        img.paste(qr, (card_x, card_y), qr)
        
    draw.text((card_x + 18, card_y + qr_h + 8), "SCAN TO CHAT", fill=(15, 23, 42), font=font_small_bold)
    draw.text((card_x + 16, card_y + qr_h + 28), "Free Instant Quote", fill=GREEN_PRIMARY, font=font_tiny_bold)
    
    img.save(output_filename, dpi=(300, 300), format="PNG")
    print(f"Generated: {output_filename}")


# ========================================================
# 2. LUXURY DARK - BACK CARD
# ========================================================
def generate_dark_back(output_filename="Rodriguez_LawnCare_Card_BACK.png"):
    img = create_background(dark=True)
    draw = ImageDraw.Draw(img)
    
    safe_left = 68
    safe_top = 58
    safe_right = WIDTH - 68
    safe_bottom = HEIGHT - 58
    
    # Header
    draw.text((safe_left, safe_top + 4), "OUR PROFESSIONAL SERVICES", fill=WHITE, font=font_h2)
    draw.text((safe_left, safe_top + 38), "HIGH-PRECISION GROUNDS MAINTENANCE • LICENSED & INSURED", fill=GREEN_LIGHT, font=font_small_bold)
    
    draw.line([(safe_left, safe_top + 62), (safe_right, safe_top + 62)], fill=(55, 65, 81), width=2)
    
    col1 = [
        "Commercial Lawn Mowing & Striping",
        "Razor-Sharp Perimeter Edging",
        "Shrub, Bush & Hedge Trimming",
        "Tree Trimming, Cutting & Planting"
    ]
    col2 = [
        "Mulch Installation & Flower Beds",
        "Leaf Cleanups & Debris Clearing",
        "Yard Clearing & Junk Hauling",
        "Full Seasonal Yard Restorations"
    ]
    
    list_y = safe_top + 88
    row_gap = 42
    
    for i, srv in enumerate(col1):
        cy = list_y + (i * row_gap)
        draw_vector_checkmark(draw, safe_left, cy, size=22, box_color=GREEN_PRIMARY, check_color=WHITE)
        draw.text((safe_left + 36, cy + 1), srv, fill=WHITE, font=font_body_bold)
        
    col2_x = safe_left + 480
    for i, srv in enumerate(col2):
        cy = list_y + (i * row_gap)
        draw_vector_checkmark(draw, col2_x, cy, size=22, box_color=GREEN_PRIMARY, check_color=WHITE)
        draw.text((col2_x + 36, cy + 1), srv, fill=WHITE, font=font_body_bold)
        
    banner_y = safe_bottom - 86
    banner_h = 80
    draw.rounded_rectangle([safe_left, banner_y, safe_right, banner_y + banner_h], radius=12, fill=(17, 24, 39), outline=(55, 65, 81), width=1)
    
    draw.text((safe_left + 20, banner_y + 14), "100% SATISFACTION GUARANTEED", fill=GOLD, font=font_body_bold)
    draw.text((safe_left + 20, banner_y + 42), "Daily Sharpened Blades • Punctual Schedule • Direct Work & Contractor Jobs", fill=GRAY_400, font=font_small)
    
    draw.text((safe_right - 265, banner_y + 14), "ACCEPTED PAYMENTS:", fill=GREEN_LIGHT, font=font_small_bold)
    draw.text((safe_right - 265, banner_y + 40), "Zelle • Venmo • Cash App • PayPal • Cash", fill=WHITE, font=font_small_bold)
    
    img.save(output_filename, dpi=(300, 300), format="PNG")
    print(f"Generated: {output_filename}")


# ========================================================
# 3. CLEAN WHITE - FRONT CARD
# ========================================================
def generate_light_front(output_filename="Rodriguez_LawnCare_Card_FRONT_CleanWhite.png"):
    img = create_background(dark=False)
    draw = ImageDraw.Draw(img)
    
    safe_left = 68
    safe_top = 58
    safe_right = WIDTH - 68
    safe_bottom = HEIGHT - 58
    
    draw_leaf_icon(draw, safe_left + 24, safe_top + 26, size=24, dark=False)
    
    text_x = safe_left + 64
    draw.text((text_x, safe_top + 4), "RODRIGUEZ", fill=(15, 23, 42), font=font_title)
    bbox = draw.textbbox((text_x, safe_top + 4), "RODRIGUEZ ", font=font_title)
    draw.text((bbox[2], safe_top + 4), "LAWNCARE", fill=GREEN_PRIMARY, font=font_title)
    
    draw.text((text_x + 2, safe_top + 50), "LANDSCAPING & GROUNDS MAINTENANCE", fill=(180, 83, 9), font=font_subtitle)
    
    badge_w = 205
    badge_h = 32
    badge_x = safe_right - badge_w
    badge_y = safe_top + 10
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=16, fill=(254, 243, 199), outline=(217, 119, 6), width=1)
    draw.text((badge_x + 18, badge_y + 8), "COMMERCIALLY INSURED", fill=(180, 83, 9), font=font_tiny_bold)
    
    draw.line([(safe_left, safe_top + 80), (safe_right - 230, safe_top + 80)], fill=(209, 213, 219), width=2)
    
    draw.text((safe_left, safe_top + 98), "Residential & Commercial Lawn Maintenance", fill=(15, 23, 42), font=font_body_bold)
    
    items_y = safe_top + 146
    line_gap = 48
    
    draw_phone_icon(draw, safe_left, items_y, bg_color=GREEN_PRIMARY)
    draw.text((safe_left + 38, items_y - 2), "Direct Call & WhatsApp:", fill=GREEN_PRIMARY, font=font_small_bold)
    draw.text((safe_left + 38, items_y + 16), "(254) 612-1399", fill=(15, 23, 42), font=font_body_bold)
    
    y2 = items_y + line_gap
    draw_star_icon(draw, safe_left, y2, bg_color=(217, 119, 6))
    draw.text((safe_left + 38, y2 - 2), "24/7 AI Booking & Estimate Line:", fill=(180, 83, 9), font=font_small_bold)
    draw.text((safe_left + 38, y2 + 16), "(254) 852-8163", fill=(15, 23, 42), font=font_body_bold)
    
    y3 = y2 + line_gap
    draw_mail_icon(draw, safe_left, y3, bg_color=(75, 85, 99))
    draw.text((safe_left + 38, y3 - 2), "Email Inquiries:", fill=(75, 85, 99), font=font_small_bold)
    draw.text((safe_left + 38, y3 + 16), "arizmendir754@gmail.com", fill=(15, 23, 42), font=font_body_bold)
    
    banner_y = safe_bottom - 46
    draw.rounded_rectangle([safe_left, banner_y, safe_right - 230, banner_y + 40], radius=8, fill=(236, 253, 245), outline=GREEN_PRIMARY, width=1)
    draw.text((safe_left + 16, banner_y + 11), "Serving: Killeen • Harker Heights • Copperas Cove • Belton", fill=GREEN_PRIMARY, font=font_small_bold)
    
    qr_w = 175
    qr_h = 175
    card_x = safe_right - qr_w
    card_y = safe_top + 95
    
    draw.rounded_rectangle([card_x - 14, card_y - 12, card_x + qr_w + 14, card_y + qr_h + 60], radius=14, fill=WHITE, outline=(229, 231, 235), width=2)
    
    if os.path.exists(qr_path):
        qr = Image.open(qr_path).convert("RGBA")
        qr = qr.resize((qr_w, qr_h), Image.Resampling.LANCZOS)
        img.paste(qr, (card_x, card_y), qr)
        
    draw.text((card_x + 18, card_y + qr_h + 8), "SCAN TO CHAT", fill=(15, 23, 42), font=font_small_bold)
    draw.text((card_x + 16, card_y + qr_h + 28), "Free Instant Quote", fill=GREEN_PRIMARY, font=font_tiny_bold)
    
    img.save(output_filename, dpi=(300, 300), format="PNG")
    print(f"Generated: {output_filename}")


# ========================================================
# 4. CLEAN WHITE - BACK CARD
# ========================================================
def generate_light_back(output_filename="Rodriguez_LawnCare_Card_BACK_CleanWhite.png"):
    img = create_background(dark=False)
    draw = ImageDraw.Draw(img)
    
    safe_left = 68
    safe_top = 58
    safe_right = WIDTH - 68
    safe_bottom = HEIGHT - 58
    
    draw.text((safe_left, safe_top + 4), "OUR PROFESSIONAL SERVICES", fill=(15, 23, 42), font=font_h2)
    draw.text((safe_left, safe_top + 38), "HIGH-PRECISION GROUNDS MAINTENANCE • LICENSED & INSURED", fill=GREEN_PRIMARY, font=font_small_bold)
    
    draw.line([(safe_left, safe_top + 62), (safe_right, safe_top + 62)], fill=(209, 213, 219), width=2)
    
    col1 = [
        "Commercial Lawn Mowing & Striping",
        "Razor-Sharp Perimeter Edging",
        "Shrub, Bush & Hedge Trimming",
        "Tree Trimming, Cutting & Planting"
    ]
    col2 = [
        "Mulch Installation & Flower Beds",
        "Leaf Cleanups & Debris Clearing",
        "Yard Clearing & Junk Hauling",
        "Full Seasonal Yard Restorations"
    ]
    
    list_y = safe_top + 88
    row_gap = 42
    
    for i, srv in enumerate(col1):
        cy = list_y + (i * row_gap)
        draw_vector_checkmark(draw, safe_left, cy, size=22, box_color=GREEN_PRIMARY, check_color=WHITE)
        draw.text((safe_left + 36, cy + 1), srv, fill=(15, 23, 42), font=font_body_bold)
        
    col2_x = safe_left + 480
    for i, srv in enumerate(col2):
        cy = list_y + (i * row_gap)
        draw_vector_checkmark(draw, col2_x, cy, size=22, box_color=GREEN_PRIMARY, check_color=WHITE)
        draw.text((col2_x + 36, cy + 1), srv, fill=(15, 23, 42), font=font_body_bold)
        
    banner_y = safe_bottom - 86
    banner_h = 80
    draw.rounded_rectangle([safe_left, banner_y, safe_right, banner_y + banner_h], radius=12, fill=(241, 245, 249), outline=(203, 213, 225), width=1)
    
    draw.text((safe_left + 20, banner_y + 14), "100% SATISFACTION GUARANTEED", fill=(180, 83, 9), font=font_body_bold)
    draw.text((safe_left + 20, banner_y + 42), "Daily Sharpened Blades • Punctual Schedule • Direct Work & Contractor Jobs", fill=(71, 85, 105), font=font_small)
    
    draw.text((safe_right - 265, banner_y + 14), "ACCEPTED PAYMENTS:", fill=GREEN_PRIMARY, font=font_small_bold)
    draw.text((safe_right - 265, banner_y + 40), "Zelle • Venmo • Cash App • PayPal • Cash", fill=(15, 23, 42), font=font_small_bold)
    
    img.save(output_filename, dpi=(300, 300), format="PNG")
    print(f"Generated: {output_filename}")


if __name__ == "__main__":
    generate_dark_front("Rodriguez_LawnCare_Card_FRONT.png")
    generate_dark_back("Rodriguez_LawnCare_Card_BACK.png")
    generate_light_front("Rodriguez_LawnCare_Card_FRONT_CleanWhite.png")
    generate_light_back("Rodriguez_LawnCare_Card_BACK_CleanWhite.png")
    print("ALL 4 IMAGE FILES READY FOR OFFICE MAX / OFFICE DEPOT!")
