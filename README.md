# public-images

Public, permanent hosting for certificate-of-analysis (COA) documents and
the QR codes that point at them, plus the source artwork for vial labels
printed on a NIIMBOT M2 (40 x 20 mm black thermal on transparent stock).

GitHub Pages serves everything on `main` directly:

`https://jorgitin02.github.io/public-images/`

**Everything pushed to `main` is public and effectively permanent.** Assume
anything committed can be scanned from a printed label years from now.

## Layout

| Path | Purpose |
|---|---|
| `coa/` | COA images and PDFs, byte-exact as received. Never edited, cropped, or redacted. |
| `qr/` | QR images, one per hosted asset, pointing to the final Pages URL of that asset. |
| `labels/` | Vial label source artwork (SVG master + rendered PNG + exact-size PDF twin). |
| `index.html` | COA dashboard — the landing page QRs can link to, listing hosted COAs by product. |
| `links.csv` | Source of truth connecting every asset, public URL, QR, and label. If it is not in `links.csv`, it does not exist. |
| `AGENTS.md` | Standing rules for coding agents working in this repo. |
| `.agents/skills/niimbot-vial-label/` | Skill that walks an agent through the full label design -> verify -> register -> import workflow. |

## links.csv columns

| Column | Meaning |
|---|---|
| `id` | Stable identifier; basename of the primary asset. |
| `type` | `coa`, `label`, `page`, ... |
| `source_path` | Repo path of the hosted or source file. |
| `public_url` | Absolute Pages URL once hosted (empty if not hosted). |
| `qr_path` | QR image in `qr/` that references this asset (empty if none). |
| `qr_public_url` | Hosted URL of the QR image itself. |
| `label_path` | Rendered label file that embeds the QR (label rows only). |
| `added_on` | ISO date added. |
| `notes` | Free text: verification numbers, QR destination, provenance. |

## Workflow A — host a COA

1. Inspect the source file for readability and accidental private
   information. Preserve it byte-exact — COAs are evidence.
2. Copy into `coa/` using
   `<subject>-<amount>-<document>-<yyyy-mm-dd>.<ext>` (lowercase, hyphens).
3. Generate a QR pointing at the **final Pages URL** (never a blob or raw
   URL), save it in `qr/` with the same basename, and add rows for both to
   `links.csv`.
4. Verify before considering it done: the public URL returns HTTP 200 with
   the intended media type, and the QR decodes to that URL.
5. Commit to `main` to publish. Commit and push only when asked, or when
   publishing is the task.

## Workflow B — create a vial label

Do not design labels by clicking in the NIIMBOT app; its editor cannot be
reliably automated and hand-built labels drift. The reliable pipeline is:
design here, verify, register, then import the finished image.

Full step-by-step: `.agents/skills/niimbot-vial-label/SKILL.md`. Summary:

1. Copy the 40x20mm template from the skill's `assets/`, fill in
   user-verified values only (no invented purity, expiration, or lab
   claims), embed the compound's existing `qr/` asset if one exists.
2. Render with `scripts/build_and_check.sh` (PNG for import + exact-size
   PDF) and verify no text overflow plus a visual pass.
3. Register the label in `links.csv`, referencing the embedded QR.
4. Import into the NIIMBOT macOS app via computer use (Image tool -> native
   file picker -> auto-fit -> Save -> rename), and confirm it appears in
   the app's Recent list.
