import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

# EXACT OFFICE MAX / OFFICE DEPOT SPECS
# 3.625" x 2.125" at 300 DPI = 1088 x 638 pixels (Landscape)
WIDTH = 1088
HEIGHT = 638

# Color Palette matching user's reference card
COLOR_BLACK = (6, 8, 10)         # deep midnight black
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (34, 197, 94)       # #22c55e vibrant fresh lawn green
COLOR_DARK_GREEN = (21, 128, 61)  # #15803d
COLOR_LIME = (74, 222, 128)       # #4ade80 light green
COLOR_GOLD = (245, 158, 11)       # #f59e0b
COLOR_GRAY_LIGHT = (229, 231, 235)
COLOR_GRAY_MUTED = (156, 163, 175)
COLOR_GRAY_DARK = (45, 52, 60)

# Fonts
font_brand = ImageFont.truetype("segoeuib.ttf", 44)
font_brand_sub = ImageFont.truetype("segoeuib.ttf", 15)
font_name = ImageFont.truetype("segoeuib.ttf", 25)
font_role = ImageFont.truetype("segoeuib.ttf", 13)
font_h2 = ImageFont.truetype("segoeuib.ttf", 28)
font_body_bold = ImageFont.truetype("segoeuib.ttf", 18)
font_body = ImageFont.truetype("segoeui.ttf", 15)
font_label = ImageFont.truetype("segoeuib.ttf", 12)
font_small_bold = ImageFont.truetype("segoeuib.ttf", 13)
font_small = ImageFont.truetype("segoeui.ttf", 13)
font_tiny_bold = ImageFont.truetype("segoeuib.ttf", 11)

# LUSH NATURAL GRASS BORDER ALONG BOTTOM
def draw_lush_grass_border(img, y_base=638, max_h=85):
    draw = ImageDraw.Draw(img)
    random.seed(777)
    
    grass_shades = [
        (10, 60, 32),
        (16, 95, 48),
        (21, 128, 61),
        (34, 197, 94),
        (22, 163, 74),
        (74, 222, 128),
        (134, 239, 172)
    ]
    
    # 5 rich overlapping layers of grass
    for layer in range(5):
        h_mult = 0.5 + (layer * 0.13)
        step = 2
        for x in range(-5, WIDTH + 10, step):
            blade_h = int(random.uniform(max_h * 0.5, max_h) * h_mult)
            curve = random.uniform(-15, 15)
            tip_x = x + curve
            tip_y = y_base - blade_h
            
            color_idx = min(len(grass_shades) - 1, layer + random.randint(0, 2))
            col = grass_shades[color_idx]
            
            base_w = random.uniform(2.5, 4.5)
            draw.polygon([
                (x - base_w, y_base),
                (tip_x, tip_y),
                (x + base_w, y_base)
            ], fill=col)
            
    # Solid dark green base strip to ensure zero gap at edge
    for y in range(y_base - 14, y_base):
        draw.line([(0, y), (WIDTH, y)], fill=(10, 50, 26))

# COMMERCIAL LAWN MOWER DETAILED VECTOR
def draw_lawnmower(draw, cx, cy, scale=1.0, is_watermark=False):
    s = scale
    
    if is_watermark:
        w_col = (100, 115, 130)
        g_col = (40, 110, 65)
        d_col = (30, 35, 40)
        t_col = (25, 30, 35)
    else:
        w_col = COLOR_WHITE
        g_col = COLOR_GREEN
        d_col = (35, 38, 42)
        t_col = (20, 22, 25)
    
    # Rear Wheel (Large)
    rw_r = int(25 * s)
    rw_x = cx - int(45 * s)
    rw_y = cy + int(14 * s)
    
    draw.ellipse([rw_x - rw_r, rw_y - rw_r, rw_x + rw_r, rw_y + rw_r], fill=t_col, outline=w_col, width=max(2, int(3*s)))
    rim_r = int(17 * s)
    draw.ellipse([rw_x - rim_r, rw_y - rim_r, rw_x + rim_r, rw_y + rim_r], fill=d_col, outline=g_col, width=max(1, int(2*s)))
    draw.ellipse([rw_x - int(7*s), rw_y - int(7*s), rw_x + int(7*s), rw_y + int(7*s)], fill=g_col, outline=w_col, width=1)
    for angle in [0, 45, 90, 135]:
        rad = math.radians(angle)
        dx = int(math.cos(rad) * (rim_r - 2))
        dy = int(math.sin(rad) * (rim_r - 2))
        draw.line([(rw_x - dx, rw_y - dy), (rw_x + dx, rw_y + dy)], fill=w_col, width=max(1, int(2*s)))
        
    # Front Wheel (Smaller)
    fw_r = int(16 * s)
    fw_x = cx + int(48 * s)
    fw_y = cy + int(22 * s)
    
    draw.ellipse([fw_x - fw_r, fw_y - fw_r, fw_x + fw_r, fw_y + fw_r], fill=t_col, outline=w_col, width=max(2, int(3*s)))
    f_rim = int(11 * s)
    draw.ellipse([fw_x - f_rim, fw_y - f_rim, fw_x + f_rim, fw_y + f_rim], fill=d_col, outline=g_col, width=max(1, int(2*s)))
    draw.ellipse([fw_x - int(5*s), fw_y - int(5*s), fw_x + int(5*s), fw_y + int(5*s)], fill=g_col, outline=w_col, width=1)
    for angle in [0, 90]:
        rad = math.radians(angle)
        dx = int(math.cos(rad) * (f_rim - 2))
        dy = int(math.sin(rad) * (f_rim - 2))
        draw.line([(fw_x - dx, fw_y - dy), (fw_x + dx, fw_y + dy)], fill=w_col, width=max(1, int(2*s)))

    # Grass Catcher Bag (Rear)
    bag = [
        (rw_x - int(6 * s), cy + int(6 * s)),
        (cx - int(72 * s), cy - int(12 * s)),
        (cx - int(82 * s), cy + int(8 * s)),
        (cx - int(48 * s), cy + int(24 * s)),
        (rw_x, cy + int(22 * s))
    ]
    draw.polygon(bag, fill=(28, 30, 34) if not is_watermark else (20, 24, 28), outline=w_col)
    draw.line(bag + [bag[0]], fill=w_col, width=max(1, int(2*s)))
    draw.line([(cx - int(68 * s), cy - int(6 * s)), (cx - int(52 * s), cy + int(18 * s))], fill=d_col, width=max(1, int(2*s)))

    # Cutting Deck (Main Body)
    deck = [
        (rw_x, cy + int(8 * s)),
        (rw_x + int(12 * s), cy - int(12 * s)),
        (cx - int(10 * s), cy - int(16 * s)),
        (cx + int(36 * s), cy - int(16 * s)),
        (fw_x + int(10 * s), cy + int(14 * s)),
        (fw_x - int(14 * s), cy + int(24 * s)),
        (cx, cy + int(24 * s)),
        (rw_x, cy + int(22 * s))
    ]
    draw.polygon(deck, fill=g_col, outline=w_col)
    draw.line(deck + [deck[0]], fill=w_col, width=max(2, int(3*s)))
    draw.line([(rw_x + int(10 * s), cy + int(20 * s)), (fw_x, cy + int(22 * s))], fill=(220, 220, 220) if not is_watermark else (80, 90, 100), width=max(2, int(3*s)))

    # Engine Shroud
    eng = [
        (cx - int(24 * s), cy - int(16 * s)),
        (cx - int(20 * s), cy - int(42 * s)),
        (cx + int(15 * s), cy - int(42 * s)),
        (cx + int(24 * s), cy - int(16 * s))
    ]
    draw.polygon(eng, fill=(245, 245, 245) if not is_watermark else (70, 80, 90), outline=w_col)
    draw.line(eng + [eng[0]], fill=w_col, width=max(2, int(3*s)))
    
    # Grill & pull cord cap
    draw.rounded_rectangle([cx - int(15 * s), cy - int(34 * s), cx + int(15 * s), cy - int(22 * s)], radius=int(3*s), fill=d_col, outline=g_col, width=max(1, int(2*s)))
    draw.rounded_rectangle([cx - int(11 * s), cy - int(48 * s), cx + int(8 * s), cy - int(42 * s)], radius=int(2*s), fill=w_col)

    # Handle Bar
    h_base_x = rw_x + int(8 * s)
    h_base_y = cy - int(8 * s)
    h_mid_x = cx - int(72 * s)
    h_mid_y = cy - int(54 * s)
    h_top_x = cx - int(112 * s)
    h_top_y = cy - int(92 * s)

    draw.line([(h_base_x, h_base_y), (h_mid_x, h_mid_y)], fill=w_col, width=max(2, int(4*s)))
    draw.ellipse([h_mid_x - int(5*s), h_mid_y - int(5*s), h_mid_x + int(5*s), h_mid_y + int(5*s)], fill=g_col, outline=w_col, width=1)
    draw.line([(h_mid_x, h_mid_y), (h_top_x, h_top_y)], fill=w_col, width=max(2, int(4*s)))
    draw.line([(h_top_x - int(6*s), h_top_y - int(6*s)), (h_top_x + int(6*s), h_top_y + int(6*s))], fill=g_col, width=max(4, int(7*s)))
    draw.line([(h_mid_x - int(10*s), h_mid_y - int(15*s)), (h_top_x - int(4*s), h_top_y - int(2*s))], fill=(200, 200, 200) if not is_watermark else (70, 80, 90), width=max(1, int(2*s)))

    # Flying grass clippings
    if not is_watermark:
        random.seed(999)
        for _ in range(14):
            gx = cx + int(random.uniform(15, 65) * s)
            gy = cy + int(random.uniform(18, 40) * s)
            gw = int(random.uniform(5, 12) * s)
            gh = int(random.uniform(2, 5) * s)
            draw.line([(gx, gy), (gx + gw, gy - gh)], fill=g_col, width=max(1, int(2*s)))


# =========================================================================
# 1. FRONT OF BUSINESS CARD (Exact Match to User Reference Photo)
# =========================================================================
def create_front_card(filename="Rodriguez_LawnCare_Card_FRONT.png"):
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BLACK)
    draw = ImageDraw.Draw(img)
    
    # Safe bounds: 65px from edges
    safe_left = 65
    safe_top = 55
    safe_right = WIDTH - 65
    
    # ---------------- LEFT SIDE: LOGO & BRAND ----------------
    mower_cx = 240
    mower_cy = 185
    draw_lawnmower(draw, mower_cx, mower_cy, scale=1.55)
    
    # "RODRIGUEZ"
    title_text = "RODRIGUEZ"
    bbox = draw.textbbox((0, 0), title_text, font=font_brand)
    w_title = bbox[2] - bbox[0]
    draw.text((mower_cx - (w_title // 2), 268), title_text, fill=COLOR_WHITE, font=font_brand)
    
    # "LAWN CARE & LANDSCAPING"
    sub_text = "LAWN CARE & LANDSCAPING"
    bbox_sub = draw.textbbox((0, 0), sub_text, font=font_brand_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    sub_x = mower_cx - (w_sub // 2)
    sub_y = 324
    
    # Green accent lines on left and right of subtitle
    draw.line([(sub_x - 30, sub_y + 10), (sub_x - 10, sub_y + 10)], fill=COLOR_GREEN, width=2)
    draw.text((sub_x, sub_y), sub_text, fill=COLOR_GREEN, font=font_brand_sub)
    draw.line([(sub_x + w_sub + 10, sub_y + 10), (sub_x + w_sub + 30, sub_y + 10)], fill=COLOR_GREEN, width=2)
    
    # Sub-tagline
    tag_text = "Commercial & Residential Services"
    bbox_tag = draw.textbbox((0, 0), tag_text, font=font_small)
    w_tag = bbox_tag[2] - bbox_tag[0]
    draw.text((mower_cx - (w_tag // 2), 356), tag_text, fill=COLOR_GRAY_MUTED, font=font_small)

    # ---------------- VERTICAL DIVIDER ----------------
    div_x = 470
    draw.line([(div_x, 80), (div_x, 490)], fill=COLOR_GRAY_DARK, width=2)
    draw.line([(div_x, 230), (div_x, 340)], fill=COLOR_GREEN, width=2) # green center highlight

    # ---------------- RIGHT SIDE: CONTACT INFO & IA NUMBER ----------------
    r_x = 515
    y = safe_top + 15
    
    # Name & Role with arrow (Exactly like reference: "► Franklin Robert")
    draw.text((r_x, y), "►  Rafael Rodriguez", fill=COLOR_GREEN, font=font_name)
    draw.text((r_x + 28, y + 36), "OWNER / OPERATOR", fill=COLOR_GRAY_MUTED, font=font_role)
    
    # Thin green horizontal line under name
    draw.line([(r_x, y + 62), (safe_right - 30, y + 62)], fill=COLOR_GREEN, width=2)
    
    # Contact items with spacing
    y_contact = y + 80
    
    # 1. PERSONAL / DIRECT NUMBER
    draw.text((r_x, y_contact), "Direct & WhatsApp (Owner):", fill=COLOR_GREEN, font=font_label)
    draw.text((r_x, y_contact + 18), "(254) 612-1399", fill=COLOR_WHITE, font=font_body_bold)
    
    # 2. AI PHONE NUMBER (24/7 CALL LINE)
    y_ai = y_contact + 58
    draw.text((r_x, y_ai), "24/7 AI Instant Booking Line:", fill=COLOR_GOLD, font=font_label)
    draw.text((r_x, y_ai + 18), "(254) 852-8163", fill=COLOR_WHITE, font=font_body_bold)
    
    # 3. EMAIL
    y_em = y_ai + 58
    draw.text((r_x, y_em), "Email Inquiries:", fill=COLOR_GRAY_MUTED, font=font_label)
    draw.text((r_x, y_em + 18), "arizmendir754@gmail.com", fill=COLOR_WHITE, font=font_body)
    
    # 4. LOCATION / SERVICE AREA
    y_loc = y_em + 54
    draw.text((r_x, y_loc), "Service Area:", fill=COLOR_GRAY_MUTED, font=font_label)
    draw.text((r_x, y_loc + 18), "Killeen, Harker Heights, Copperas Cove & Belton, TX", fill=COLOR_GRAY_LIGHT, font=font_small)

    # 5. TRUST BADGE
    y_badge = y_loc + 48
    draw.rounded_rectangle([r_x, y_badge, safe_right, y_badge + 28], radius=6, fill=(18, 30, 24), outline=COLOR_GREEN, width=1)
    draw.text((r_x + 14, y_badge + 6), "COMMERCIALLY INSURED  •  FREE ESTIMATES", fill=COLOR_LIME, font=font_tiny_bold)

    # Lush Grass bottom border
    draw_lush_grass_border(img, y_base=HEIGHT, max_h=80)

    # Save PNG at 300 DPI
    img.save(filename, dpi=(300, 300), format="PNG")
    print(f"Front Card saved: {filename}")


# =========================================================================
# 2. BACK OF BUSINESS CARD (Exact Match to User Reference Photo)
# =========================================================================
def create_back_card(filename="Rodriguez_LawnCare_Card_BACK.png"):
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BLACK)
    draw = ImageDraw.Draw(img)
    
    safe_left = 65
    safe_top = 55
    safe_right = WIDTH - 65
    
    # ---------------- RIGHT SIDE: WATERMARK LAWNMOWER ----------------
    # In the reference card, the back features a large lawnmower on the right side
    wm_cx = 780
    wm_cy = 280
    draw_lawnmower(draw, wm_cx, wm_cy, scale=2.35, is_watermark=True)

    # ---------------- LEFT SIDE: SERVICES LIST ----------------
    # Header: "OUR SERVICES"
    draw.text((safe_left, safe_top + 10), "OUR SERVICES", fill=COLOR_GREEN, font=font_h2)
    draw.line([(safe_left, safe_top + 48), (safe_left + 420, safe_top + 48)], fill=COLOR_GREEN, width=2)
    
    # Services List (Exact from Rodriguez LawnCare website)
    services = [
        "Commercial Lawn Mowing & Striping",
        "Razor-Sharp Perimeter Edging",
        "Shrub, Bush & Hedge Trimming",
        "Tree Trimming, Cutting & Planting",
        "Mulch Installation & Flower Beds",
        "Leaf Cleanups & Debris Removal",
        "Junk Removal & Property Hauling",
        "Full Seasonal Yard Restorations"
    ]
    
    list_y = safe_top + 68
    gap = 36
    
    for i, srv in enumerate(services):
        sy = list_y + (i * gap)
        # Green bullet dot
        draw.ellipse([safe_left, sy + 4, safe_left + 9, sy + 13], fill=COLOR_GREEN)
        draw.text((safe_left + 22, sy), srv, fill=COLOR_WHITE, font=font_body_bold)

    # ---------------- BOTTOM BANNER: GUARANTEE & PAYMENTS ----------------
    banner_y = HEIGHT - 150
    banner_w = WIDTH - (safe_left * 2)
    draw.rounded_rectangle([safe_left, banner_y, safe_right, banner_y + 54], radius=8, fill=(16, 20, 24), outline=COLOR_GRAY_DARK, width=1)
    
    # Guarantee on left
    draw.text((safe_left + 16, banner_y + 9), "100% SATISFACTION GUARANTEED", fill=COLOR_GOLD, font=font_small_bold)
    draw.text((safe_left + 16, banner_y + 30), "Commercial Equipment • Daily Sharpened Blades • Punctual Schedule", fill=COLOR_GRAY_MUTED, font=font_tiny_bold)
    
    # Payments on right
    draw.text((safe_right - 280, banner_y + 9), "ACCEPTED PAYMENTS:", fill=COLOR_GREEN, font=font_small_bold)
    draw.text((safe_right - 280, banner_y + 30), "Zelle • Venmo • Cash App • PayPal • Cash", fill=COLOR_WHITE, font=font_tiny_bold)

    # Lush Grass bottom border
    draw_lush_grass_border(img, y_base=HEIGHT, max_h=80)

    # Save PNG at 300 DPI
    img.save(filename, dpi=(300, 300), format="PNG")
    print(f"Back Card saved: {filename}")


if __name__ == "__main__":
    create_front_card("Rodriguez_LawnCare_Card_FRONT.png")
    create_back_card("Rodriguez_LawnCare_Card_BACK.png")
    print("FINISHED GENERATING MATCHING BUSINESS CARDS!")
