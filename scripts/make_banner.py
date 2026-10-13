"""Render assets/banner.png (2400x800, drawn at 2x then downsampled for smooth edges)."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, S = 1200, 400, 2
FONT = "/System/Library/Fonts/Avenir Next.ttc"


def font(size, idx=0):
    return ImageFont.truetype(FONT, size * S, index=idx)


img = Image.new("RGB", (W * S, H * S), "#0d1117")
px = img.load()
# diagonal gradient background
for y in range(H * S):
    for x in range(W * S):
        t = (x / (W * S) + y / (H * S)) / 2
        px[x, y] = (int(13 + 14 * t), int(17 + 18 * t), int(23 + 40 * t))

# soft green glow
glow = Image.new("RGB", img.size, (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([780 * S, -200 * S, 1400 * S, 420 * S], fill=(30, 140, 100))
glow = glow.filter(ImageFilter.GaussianBlur(120 * S))
img = Image.blend(img, Image.eval(Image.composite(glow, img, Image.new("L", img.size, 255)), lambda v: v), 0.0)
from PIL import ImageChops
img = ImageChops.add(img, glow.point(lambda v: int(v * 0.55)))

d = ImageDraw.Draw(img)
# subtle grid
for gx in range(0, W, 40):
    d.line([gx * S, 0, gx * S, H * S], fill=(255, 255, 255, 8), width=1) if False else None

GREEN, GREY, WHITE = "#3ddc97", "#8b95a7", "#f0f3f8"

d.text((60 * S, 50 * S), "OKTO PULSE  ·  BENCHMARKS", font=font(20, 1), fill=GREEN)
d.text((60 * S, 85 * S), "Staged vs. direct agent edits", font=font(54, 7), fill=WHITE)
d.text((60 * S, 160 * S), "SWE-bench Lite · pytest slice · n = 10", font=font(22, 0), fill=GREY)

cards = [
    ("qwen3.8-flash", "Resolved · harness-graded", "10/10", "9/10"),
    ("Qwen3.5-27B", "Resolved · harness-graded", "10/10", "10/10"),
    ("Qwen3.5-9B", "Code change applied · not graded", "10/10", "10/10"),
]
cw, gap, y0, ch = 340, 30, 215, 150
x0 = 60
for i, (name, metric, st, di) in enumerate(cards):
    x = x0 + i * (cw + gap)
    d.rounded_rectangle([x * S, y0 * S, (x + cw) * S, (y0 + ch) * S], 16 * S, fill="#161c27", outline="#2a3345", width=2)
    d.text(((x + 24) * S, (y0 + 16) * S), name, font=font(26, 7), fill=WHITE)
    d.text(((x + 24) * S, (y0 + 52) * S), metric, font=font(14, 5), fill=GREY)
    d.text(((x + 24) * S, (y0 + 82) * S), "STAGED", font=font(12, 1), fill=GREEN)
    d.text(((x + 24) * S, (y0 + 98) * S), st, font=font(32, 7), fill=GREEN)
    d.text(((x + 190) * S, (y0 + 82) * S), "DIRECT", font=font(12, 1), fill=GREY)
    d.text(((x + 190) * S, (y0 + 98) * S), di, font=font(32, 7), fill="#a3adc0")

img = img.resize((W * 2, H * 2), Image.LANCZOS) if S != 2 else img
os.makedirs("assets", exist_ok=True)
img.save("assets/banner.png", optimize=True)
