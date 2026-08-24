# Testosterone Cypionate Verification Page

## Goal

Host one public mobile-friendly page for Testosterone Cypionate 250 mg/mL,
10 mL. A single QR code will open this page and provide access to three
original Janoshik verification reports.

## Page

Public path:

`pages/testosterone-cypionate-250mg-10ml/index.html`

Public URL:

`https://jorgitin02.github.io/public-images/pages/testosterone-cypionate-250mg-10ml/`

The page will contain:

- Product heading: `Testosterone Cypionate`
- Specification: `250 mg/mL · 10 mL`
- Three clearly labeled links to the supplied Janoshik verification pages
- A short statement that each link opens the original Janoshik report

The page will not copy, summarize, or modify report results. Janoshik remains
the source of truth.

## Links

1. `https://verify.janoshik.com/tests/171465-02_250mg_4PXARE612UR9`
2. `https://verify.janoshik.com/tests/171472-Testosterone_Cypionate_250mg_MCT_GCMS_E9WN8DMCRRYV`
3. `https://verify.janoshik.com/tests/165299-Testosterone_Cypionate_250mg_DQ5BDAMD1ZPW`

## QR And Registry

Generate:

`qr/testosterone-cypionate-250mg-10ml.png`

The QR will encode the public combined-page URL with a four-module quiet zone
and high error correction. Record both the QR destination URL and the hosted
QR image URL in `links.csv`.

## Verification

- Validate the HTML structure and all three exact outbound URLs.
- Confirm the generated QR decodes to the combined-page URL.
- Confirm GitHub Pages returns the page as HTML and the QR as PNG.
- Confirm the public page contains all three Janoshik links.
