---
name: niimbot-vial-label
description: >
  Design a compound vial label outside the NIIMBOT app at exact 40x20mm,
  verify it, register it in links.csv, and import it into the NIIMBOT macOS
  app as a saved template via computer use. Use whenever the user asks to
  make, design, generate, update, or import a vial label, compound label,
  peptide label, or NIIMBOT template in this repo — including phrases like
  "make a label for <compound>", "new label", "import to NIIMBOT/printer",
  or "print a label for <compound>". Do not design labels by clicking in the
  app; the import pipeline is the only reliable path.
---

# NIIMBOT vial label: design, verify, register, import

Proven end-to-end 2026-09-19 (retatrutide-10mg label, saved in-app as
`retat10-glm`). Division of labor: all design happens in this repo where it
is deterministic and reviewable; the NIIMBOT GUI is used only for import,
save, and rename. Never author label content by clicking in the app — its
Flutter UI ignores semantic writes and text/position editing is unreliable.

## 0. Inputs to collect

Ask the user only for what is missing; never invent values:

- Compound name and vial fill amount (e.g. retatrutide 10 mg)
- Real/actual mass if the user provides one (e.g. 11.71 mg)
- Vial size (e.g. 3 ml) and diluent volume/type (e.g. 2 ml water)
- Test date (default: today, printed as MM/DD/YYYY)
- QR target: if `coa/` already has a COA for this compound and `qr/` has its
  QR, embed that existing QR — never generate a replacement QR unless none
  exists or the user asks. New QRs must be registered in `links.csv` and
  point to the final GitHub Pages asset URL.

Content policy (from repo AGENTS.md): no purity, expiration, laboratory, or
regulatory claims that the user did not provide. Print only the values given.

## 1. Design

Work in `labels/`. Copy the template and edit it:

```bash
cp .agents/skills/niimbot-vial-label/assets/label-template-40x20.svg \
   labels/<compound>-<amount>-vial-label-<initials>-<yyyy-mm-dd>.svg
```

Naming: lowercase ASCII, hyphens, `<subject>-<amount>-vial-label-<who>-<date>`.
`<who>` is a short tag for who/what produced it (the user may ask for a model
name — e.g. `glm`). Never overwrite an existing file; use a new date or tag.

Layout facts baked into the template (all units are mm, viewBox 0 0 40 20):

- Text zone: x = 1.7 to ~27.0. Anything wider than ~25.3mm starting at x=1.7
  collides with the QR — this is the failure that actually happens. Fact
  lines are Helvetica Neue Condensed Bold 2.0mm; keep each under ~25mm and
  verify numerically (step 2).
- Title: Helvetica Neue Condensed Bold 4.6mm, baseline y=5.6, rule below.
  Do not enlarge it: at 4.9mm the title's arms reach into the QR column.
- QR: 11.2x11.2 at x=27.3, y=4.0, referencing `../qr/<qr-file>.png`
  (relative path — resolves at render time, keeps the SVG portable).
- Black (#000) on white only. Thermal printing: white = no ink. Bold,
  high-contrast, no fine decorative lines, one simple border.

Write real content over the placeholders, then go to step 2.

## 2. Render and verify

```bash
.agents/skills/niimbot-vial-label/scripts/build_and_check.sh \
  labels/<file>.svg
```

The script renders the print PNG (640x320, 16 px/mm) and an exact-40x20mm
page PDF next to the SVG, then checks: PNG is 640x320, PDF rasterizes to
~113x57 at 72dpi (= 40x20mm; note `magick identify` lies about rsvg PDF
page size — do not use it for this check), and per-band ink extents via
`scripts/measure_ink.py` (reports the rightmost ink in the text zone so
overflow into the QR gutter is caught numerically).

Then Read the PNG visually — confirm nothing is clipped, the QR is intact,
and the text hierarchy reads like a professional lab label. If a fact line
does not fit, shorten the wording or drop the font to 1.9mm (all three fact
lines together, never one alone). Re-run until clean.

## 3. Register in links.csv

Append one row (match header order exactly):

```csv
<id>,label,labels/<file>.svg,,<existing qr path>,<qr public url>,labels/<file>.png,<yyyy-mm-dd>,"<one-line description; QR destination; PDF twin note>"
```

`id` equals the SVG basename. `public_url` stays empty unless the label
itself is being hosted. Reference the embedded QR's path and its hosted URL
so the destination stays recoverable. The retatrutide row
(`retatrutide-10mg-3ml-vial-label-glm-2026-09-19`) is the worked example.

## 4. Import into NIIMBOT (computer use)

Load the `computer-use:computer-use` skill first, then follow this flow.
Derive every pixel coordinate from the LATEST screenshot raster — never
reuse stale coordinates. After every action: `wait` 2–4s, re-observe, verify.
The app is Flutter-based and only exposes its accessibility tree after
`open_application(activate=true)` warms it; before that the tree is ~8
generic elements.

1. Launch/activate: `open_application {"bundle_id": "com.niimbot.print",
   activate=true}`. The window may live on a secondary display — fine.
2. If the editor is not open: click **Create a label**, then
   **Create with this label** on the EL40\*20-345Laser Silver card (40x20mm,
   matches the stock). Never open or edit the user's existing templates
   (hgh25iu, kpv10, tirze10, ...).
3. Click the **Image** tool (left toolbar, 2nd icon). A native macOS open
   panel appears — this panel is fully accessible and is the reliable path.
4. In the panel: send Cmd+Shift+G (scoped to the panel window). If it
   refuses with `foreground_required`, re-run `open_application` with
   activate=true plus the panel's pid/window_id, observe, retry. Type the
   full absolute path of the label PNG into the focused PathTextField
   (a11y set works — it is a native AppKit field), press Return, then click
   **Open** (native button — AXPress works).
5. The app auto-fits the image to the canvas and opens an Image Style panel
   (contrast/dither preview). Screenshot-verify the whole label is placed,
   nothing clipped.
6. Click **Save**. It saves silently under the auto tab name
   (`Templates-<timestamp>`); there is no name dialog. If the click shows a
   not-allowed cursor, the save may still have happened — verify on Home →
   Recent before retrying.
7. Rename (required so the template is identifiable): open the template
   from Recent, click the **pencil icon** next to the tab title, in the
   Rename dialog the current name is pre-selected — send app-scoped
   `type` with the new short name (typing works ONLY into genuinely focused
   fields; keep names short, e.g. `retat10-glm`), click **Done**.
8. Final verify: Home → Recent shows the renamed template with the correct
   thumbnail. Report the saved name to the user.

Do not click **Print** unless the user asks and the app shows a connected
printer — while it says "Unconnected" printing is impossible anyway.
Known dead ends (do not retry): AXPress on in-app Flutter buttons,
`set_value` on in-app text fields (writes never reach the app), Cmd+S (no
effect), typed text with stale focus (lands nowhere).

## 5. Committing

Repo rule: commit and push only when the user explicitly asks. When they
do, include the SVG/PNG/PDF trio and the links.csv row (and the new QR +
COA row first if a QR was generated for this label).
