import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1088
HEIGHT = 638

def draw_grass_border(img, y_base=638, max_h=80):
    draw = ImageDraw.Draw(img)
    random.seed(1234)
    
    grass_colors = [
        (13, 71, 40),
        (21, 128, 61),
        (34, 197, 94),
        (22, 163, 74),
        (74, 222, 128),
        (134, 239, 172)
    ]
    
    # 5 dense layers of grass blades
    for layer in range(5):
        h_factor = 0.55 + (layer * 0.12)
        step = 2
        for x in range(-5, WIDTH + 10, step):
            blade_h = int(random.uniform(max_h * 0.5, max_h) * h_factor)
            curve = random.uniform(-16, 16)
            tip_x = x + curve
            tip_y = y_base - blade_h
            
            color_choice = grass_colors[min(len(grass_colors)-1, layer + random.randint(0, 1))]
            base_w = random.uniform(2.5, 4.5)
            
            draw.polygon([
                (x - base_w, y_base),
                (tip_x, tip_y),
                (x + base_w, y_base)
            ], fill=color_choice)
            
    # Bottom solid base
    for y in range(y_base - 14, y_base):
        draw.line([(0, y), (WIDTH, y)], fill=(12, 60, 32))

def draw_detailed_mower(draw, cx, cy, scale=1.0, alpha_white=255, alpha_green=255):
    s = scale
    
    w_col = (255, 255, 255)
    g_col = (34, 197, 94)
    dark_gray = (35, 38, 42)
    tire_col = (20, 22, 25)
    
    # Back Wheel (Large)
    rw_r = int(26 * s)
    rw_x = cx - int(45 * s)
    rw_y = cy + int(14 * s)
    
    # Tire with treads
    draw.ellipse([rw_x - rw_r, rw_y - rw_r, rw_x + rw_r, rw_y + rw_r], fill=tire_col, outline=w_col, width=max(2, int(3*s)))
    # Wheel rim
    rim_r = int(18 * s)
    draw.ellipse([rw_x - rim_r, rw_y - rim_r, rw_x + rim_r, rw_y + rim_r], fill=dark_gray, outline=g_col, width=max(1, int(2*s)))
    # Hubcap
    draw.ellipse([rw_x - int(7*s), rw_y - int(7*s), rw_x + int(7*s), rw_y + int(7*s)], fill=g_col, outline=w_col, width=1)
    # Wheel Spokes
    for angle in [0, 45, 90, 135]:
        rad = math.radians(angle)
        dx = int(math.cos(rad) * (rim_r - 2))
        dy = int(math.sin(rad) * (rim_r - 2))
        draw.line([(rw_x - dx, rw_y - dy), (rw_x + dx, rw_y + dy)], fill=w_col, width=max(1, int(2*s)))
        
    # Front Wheel (Smaller)
    fw_r = int(17 * s)
    fw_x = cx + int(50 * s)
    fw_y = cy + int(22 * s)
    
    draw.ellipse([fw_x - fw_r, fw_y - fw_r, fw_x + fw_r, fw_y + fw_r], fill=tire_col, outline=w_col, width=max(2, int(3*s)))
    f_rim = int(11 * s)
    draw.ellipse([fw_x - f_rim, fw_y - f_rim, fw_x + f_rim, fw_y + f_rim], fill=dark_gray, outline=g_col, width=max(1, int(2*s)))
    draw.ellipse([fw_x - int(5*s), fw_y - int(5*s), fw_x + int(5*s), fw_y + int(5*s)], fill=g_col, outline=w_col, width=1)
    for angle in [0, 90]:
        rad = math.radians(angle)
        dx = int(math.cos(rad) * (f_rim - 2))
        dy = int(math.sin(rad) * (f_rim - 2))
        draw.line([(fw_x - dx, fw_y - dy), (fw_x + dx, fw_y + dy)], fill=w_col, width=max(1, int(2*s)))

    # Grass Catcher Bag (Rear)
    bag = [
        (rw_x - int(8 * s), cy + int(6 * s)),
        (cx - int(75 * s), cy - int(12 * s)),
        (cx - int(85 * s), cy + int(8 * s)),
        (cx - int(50 * s), cy + int(24 * s)),
        (rw_x, cy + int(22 * s))
    ]
    draw.polygon(bag, fill=(28, 30, 34), outline=w_col)
    draw.line(bag + [bag[0]], fill=w_col, width=max(1, int(2*s)))
    # Bag mesh texture lines
    draw.line([(cx - int(70 * s), cy - int(6 * s)), (cx - int(55 * s), cy + int(18 * s))], fill=dark_gray, width=max(1, int(2*s)))
    draw.line([(cx - int(60 * s), cy - int(2 * s)), (cx - int(45 * s), cy + int(20 * s))], fill=dark_gray, width=max(1, int(2*s)))

    # Cutting Deck (Main Body)
    deck = [
        (rw_x, cy + int(8 * s)),
        (rw_x + int(12 * s), cy - int(12 * s)),
        (cx - int(10 * s), cy - int(16 * s)),
        (cx + int(38 * s), cy - int(16 * s)),
        (fw_x + int(12 * s), cy + int(14 * s)),
        (fw_x - int(14 * s), cy + int(24 * s)),
        (cx, cy + int(24 * s)),
        (rw_x, cy + int(22 * s))
    ]
    draw.polygon(deck, fill=g_col, outline=w_col)
    draw.line(deck + [deck[0]], fill=w_col, width=max(2, int(3*s)))
    
    # Deck bottom metallic trim / blade shroud
    draw.line([(rw_x + int(10 * s), cy + int(20 * s)), (fw_x, cy + int(22 * s))], fill=(230, 230, 230), width=max(2, int(3*s)))

    # Engine Cowling / Shroud (Top Center)
    eng = [
        (cx - int(25 * s), cy - int(16 * s)),
        (cx - int(20 * s), cy - int(42 * s)),
        (cx + int(15 * s), cy - int(42 * s)),
        (cx + int(24 * s), cy - int(16 * s))
    ]
    draw.polygon(eng, fill=(245, 245, 245), outline=w_col)
    draw.line(eng + [eng[0]], fill=w_col, width=max(2, int(3*s)))
    
    # Engine black grill & branding strip
    draw.rounded_rectangle([cx - int(16 * s), cy - int(34 * s), cx + int(16 * s), cy - int(22 * s)], radius=int(3*s), fill=dark_gray, outline=g_col, width=max(1, int(2*s)))
    # Air recoil starter top cap
    draw.rounded_rectangle([cx - int(12 * s), cy - int(48 * s), cx + int(8 * s), cy - int(42 * s)], radius=int(2*s), fill=w_col)

    # Push Handle Bars (Angled back up)
    h_base_x = rw_x + int(8 * s)
    h_base_y = cy - int(8 * s)
    h_mid_x = cx - int(75 * s)
    h_mid_y = cy - int(55 * s)
    h_top_x = cx - int(115 * s)
    h_top_y = cy - int(92 * s)

    # Lower tubular steel handle
    draw.line([(h_base_x, h_base_y), (h_mid_x, h_mid_y)], fill=w_col, width=max(2, int(4*s)))
    # Folding adjustment knob
    draw.ellipse([h_mid_x - int(6*s), h_mid_y - int(6*s), h_mid_x + int(6*s), h_mid_y + int(6*s)], fill=g_col, outline=w_col, width=1)
    # Upper handle
    draw.line([(h_mid_x, h_mid_y), (h_top_x, h_top_y)], fill=w_col, width=max(2, int(4*s)))
    
    # Handle Grip Cushion (Green)
    draw.line([(h_top_x - int(6*s), h_top_y - int(6*s)), (h_top_x + int(6*s), h_top_y + int(6*s))], fill=g_col, width=max(4, int(7*s)))
    # Safety bail lever
    draw.line([(h_mid_x - int(10*s), h_mid_y - int(16*s)), (h_top_x - int(4*s), h_top_y - int(2*s))], fill=(200, 200, 200), width=max(1, int(2*s)))

    # Flying grass clippings from deck!
    random.seed(99)
    for _ in range(12):
        gx = cx + int(random.uniform(15, 65) * s)
        gy = cy + int(random.uniform(18, 38) * s)
        gw = int(random.uniform(4, 10) * s)
        gh = int(random.uniform(2, 4) * s)
        draw.line([(gx, gy), (gx + gw, gy - gh)], fill=g_col, width=max(1, int(2*s)))

img = Image.new("RGB", (WIDTH, HEIGHT), (5, 5, 5))
draw = ImageDraw.Draw(img)
draw_detailed_mower(draw, 500, 300, scale=2.0)
draw_grass_border(img, 638, 80)
img.save("test_detailed_mower.png")
print("DETAILED MOWER GENERATED")
