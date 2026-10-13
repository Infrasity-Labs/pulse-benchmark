"""Render assets/banner.png (2400x800; drawn at 2x)."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H, S = 1200, 400, 2
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"  # idx: 0 regular, 1 bold, 10 medium
INK, MUTED, RULE = "#111827", "#6b7280", "#d9d6cf"
BG, ACCENT, TRACK, DIRECT = "#f6f4ef", "#0f7b5f", "#e6e3db", "#9ca3af"


def font(size, idx=0):
    return ImageFont.truetype(FONT, size * S, index=idx)


img = Image.new("RGB", (W * S, H * S), BG)
d = ImageDraw.Draw(img)
P = lambda v: int(v * S)

# left column
d.rectangle([P(0), P(0), P(10), P(H)], fill=ACCENT)
d.text((P(60), P(58)), "OKTO PULSE BENCHMARKS", font=font(15, 1), fill=ACCENT)
d.text((P(60), P(92)), "Staged vs. direct", font=font(50, 1), fill=INK)
d.text((P(60), P(150)), "agent edits", font=font(50, 1), fill=INK)
d.text((P(60), P(240)), "Paired SWE-bench Lite runs,", font=font(19, 0), fill=MUTED)
d.text((P(60), P(266)), "pytest slice, n = 10 tasks.", font=font(19, 0), fill=MUTED)
d.rectangle([P(60), P(318), P(76), P(326)], fill=ACCENT)
d.text((P(86), P(311)), "Staged (Okto Pulse)", font=font(14, 0), fill=INK)
d.rectangle([P(240), P(318), P(256), P(326)], fill=DIRECT)
d.text((P(266), P(311)), "Direct", font=font(14, 0), fill=INK)

# divider
d.line([P(560), P(50), P(560), P(350)], fill=RULE, width=P(1))

# right column: one block per model
rows = [
    ("qwen3.8-flash", "Resolved, harness-graded", 10, 9),
    ("Qwen3.5-27B", "Resolved, harness-graded", 10, 10),
    ("Qwen3.5-9B", "Code change applied, not graded", 10, 10),
]
x, bw = 600, 440
for i, (name, sub, st, di) in enumerate(rows):
    y = 50 + i * 102
    d.text((P(x), P(y)), name, font=font(20, 1), fill=INK)
    d.text((P(x + 175), P(y + 4)), sub, font=font(14, 0), fill=MUTED)
    for j, (val, col) in enumerate([(st, ACCENT), (di, DIRECT)]):
        by = y + 36 + j * 24
        d.rounded_rectangle([P(x), P(by), P(x + bw), P(by + 14)], P(7), fill=TRACK)
        d.rounded_rectangle([P(x), P(by), P(x + bw * val / 10), P(by + 14)], P(7), fill=col)
        d.text((P(x + bw + 16), P(by - 4)), f"{val}/10", font=font(18, 1), fill=INK if j == 0 else MUTED)

os.makedirs("assets", exist_ok=True)
img.save("assets/banner.png", optimize=True)
