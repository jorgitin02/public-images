# Public Images and Label Assets

## Purpose

This repository hosts public images, COAs, QR codes, and printable label
artwork. GitHub Pages serves files directly from the `main` branch at:

`https://jorgitin02.github.io/public-images/`

Assume uploaded files are public and permanent.

## Repository Layout

- `coa/`: COA images and other supporting test documents.
- `qr/`: Generated QR images that point to hosted assets.
- `labels/`: Editable and print-ready label artwork.
- `links.csv`: Source of truth connecting assets, public URLs, QR files, and
  label files.

Create a directory only when it has a real file to contain. Do not add empty
placeholder directories.

## Naming

Use lowercase ASCII filenames with hyphens and a meaningful stable identifier:

`<subject>-<amount>-<document>-<yyyy-mm-dd>.<ext>`

Examples:

- `coa/retatrutide-30mg-coa-2026-07-16.png`
- `qr/retatrutide-30mg-coa-2026-07-16.png`
- `labels/retatrutide-30mg-40x20mm.svg`

Do not silently overwrite an existing asset. Add a revision suffix or a new
date when the contents change.

## Public URLs and QR Codes

Every hosted asset or generated QR must have a row in `links.csv`.

- Use the GitHub Pages URL, not a GitHub `blob` or temporary raw URL.
- Point QR codes to the final direct asset URL unless explicitly asked for a
  webpage.
- Save generated QR artwork in `qr/` with the same basename as its target.
- Record both the QR destination and the hosted QR image URL in `links.csv`.
- Keep a four-module quiet zone and use error correction suitable for small
  printed labels.
- Verify the public URL returns the intended media type.
- Decode or otherwise validate every generated QR before considering it ready.
- Keep the registry entry when a label references a QR so the destination is
  recoverable without scanning the printed label.

## Label Defaults

Unless a task specifies otherwise, labels target a NIIMBOT M2 using black
thermal printing on transparent 40 x 20 mm stock.

- Design at the exact physical size and preserve a print-ready source file.
- Prefer bold, high-contrast text and avoid fine decorative lines.
- Keep QR codes large enough to scan after the label is applied to a curved
  vial.
- Save editable artwork and any exported print image in `labels/`.
- Record the related QR or public URL in `links.csv`.
- Do not add unverified purity, amount, expiration, laboratory, or regulatory
  claims.

## Upload Workflow

1. Inspect the source file for readability and accidental private information.
2. Copy it into the appropriate directory using the naming convention.
3. Add or update its row in `links.csv`.
4. Generate and save a QR when requested.
5. Verify the local asset, public URL, media type, and QR destination.
6. Commit and push only when the user explicitly asks, except when publishing
   an asset is itself the explicit task.

Do not alter, enhance, crop, or redact a source COA unless explicitly asked.
Preserve the submitted file exactly when it is intended as evidence.
