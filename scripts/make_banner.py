"""Render assets/pulse-benchmark-banner.png (2400x800; drawn at 2x)."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H, S = 1200, 400, 2
SANS = "/System/Library/Fonts/HelveticaNeue.ttc"  # 0 regular, 1 bold
MONO = "/System/Library/Fonts/Menlo.ttc"          # 0 regular, 1 bold
INK, PAPER = "#0b1f1a", "#f4f1ea"
LIME, MUTED, LINE = "#c6f432", "#7f948d", "#d8d3c6"

P = lambda v: int(v * S)
sans = lambda s, i=0: ImageFont.truetype(SANS, P(s), index=i)
mono = lambda s, i=0: ImageFont.truetype(MONO, P(s), index=i)

img = Image.new("RGB", (P(W), P(H)), PAPER)
d = ImageDraw.Draw(img)

# ---- left panel (ink) ----
LW = 470
d.rectangle([0, 0, P(LW), P(H)], fill=INK)
d.text((P(48), P(48)), "OKTO PULSE", font=mono(15, 1), fill=LIME)
d.text((P(48), P(150)), "pulse-", font=sans(64, 1), fill=PAPER)
d.text((P(48), P(220)), "benchmark", font=sans(64, 1), fill=PAPER)
d.text((P(48), P(318)), "Staged vs. direct agent edits", font=sans(17, 0), fill=MUTED)
d.text((P(48), P(342)), "SWE-bench Lite  /  pytest  /  n=10", font=mono(13, 0), fill=MUTED)

# ---- right panel: results table ----
x0, x1 = LW + 56, W - 56
cs, cd = x1 - 250, x1 - 70       # column right edges for staged / direct
d.text((P(x0), P(52)), "MODEL", font=mono(12, 1), fill=MUTED)
d.text((P(cs - 80), P(52)), "STAGED", font=mono(12, 1), fill=INK)
d.text((P(cd - 74), P(52)), "DIRECT", font=mono(12, 1), fill=MUTED)
d.line([P(x0), P(78), P(x1), P(78)], fill=INK, width=P(2))

rows = [
    ("qwen3.8-flash", "resolved, harness-graded", "10", "9", True),
    ("Qwen3.5-27B", "resolved, harness-graded", "10", "10", False),
    ("Qwen3.5-9B", "code change applied (not graded)", "10", "10", False),
]
for i, (name, sub, st, di, win) in enumerate(rows):
    y = 90 + i * 85
    d.text((P(x0), P(y + 8)), name, font=sans(24, 1), fill=INK)
    d.text((P(x0), P(y + 44)), sub, font=mono(11, 0), fill=MUTED)
    # staged number
    if win:
        d.rounded_rectangle([P(cs - 96), P(y + 4), P(cs + 22), P(y + 62)], P(10), fill=LIME)
    d.text((P(cs - 84), P(y + 6)), st, font=sans(48, 1), fill=INK)
    d.text((P(cs - 84 + 62), P(y + 36)), "/10", font=mono(14, 1), fill=INK)
    # direct number
    d.text((P(cd - 66), P(y + 6)), di, font=sans(48, 1), fill="#9a9a90")
    d.text((P(cd - 66 + (62 if len(di) == 2 else 33)), P(y + 36)), "/10", font=mono(14, 0), fill="#9a9a90")
    if i < 2:
        d.line([P(x0), P(y + 78), P(x1), P(y + 78)], fill=LINE, width=P(1))

d.text((P(x0), P(356)), "No LLM grading. Official swebench harness.", font=mono(11, 0), fill=MUTED)

os.makedirs("assets", exist_ok=True)
img.save("assets/pulse-benchmark-banner.png", optimize=True)
