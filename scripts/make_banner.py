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

d.text((80 * S, 70 * S), "OKTO PULSE  ·  BENCHMARKS", font=font(20, 1), fill=GREEN)
d.text((80 * S, 110 * S), "Staged vs. direct", font=font(70, 7), fill=WHITE)
d.text((80 * S, 190 * S), "agent edits", font=font(70, 7), fill=WHITE)
d.text((80 * S, 295 * S), "Paired, harness-graded SWE-bench Lite runs", font=font(24, 0), fill=GREY)
d.text((80 * S, 330 * S), "of Okto Pulse's plan-then-edit workflow.", font=font(24, 0), fill=GREY)

# stat cards
cards = [("10 / 10", "staged · qwen3.8-flash", GREEN), ("9 / 10", "direct · qwen3.8-flash", "#6d7a92"),
         ("10 / 10", "staged · Qwen3.5-27B", GREEN)]
x0, y0, cw, ch, gap = 700, 90, 220, 130, 16
for i, (big, small, col) in enumerate(cards[:2]):
    x = x0 + i * (cw + gap)
    d.rounded_rectangle([x * S, y0 * S, (x + cw) * S, (y0 + ch) * S], 16 * S, fill=(255, 255, 255, 0) if False else "#161c27", outline="#2a3345", width=2)
    d.text(((x + 20) * S, (y0 + 22) * S), big, font=font(40, 7), fill=col)
    d.text(((x + 20) * S, (y0 + 86) * S), small, font=font(14, 5), fill=GREY)
d.rounded_rectangle([x0 * S, (y0 + ch + gap) * S, (x0 + 2 * cw + gap) * S, (y0 + ch + gap + 70) * S], 16 * S, fill="#161c27", outline="#2a3345", width=2)
d.text(((x0 + 20) * S, (y0 + ch + gap + 12) * S), "SWE-bench Lite · pytest slice · n = 10", font=font(16, 2), fill=WHITE)
d.text(((x0 + 20) * S, (y0 + ch + gap + 38) * S), "graded by the official swebench harness", font=font(14, 0), fill=GREY)

img = img.resize((W * 2, H * 2), Image.LANCZOS) if S != 2 else img
os.makedirs("assets", exist_ok=True)
img.save("assets/banner.png", optimize=True)
