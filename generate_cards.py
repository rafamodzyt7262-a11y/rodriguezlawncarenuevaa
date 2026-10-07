import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH = 2175
HEIGHT = 1275
OUT_DIR = 'business_cards'
os.makedirs(OUT_DIR, exist_ok=True)

FONT_BOLD = 'C:/Windows/Fonts/segoeuib.ttf'
FONT_REGULAR = 'C:/Windows/Fonts/segoeui.ttf'

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# Colors
DARK_BASE = (11, 17, 24)       # Deep charcoal luxury
EMERALD = (34, 197, 94)        # Vivid emerald green
EMERALD_DEEP = (16, 85, 42)
EMERALD_LIGHT = (134, 239, 172)
GOLD = (245, 158, 11)          # Warm amber gold
WHITE = (255, 255, 255)
GRAY_TEXT = (148, 163, 184)
GRAY_LINE = (38, 52, 69)
BADGE_BG = (20, 30, 42)

# --- Vector Icon Helper Functions ---
def draw_checkmark(draw, x, y, size=32, color=WHITE, width=4):
    p1 = (x, y + size * 0.55)
    p2 = (x + size * 0.38, y + size * 0.95)
    p3 = (x + size * 0.95, y + size * 0.15)
    draw.line([p1, p2, p3], fill=color, width=width, joint='curve')

def draw_star(draw, cx, cy, r=16, color=GOLD):
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        radius = r if i % 2 == 0 else r * 0.45
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(points, fill=color)

def draw_phone_icon(draw, cx, cy, size=24, color=WHITE):
    # Modern minimalist phone receiver
    r = size // 2
    draw.arc([cx - r, cy - r, cx + r, cy + r], start=210, end=330, fill=color, width=4)
    draw.line([(cx - r*0.7, cy - r*0.1), (cx - r*0.3, cy + r*0.5)], fill=color, width=4)
    draw.line([(cx + r*0.7, cy - r*0.1), (cx + r*0.3, cy + r*0.5)], fill=color, width=4)

def draw_pin_icon(draw, cx, cy, size=22, color=GOLD):
    r = size // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r*0.6], fill=color)
    draw.polygon([(cx - r*0.7, cy), (cx + r*0.7, cy), (cx, cy + r*1.3)], fill=color)
    draw.ellipse([cx - r*0.35, cy - r*0.5, cx + r*0.35, cy + r*0.2], fill=DARK_BASE)

def draw_mail_icon(draw, x, y, w=32, h=22, color=WHITE):
    draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
    draw.line([(x, y), (x + w//2, y + h*0.65), (x + w, y)], fill=color, width=3)

# =========================================================================
# 1. FRONT OF BUSINESS CARD (Elite Landscape 2175 x 1275)
# =========================================================================
def build_front():
    # Base dark canvas
    base = Image.new('RGB', (WIDTH, HEIGHT), color=DARK_BASE)

    # Composite lifted Tundra / team image on the right side with luxury gradient blend
    truck_path = 'assets/images/team.jpg'
    if os.path.exists(truck_path):
        truck = Image.open(truck_path).convert('RGB')
        # Scale to fill right side
        t_w = int(HEIGHT * (truck.width / truck.height))
        truck = truck.resize((t_w, HEIGHT), Image.Resampling.LANCZOS)
        
        # Create gradient mask
        mask = Image.new('L', (t_w, HEIGHT), color=0)
        mask_draw = ImageDraw.Draw(mask)
        for x in range(t_w):
            alpha = int(255 * (x / t_w) ** 1.8 * 0.70)
            mask_draw.line([(x, 0), (x, HEIGHT)], fill=alpha)
        
        truck_x = WIDTH - t_w + 100
        base.paste(truck, (truck_x, 0), mask)

    draw = ImageDraw.Draw(base)

    # Diagonal luxury emerald slash accents in top right
    draw.polygon([(WIDTH - 500, 0), (WIDTH - 460, 0), (WIDTH, 460), (WIDTH, 500)], fill=(34, 197, 94))
    draw.polygon([(WIDTH - 360, 0), (WIDTH - 330, 0), (WIDTH, 330), (WIDTH, 360)], fill=(22, 101, 52))

    # Bottom status bar line
    draw.rectangle([0, HEIGHT - 110, WIDTH, HEIGHT], fill=(8, 12, 17))
    draw.line([(0, HEIGHT - 110), (WIDTH, HEIGHT - 110)], fill=EMERALD, width=5)

    LEFT = 140
    TOP = 110

    # Modern Leaf Shield Emblem
    cx, cy, r = LEFT + 55, TOP + 55, 55
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(16, 75, 38), outline=EMERALD, width=4)
    # White stylized leaf
    draw.polygon([(cx, cy - 35), (cx + 28, cy), (cx, cy + 35), (cx - 28, cy)], fill=WHITE)
    draw.line([(cx, cy - 35), (cx, cy + 35)], fill=(16, 75, 38), width=4)

    # Brand Title
    font_brand = get_font(FONT_BOLD, 78)
    font_sub = get_font(FONT_BOLD, 24)
    
    brand_x = LEFT + 140
    brand_y = TOP + 10
    draw.text((brand_x, brand_y), "RODRIGUEZ ", fill=WHITE, font=font_brand)
    bbox = draw.textbbox((brand_x, brand_y), "RODRIGUEZ ", font=font_brand)
    draw.text((bbox[2], brand_y), "LAWNCARE", fill=EMERALD, font=font_brand)

    # Tagline
    draw.text((brand_x + 5, brand_y + 85), "COMMERCIAL & RESIDENTIAL LANDSCAPING", fill=EMERALD_LIGHT, font=font_sub)

    # Divider line
    div_y = TOP + 175
    draw.line([(LEFT, div_y), (LEFT + 1050, div_y)], fill=GRAY_LINE, width=3)

    # --- MAIN CONTACT CONTAINER CARDS ---
    card_w = 1150
    
    # 1. Primary AI Phone Line (Big Callout Card)
    c1_y = div_y + 40
    c1_h = 160
    draw.rounded_rectangle([LEFT, c1_y, LEFT + card_w, c1_y + c1_h], radius=16, fill=(16, 26, 36), outline=EMERALD, width=3)
    
    draw.text((LEFT + 35, c1_y + 20), "24/7 AI ESTIMATE LINE  •  BILINGUAL (ENGLISH & SPANISH)", fill=EMERALD, font=get_font(FONT_BOLD, 22))
    draw.text((LEFT + 35, c1_y + 60), "(254) 852-8163", fill=WHITE, font=get_font(FONT_BOLD, 64))

    # Pill badge "CALL ANYTIME"
    p_x = LEFT + card_w - 260
    draw.rounded_rectangle([p_x, c1_y + 48, p_x + 220, c1_y + 112], radius=32, fill=EMERALD)
    draw.text((p_x + 35, c1_y + 66), "CALL 24/7", fill=(10, 20, 15), font=get_font(FONT_BOLD, 26))

    # 2. Split Cards: Owner WhatsApp + Email
    c2_y = c1_y + c1_h + 25
    half_w = (card_w - 25) // 2

    # Left: Owner Direct
    draw.rounded_rectangle([LEFT, c2_y, LEFT + half_w, c2_y + 140], radius=14, fill=(16, 26, 36), outline=GRAY_LINE, width=2)
    draw.text((LEFT + 30, c2_y + 20), "OWNER DIRECT / WHATSAPP", fill=GRAY_TEXT, font=get_font(FONT_BOLD, 20))
    draw.text((LEFT + 30, c2_y + 58), "(254) 612-1399", fill=WHITE, font=get_font(FONT_BOLD, 46))

    # Right: Email
    draw.rounded_rectangle([LEFT + half_w + 25, c2_y, LEFT + card_w, c2_y + 140], radius=14, fill=(16, 26, 36), outline=GRAY_LINE, width=2)
    draw.text((LEFT + half_w + 55, c2_y + 20), "OFFICIAL INQUIRIES & ESTIMATES", fill=GRAY_TEXT, font=get_font(FONT_BOLD, 20))
    draw.text((LEFT + half_w + 55, c2_y + 62), "arizmendir754@gmail.com", fill=WHITE, font=get_font(FONT_BOLD, 34))

    # 3. Service Coverage Cities Bar
    c3_y = c2_y + 170
    draw_pin_icon(draw, LEFT + 16, c3_y + 14, size=24, color=GOLD)
    draw.text((LEFT + 40, c3_y), "SERVICE AREAS:", fill=GOLD, font=get_font(FONT_BOLD, 26))
    draw.text((LEFT + 280, c3_y), "Killeen  •  Harker Heights  •  Copperas Cove  •  Belton, TX", fill=WHITE, font=get_font(FONT_BOLD, 26))

    # 4. Value Highlights (Crisp Checks)
    perks_y = c3_y + 65
    perks = [
        "Weekly & Bi-Weekly Mowing",
        "Commercial Blade Sharpening",
        "Zero Long-Term Contracts"
    ]
    px = LEFT
    for p in perks:
        draw_checkmark(draw, px, perks_y + 2, size=22, color=EMERALD, width=3)
        draw.text((px + 32, perks_y), p, fill=GRAY_TEXT, font=get_font(FONT_BOLD, 22))
        px += draw.textlength(p, font=get_font(FONT_BOLD, 22)) + 75

    # --- BOTTOM STATUS BAR ---
    bot_y = HEIGHT - 75
    font_bot = get_font(FONT_BOLD, 24)
    draw.text((LEFT, bot_y), "WE ACCEPT:", fill=GRAY_TEXT, font=font_bot)
    
    # Payment Badges
    badges = ["Zelle", "Venmo", "PayPal", "Cash App"]
    bx = LEFT + 165
    for b in badges:
        bw = draw.textlength(b, font=font_bot) + 36
        draw.rounded_rectangle([bx, bot_y - 8, bx + bw, bot_y + 36], radius=8, fill=BADGE_BG, outline=(51, 65, 85), width=2)
        draw.text((bx + 18, bot_y - 2), b, fill=WHITE, font=font_bot)
        bx += bw + 18

    # Star rating
    star_x = WIDTH - 590
    draw_star(draw, star_x - 20, bot_y + 12, r=14, color=GOLD)
    draw.text((star_x, bot_y - 2), "100% SATISFACTION GUARANTEED", fill=GOLD, font=font_bot)

    # Save 600 DPI & 300 DPI
    f_path = os.path.join(OUT_DIR, 'business_card_front.png')
    base.save(f_path, dpi=(600, 600))
    base_300 = base.resize((1088, 638), Image.Resampling.LANCZOS)
    base_300.save(os.path.join(OUT_DIR, 'business_card_front_300dpi.png'), dpi=(300, 300))
    print(f"Front created: {f_path}")

# =========================================================================
# 2. BACK OF BUSINESS CARD (Elite Landscape 2175 x 1275)
# =========================================================================
def build_back():
    base = Image.new('RGB', (WIDTH, HEIGHT), color=(10, 16, 22))

    # Background lawn mowing stripes texture on top half
    mow_path = 'assets/images/mowing.jpg'
    if os.path.exists(mow_path):
        mow = Image.open(mow_path).convert('RGB')
        mow = mow.resize((WIDTH, 420), Image.Resampling.LANCZOS)
        # Apply dark gradient tint
        tint = Image.new('RGB', (WIDTH, 420), color=(8, 35, 18))
        mow = Image.blend(mow, tint, 0.65)
        base.paste(mow, (0, 0))

    draw = ImageDraw.Draw(base)

    # Divider bar
    draw.line([(0, 420), (WIDTH, 420)], fill=EMERALD, width=6)

    LEFT = 140

    # Header Over Dark Banner
    font_h1 = get_font(FONT_BOLD, 64)
    font_h2 = get_font(FONT_BOLD, 26)
    draw.text((LEFT, 90), "RODRIGUEZ LAWNCARE & LANDSCAPING", fill=WHITE, font=font_h1)
    draw.text((LEFT, 185), "PREMIUM RESIDENTIAL & COMMERCIAL GROUNDS CARE", fill=EMERALD_LIGHT, font=font_h2)
    draw.text((LEFT, 235), "Proudly Serving Killeen • Harker Heights • Copperas Cove • Belton, Texas", fill=GRAY_TEXT, font=get_font(FONT_REGULAR, 24))

    # --- 8 SERVICES IN 2 COLUMNS ---
    services_col1 = [
        ("1. Front & Back Yard Cut + Edging", "Precision height mowing & concrete blade edging"),
        ("2. Sidewalk & Driveway Edging", "Razor-sharp 90-degree lines & air blowing"),
        ("3. Shrub & Hedge Trimming", "Sculpted decorative bush shaping & debris haul"),
        ("4. Tree Trimming & Hazard Cutting", "Limb canopy elevation & storm branch clearance")
    ]

    services_col2 = [
        ("5. Tree Planting & Installation", "Healthy root fertilization, deep staking & care"),
        ("6. Seasonal Leaf Cleanup & Raking", "Heavy fall/spring leaf clearing & turf bagging"),
        ("7. Yard Debris & Brush Clearing", "Overgrown lot reclamation & fallen timber haul"),
        ("8. Heavy Junk Removal & Hauling", "Bulky estate items, scrap, & dump runs")
    ]

    srv_start_y = 470
    row_gap = 100
    font_srv_title = get_font(FONT_BOLD, 30)
    font_srv_sub = get_font(FONT_REGULAR, 20)

    # Column 1
    for i, (title, sub) in enumerate(services_col1):
        sy = srv_start_y + i * row_gap
        # Green checkbox
        draw.rounded_rectangle([LEFT, sy, LEFT + 44, sy + 44], radius=10, fill=(16, 75, 38), outline=EMERALD, width=2)
        draw_checkmark(draw, LEFT + 10, sy + 8, size=24, color=WHITE, width=4)
        draw.text((LEFT + 65, sy), title, fill=WHITE, font=font_srv_title)
        draw.text((LEFT + 65, sy + 38), sub, fill=GRAY_TEXT, font=font_srv_sub)

    # Column 2
    col2_x = WIDTH // 2 + 50
    for i, (title, sub) in enumerate(services_col2):
        sy = srv_start_y + i * row_gap
        draw.rounded_rectangle([col2_x, sy, col2_x + 44, sy + 44], radius=10, fill=(16, 75, 38), outline=EMERALD, width=2)
        draw_checkmark(draw, col2_x + 10, sy + 8, size=24, color=WHITE, width=4)
        draw.text((col2_x + 65, sy), title, fill=WHITE, font=font_srv_title)
        draw.text((col2_x + 65, sy + 38), sub, fill=GRAY_TEXT, font=font_srv_sub)

    # --- SPECIAL OFFER PROMO BANNER ---
    promo_y = 900
    promo_w = WIDTH - (LEFT * 2)
    draw.rounded_rectangle([LEFT, promo_y, LEFT + promo_w, promo_y + 115], radius=16, fill=(22, 34, 26), outline=GOLD, width=3)
    
    draw_star(draw, LEFT + 45, promo_y + 57, r=16, color=GOLD)
    draw.text((LEFT + 80, promo_y + 22), "EXCLUSIVE NEW CLIENT PROMOTION", fill=GOLD, font=get_font(FONT_BOLD, 22))
    draw.text((LEFT + 80, promo_y + 56), "SAVE 15% ON YOUR FIRST MONTH OF WEEKLY SERVICE!", fill=WHITE, font=get_font(FONT_BOLD, 32))

    # --- BOTTOM CALL TO ACTION STRIP ---
    cta_y = 1045
    draw.rounded_rectangle([LEFT, cta_y, LEFT + promo_w, cta_y + 145], radius=16, fill=(16, 68, 34), outline=EMERALD, width=3)
    
    draw.text((LEFT + 40, cta_y + 22), "CALL OUR 24/7 AI ESTIMATE LINE:", fill=EMERALD_LIGHT, font=get_font(FONT_BOLD, 22))
    draw.text((LEFT + 40, cta_y + 56), "(254) 852-8163", fill=WHITE, font=get_font(FONT_BOLD, 54))

    # Right side: WhatsApp & Website
    right_x = WIDTH - 750
    draw.text((right_x, cta_y + 22), "DIRECT WHATSAPP & TEXTS:", fill=EMERALD_LIGHT, font=get_font(FONT_BOLD, 22))
    draw.text((right_x, cta_y + 56), "(254) 612-1399", fill=WHITE, font=get_font(FONT_BOLD, 48))
    draw.text((right_x, cta_y + 110), "arizmendir754@gmail.com  •  Free Estimates", fill=GRAY_TEXT, font=get_font(FONT_BOLD, 20))

    # Edge bottom line
    draw.rectangle([0, HEIGHT - 12, WIDTH, HEIGHT], fill=EMERALD)

    # Save
    b_path = os.path.join(OUT_DIR, 'business_card_back.png')
    base.save(b_path, dpi=(600, 600))
    base_300 = base.resize((1088, 638), Image.Resampling.LANCZOS)
    base_300.save(os.path.join(OUT_DIR, 'business_card_back_300dpi.png'), dpi=(300, 300))
    print(f"Back created: {b_path}")

if __name__ == '__main__':
    build_front()
    build_back()
    print("FINISHED ALL BUSINESS CARDS WITH LUXURY DESIGN!")
