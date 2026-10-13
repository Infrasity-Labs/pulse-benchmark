"""Render assets/pulse-benchmark-banner-v2.png (2400x640; drawn at 2x)."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H, S = 1200, 320, 2
SANS = "/System/Library/Fonts/HelveticaNeue.ttc"  # 0 regular, 1 bold
MONO = "/System/Library/Fonts/Menlo.ttc"
INK, LIME, MUTED = "#0b1f1a", "#c6f432", "#9db0a9"

P = lambda v: int(v * S)
sans = lambda s, i=0: ImageFont.truetype(SANS, P(s), index=i)
mono = lambda s, i=0: ImageFont.truetype(MONO, P(s), index=i)

img = Image.new("RGB", (P(W), P(H)), INK)
d = ImageDraw.Draw(img)
d.rectangle([P(70), P(86), P(130), P(92)], fill=LIME)
d.text((P(70), P(112)), "pulse-benchmark", font=sans(76, 1), fill="#f4f1ea")
d.text((P(72), P(214)), "Benchmarking agents inside Okto Pulse's plan-then-edit workflow.", font=sans(22, 0), fill=MUTED)

os.makedirs("assets", exist_ok=True)
img.save("assets/pulse-benchmark-banner-v2.png", optimize=True)
