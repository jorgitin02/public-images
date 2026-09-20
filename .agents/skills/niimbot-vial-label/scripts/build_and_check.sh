#!/usr/bin/env bash
# Render a 40x20mm label SVG into the print PNG + exact-size PDF pair and
# verify output geometry. Usage:
#   build_and_check.sh labels/<name>.svg
#
# Outputs are written next to the SVG. The SVG must live in labels/ so its
# relative ../qr/ references resolve at render time.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 labels/<name>.svg" >&2
  exit 2
fi

SVG="$1"
DIR="$(cd "$(dirname "$SVG")" && pwd)"
BASE="$(basename "${SVG%.svg}")"
HERE="$(cd "$(dirname "$0")" && pwd)"

command -v rsvg-convert >/dev/null || { echo "rsvg-convert not found (brew install librsvg)" >&2; exit 1; }

PNG="$DIR/$BASE.png"
PDF="$DIR/$BASE.pdf"

rsvg-convert -w 640 -h 320 --background-color=white "$SVG" -o "$PNG"
rsvg-convert -f pdf --page-width 40mm --page-height 20mm --background-color=white "$SVG" -o "$PDF"

# PNG must be exactly 640x320 (16 px/mm).
PNG_DIM="$(sips -g pixelWidth -g pixelHeight "$PNG" | awk '/pixel/{print $2}' | paste -sd x -)"
if [ "$PNG_DIM" != "640x320" ]; then
  echo "FAIL: PNG is ${PNG_DIM}, expected 640x320" >&2
  exit 1
fi
echo "ok: PNG 640x320 (16 px/mm) -> $PNG"

# PDF page check: rasterize page 1 at 72 dpi; 40x20mm = 113x57 px.
# Do NOT use `magick identify` on the PDF here — it reports a ghostscript
# default canvas size, not the real page box.
TMP_PDF_PNG="$(mktemp -t pdfcheck).png"
sips -s format png "$PDF" --out "$TMP_PDF_PNG" >/dev/null
PDF_DIM="$(sips -g pixelWidth -g pixelHeight "$TMP_PDF_PNG" | awk '/pixel/{print $2}' | paste -sd x -)"
rm -f "$TMP_PDF_PNG"
case "$PDF_DIM" in
  112x56|112x57|113x56|113x57|114x57|114x58)
    echo "ok: PDF page is 40x20mm -> $PDF" ;;
  *)
    echo "FAIL: PDF rasterized at 72dpi to ${PDF_DIM}, expected ~113x57 (40x20mm)" >&2
    exit 1 ;;
esac

# Ink extents + QR presence. Labels with no real <image> element (intentional
# QR-less personal labels) are checked full-width with --no-qr instead.
if python3 -c 'import sys,xml.etree.ElementTree as ET
sys.exit(0 if any(e.tag.endswith("image") for e in ET.parse(sys.argv[1]).iter()) else 1)' "$SVG"; then
  python3 "$HERE/measure_ink.py" "$PNG"
else
  python3 "$HERE/measure_ink.py" --no-qr "$PNG"
fi
