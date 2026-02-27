"""
HARLEY SOLDER — Placeholder Eye Asset Generator
Generates procedural PNG eye assets for all emotion/intensity combos.
Run this once to populate assets/eyes/ before launching.

Usage: python generate_assets.py
"""

import os
import math
import random

try:
    from PIL import Image, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Install with: pip install Pillow")
    print("Harley will use procedural PyQt6 rendering as fallback.")
    exit(0)

SIZE = 256

EMOTION_PALETTE = {
    "neutral":    ((0, 180, 200),    (0, 80, 100)),
    "curious":    ((0, 200, 255),    (0, 90, 120)),
    "happy":      ((50, 220, 100),   (20, 100, 40)),
    "sad":        ((80, 100, 180),   (30, 40, 100)),
    "angry":      ((220, 60, 40),    (100, 20, 10)),
    "fear":       ((200, 160, 0),    (80, 60, 0)),
    "disgust":    ((140, 180, 60),   (60, 90, 20)),
    "surprised":  ((255, 200, 0),    (120, 90, 0)),
    "confused":   ((180, 100, 220),  (80, 40, 120)),
    "excited":    ((0, 240, 160),    (0, 100, 70)),
    "melancholy": ((80, 120, 160),   (30, 50, 80)),
    "glitch":     ((255, 0, 100),    (100, 0, 40)),
    "error":      ((255, 0, 0),      (120, 0, 0)),
}


def draw_eye(emotion: str, intensity: int) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (5, 5, 5, 255))
    draw = ImageDraw.Draw(img)

    primary, shadow = EMOTION_PALETTE.get(emotion, ((0, 180, 200), (0, 80, 100)))
    cx, cy = SIZE // 2, SIZE // 2
    r = SIZE * 0.42

    # Outer glow ring
    glow_alpha = {1: 30, 2: 60, 3: 100}[intensity]
    glow_r = r * (1.0 + intensity * 0.12)
    for i in range(8, 0, -1):
        a = int(glow_alpha * (i / 8))
        color = primary + (a,)
        rr = glow_r + i * 3
        draw.ellipse(
            [cx - rr, cy - rr, cx + rr, cy + rr],
            outline=color, width=2
        )

    # Outer ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 outline=primary + (200,), width=2)

    # Iris
    iris_r = r * 0.56
    for y in range(int(cy - iris_r), int(cy + iris_r)):
        for x in range(int(cx - iris_r), int(cx + iris_r)):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < iris_r:
                t = dist / iris_r
                r_c = int(shadow[0] + (primary[0] - shadow[0]) * (1 - t))
                g_c = int(shadow[1] + (primary[1] - shadow[1]) * (1 - t))
                b_c = int(shadow[2] + (primary[2] - shadow[2]) * (1 - t))
                img.putpixel((x, y), (r_c, g_c, b_c, 255))

    # Pupil
    pupil_r = r * 0.22
    draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r],
                 fill=(5, 5, 5, 255))

    # Intensity rings
    if intensity >= 2:
        ring_r = r * 0.73
        draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
                     outline=primary + (80,), width=1)

    if intensity >= 3:
        # Dashed outer ring for instability
        ring_r2 = r * 0.84
        for angle in range(0, 360, 20):
            a1 = math.radians(angle)
            a2 = math.radians(angle + 12)
            x1 = cx + ring_r2 * math.cos(a1)
            y1 = cy + ring_r2 * math.sin(a1)
            x2 = cx + ring_r2 * math.cos(a2)
            y2 = cy + ring_r2 * math.sin(a2)
            draw.line([x1, y1, x2, y2], fill=primary + (60,), width=1)

    # Specular highlight
    h_x = cx - iris_r * 0.25
    h_y = cy - iris_r * 0.3
    h_r = iris_r * 0.15
    draw.ellipse([h_x - h_r, h_y - h_r, h_x + h_r, h_y + h_r],
                 fill=(255, 255, 255, 80))

    # Glitch-specific corruption
    if emotion in ("glitch", "error") or intensity == 3:
        for _ in range(int(20 * intensity)):
            sx = random.randint(0, SIZE - 1)
            sy = random.randint(0, SIZE - 1)
            sw = random.randint(2, 8)
            sh = random.randint(1, 2)
            sc = random.choice([primary, (255, 255, 255)])
            sa = random.randint(40, 120)
            draw.rectangle([sx, sy, sx + sw, sy + sh], fill=sc + (sa,))

    # Scanlines
    for y in range(0, SIZE, 3):
        draw.line([(0, y), (SIZE, y)], fill=(0, 0, 0, 20))

    return img


def generate_all():
    os.makedirs("assets/eyes", exist_ok=True)
    count = 0
    for emotion in EMOTION_PALETTE:
        for intensity in [1, 2, 3]:
            img = draw_eye(emotion, intensity)
            path = f"assets/eyes/{emotion}_{intensity}.png"
            img.save(path)
            print(f"  ✓ {path}")
            count += 1
    print(f"\n  Generated {count} eye assets in assets/eyes/")


if __name__ == "__main__":
    print("\n  HARLEY SOLDER — Eye Asset Generator\n")
    generate_all()
    print("\n  Done. Run: python main.py\n")
