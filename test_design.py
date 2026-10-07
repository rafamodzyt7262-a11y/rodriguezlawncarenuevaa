import math
import random
from PIL import Image, ImageDraw, ImageFont

# Test grass blade drawing
def draw_lush_grass(img, y_base=638, max_height=75):
    draw = ImageDraw.Draw(img)
    width = img.width
    
    # Seed for consistent, natural look
    random.seed(42)
    
    grass_colors = [
        (15, 81, 50),     # deep forest green
        (21, 128, 61),    # medium rich green
        (22, 163, 74),    # vibrant green
        (34, 197, 94),    # bright lime-emerald
        (74, 222, 128),   # highlight light green
        (134, 239, 172)   # pale tip highlight
    ]
    
    # 4 layers of grass blades from back to front
    for layer in range(4):
        step = 3
        layer_h_mult = 0.6 + (layer * 0.15)
        for x in range(0, width + 10, step):
            # random blade height
            h = int(random.uniform(max_height * 0.5, max_height) * layer_h_mult)
            curve = random.uniform(-14, 14)
            tip_x = x + curve
            tip_y = y_base - h
            
            # color based on layer & randomness
            color_idx = min(len(grass_colors) - 1, layer + random.randint(0, 2))
            col = grass_colors[color_idx]
            
            # blade polygon (triangular)
            base_w = random.uniform(2.5, 4.5)
            pts = [
                (x - base_w, y_base),
                (tip_x, tip_y),
                (x + base_w, y_base)
            ]
            draw.polygon(pts, fill=col)
            
    # Bottom solid base gradient strip so bottom is 100% covered
    for y in range(y_base - 18, y_base):
        alpha = (y - (y_base - 18)) / 18.0
        r = int(10 * (1 - alpha) + 15 * alpha)
        g = int(40 * (1 - alpha) + 80 * alpha)
        b = int(20 * (1 - alpha) + 35 * alpha)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

# Test Lawnmower vector drawing
def draw_lawnmower(draw, cx, cy, scale=1.0, color=(255, 255, 255), accent=(34, 197, 94)):
    # cx, cy is the center of the deck
    # scale factor
    s = scale
    
    # Wheels
    # Rear wheel (larger)
    rw_r = int(22 * s)
    rw_x = cx - int(45 * s)
    rw_y = cy + int(12 * s)
    draw.ellipse([rw_x - rw_r, rw_y - rw_r, rw_x + rw_r, rw_y + rw_r], fill=(30, 30, 30), outline=color, width=max(2, int(3 * s)))
    draw.ellipse([rw_x - int(8*s), rw_y - int(8*s), rw_x + int(8*s), rw_y + int(8*s)], fill=accent)
    # Wheel spokes
    draw.line([(rw_x - rw_r + 4, rw_y), (rw_x + rw_r - 4, rw_y)], fill=color, width=int(2*s))
    draw.line([(rw_x, rw_y - rw_r + 4), (rw_x, rw_y + rw_r - 4)], fill=color, width=int(2*s))
    
    # Front wheel (smaller)
    fw_r = int(15 * s)
    fw_x = cx + int(45 * s)
    fw_y = cy + int(18 * s)
    draw.ellipse([fw_x - fw_r, fw_y - fw_r, fw_x + fw_r, fw_y + fw_r], fill=(30, 30, 30), outline=color, width=max(2, int(3 * s)))
    draw.ellipse([fw_x - int(5*s), fw_y - int(5*s), fw_x + int(5*s), fw_y + int(5*s)], fill=accent)
    
    # Mower Deck (Chassis)
    deck_pts = [
        (rw_x, cy + int(8 * s)),
        (rw_x + int(10 * s), cy - int(10 * s)),
        (cx - int(15 * s), cy - int(15 * s)),
        (cx + int(35 * s), cy - int(15 * s)),
        (fw_x + int(10 * s), cy + int(12 * s)),
        (fw_x - int(15 * s), cy + int(18 * s)),
        (cx - int(10 * s), cy + int(18 * s)),
        (rw_x, cy + int(18 * s))
    ]
    draw.polygon(deck_pts, fill=accent, outline=color)
    draw.line(deck_pts + [deck_pts[0]], fill=color, width=max(2, int(3 * s)))
    
    # Engine Block / Cowl on top
    eng_pts = [
        (cx - int(25 * s), cy - int(15 * s)),
        (cx - int(20 * s), cy - int(38 * s)),
        (cx + int(15 * s), cy - int(38 * s)),
        (cx + int(22 * s), cy - int(15 * s))
    ]
    draw.polygon(eng_pts, fill=(240, 240, 240), outline=color)
    draw.line(eng_pts + [eng_pts[0]], fill=color, width=max(2, int(3 * s)))
    
    # Engine details (air filter / pull cord)
    draw.rounded_rectangle([cx - int(12 * s), cy - int(45 * s), cx + int(8 * s), cy - int(38 * s)], radius=int(3*s), fill=color)
    
    # Push Handle
    handle_start_x = rw_x + int(5 * s)
    handle_start_y = cy - int(5 * s)
    handle_mid_x = cx - int(65 * s)
    handle_mid_y = cy - int(45 * s)
    handle_grip_x = cx - int(95 * s)
    handle_grip_y = cy - int(75 * s)
    
    draw.line([(handle_start_x, handle_start_y), (handle_mid_x, handle_mid_y), (handle_grip_x, handle_grip_y)], fill=color, width=max(2, int(4 * s)))
    # Grip bar
    draw.line([(handle_grip_x - int(6*s), handle_grip_y - int(6*s)), (handle_grip_x + int(6*s), handle_grip_y + int(6*s))], fill=accent, width=max(3, int(6 * s)))
    
    # Grass bag / discharge chute in back
    bag_pts = [
        (rw_x - int(5 * s), cy + int(5 * s)),
        (cx - int(55 * s), cy - int(8 * s)),
        (cx - int(60 * s), cy + int(12 * s)),
        (rw_x, cy + int(18 * s))
    ]
    draw.polygon(bag_pts, fill=(40, 40, 40), outline=color)
    draw.line(bag_pts + [bag_pts[0]], fill=color, width=max(2, int(2 * s)))

# Quick test
img = Image.new("RGB", (1088, 638), (10, 10, 10))
draw = ImageDraw.Draw(img)
draw_lawnmower(draw, 300, 300, scale=1.5)
draw_lush_grass(img, 638, 75)
img.save("test_mower.png")
print("TEST MOWER & GRASS OK")
