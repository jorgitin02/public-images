#!/usr/bin/env python3
"""Report rightmost ink per 1mm band in a label PNG's text zone, and
verify the QR actually rendered.

Catches the two common failures:
1. A fact line running into the QR gutter.
2. A blank QR: librsvg 2.62+ silently drops image hrefs that escape the
   SVG's directory (e.g. ../qr/name.png) — the render exits 0 with an
   empty QR zone. The QR box must contain real ink.

Assumes the 640x320 render (16 px/mm) produced by build_and_check.sh
and the standard template geometry: text zone starts at x=2.0mm, QR
occupies x 27.3-38.5mm, y 4.0-15.2mm.

Exit code 1 if any band's ink crosses into the gutter (right edge of a
text row beyond 26.9mm) or the QR box is blank, else 0.
"""
import sys
from PIL import Image

PX_PER_MM = 16.0
X0_MM = 2.0          # left edge of the text zone (inside the border)
QR_START_MM = 27.3   # left edge of the QR column
QR_TOP_MM = 4.0      # top edge of the QR: rows above it may overhang right
LIMIT_MM = 26.9      # text must stay left of this wherever the QR exists
EDGE_MARGIN_MM = 0.15  # skip the QR's anti-aliased edge pixels
QR_SIDE_MM = 11.2    # QR box is QR_START..QR_START+QR_SIDE, QR_TOP..+QR_SIDE
QR_INK_MIN = 3000    # dark px inside the QR box; a real QR has >10k


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} labels/<name>.png", file=sys.stderr)
        return 2

    img = Image.open(sys.argv[1]).convert("L")
    w, h = img.size
    px = img.load()
    mm = PX_PER_MM

    worst = 0.0
    overflow = False
    for band_top in range(1, 19):  # interior vertical range, 1mm..18mm
        y0, y1 = int(band_top * mm), int((band_top + 1) * mm)
        x_hi = min(w - 1, int((QR_START_MM - EDGE_MARGIN_MM) * mm))
        x_lo = int(X0_MM * mm)
        right = 0.0
        for y in range(y0, min(y1, h)):
            for x in range(x_hi, x_lo, -1):
                if px[x, y] < 128:
                    right_mm = x / mm
                    if right_mm > right:
                        right = right_mm
                    break
        if right <= X0_MM:
            continue
        # Rows fully above the QR have no gutter limit (the title may
        # overhang right of QR_START as long as it stays above QR_TOP).
        limited = (band_top + 1) > QR_TOP_MM
        flagged = limited and right > LIMIT_MM
        print(f"y {band_top:>2}-{band_top + 1:<2} mm: right ink {right:5.2f} mm"
              + ("  << TOO WIDE" if flagged else ""))
        if flagged:
            overflow = True
        elif limited:
            worst = max(worst, right)

    print(f"text zone right limit: {LIMIT_MM} mm (QR starts {QR_START_MM} mm)")
    if overflow:
        print("FAIL: text overflows into the QR gutter — shorten the line "
              "or reduce all fact-line font sizes together.")
        return 1
    print(f"ok: widest text ink {worst:.2f} mm")

    # QR presence check (inset 2px to skip the box's anti-aliased edges).
    qx0, qy0 = int(QR_START_MM * mm) + 2, int(QR_TOP_MM * mm) + 2
    qx1, qy1 = int((QR_START_MM + QR_SIDE_MM) * mm) - 2, \
               int((QR_TOP_MM + QR_SIDE_MM) * mm) - 2
    qr_ink = sum(1 for y in range(qy0, qy1) for x in range(qx0, qx1)
                 if px[x, y] < 128)
    print(f"QR zone ink: {qr_ink} px (minimum {QR_INK_MIN})")
    if qr_ink < QR_INK_MIN:
        print("FAIL: QR zone is blank — the SVG's QR image did not render. "
              "librsvg 2.62+ silently drops file hrefs that escape the "
              "SVG's directory (../qr/x.png). Embed the QR as a base64 "
              "data URI instead.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
