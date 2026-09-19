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

Proven end-to-end 2026-09-19 with three templates: `retat10-glm`,
`hgh24-glm`, `reta30-glm`. Division of labor: all design happens in this
repo where it is deterministic and reviewable; the NIIMBOT GUI is used only
for import, save, and rename. Never author label content by clicking in the
app — its Flutter UI ignores semantic writes and text/position editing is
unreliable.

Read section 6 (environment hazards) BEFORE any GUI work. Three failure
classes each burned hours on 2026-09-19 before being understood; every one
is now documented here with its working path. Do not rediscover them.

## Harness compatibility (read before GUI work)

This skill is shared by ZCode and OpenCode sessions in this repo. Steps 0-4
and 7 (QR, design, render/verify, links.csv, commit) are harness-neutral.
Steps 5-6 name ZCode computer-use tools; under OpenCode use the mapping
below — the workflow and its failure modes are identical.

Identify your harness by the tools you actually have: if `open_application`
and `perform_action` exist, you are on ZCode; if the action tools are named
`perform_secondary_action` / `type_text` / `click`, you are on OpenCode.

| Action | ZCode (`computer-use:computer-use`) | OpenCode (`open-computer-use` MCP) |
|---|---|---|
| Permissions | `request_access` | `open-computer-use doctor` (shell, once) |
| Launch / activate app | `open_application {bundle_id, activate:true}` | shell `open -a NIIMBOT` (no app tool) |
| Observe state | `get_app_state` | `get_app_state` (AX tree + image) |
| Element click | `left_click` | `click {element_index}` |
| Double-click | `double_click` | `click {element_index, click_count:2}` |
| Named AX action | `perform_action {action:"AX..."}` | `perform_secondary_action {action:"AX..."}` |
| Set field value | `set_value` | `set_value` (same) |
| Type text | `type` | `type_text` |
| Key chord | `press_key` | `press_key` (same) |
| Screenshot | `screenshot` | `get_app_state` image (no separate tool) |
| Wait | `wait` | shell `sleep` |
| Zoom | `zoom` | none — prefer element indexes over pixels |

ZCode loads the `computer-use:computer-use` skill first; OpenCode has no
computer-use skill — its tools come straight from the `open-computer-use`
MCP, so skip that load step. OpenCode has no app-launch tool: launch and
activate NIIMBOT with `open -a NIIMBOT` and confirm with `get_app_state`.
Whether that warms the Flutter AX tree as reliably as ZCode's
`open_application activate=true` is not yet re-verified (flagged again in
step 5).

## 0. Inputs to collect

Ask the user only for what is missing; never invent values:

- Compound name and vial fill amount (e.g. retatrutide 30 mg)
- Real/actual mass or measured content — take it from the COA when the user
  points at one (e.g. HGH: "8.35 mg / 25.05 IU actual"; reta: net content
  36.06 mg). Nominal amount goes in the title/line 1; actuals labeled
  "ACTUAL" or "REAL MASS".
- Vial size and diluent volume/type ONLY if the user provides them (the
  10 mg label had "3 ML VIAL • 2 ML WATER"; the 24 IU and 30 mg labels omit
  the line entirely). Omit rather than guess.
- Test date: print the COA's own analysis/report date as MM/DD/YYYY — the
  QR points at that exact COA, so TESTED should match it. (Do not default
  to today's date when a COA date exists.)
- Reconstitution date: requested BLANK — print "RECON" plus an underline
  rect and let the user hand-write it after mixing.
- Batch/cap identifier (e.g. "BLUE CAP") when the COA or user names one —
  it distinguishes lookalike vials.
- QR target: if `coa/` has a COA for this compound and `qr/` has its QR,
  embed that existing QR — never generate a replacement unless none exists
  or the user asks. A new QR points at the final GitHub Pages asset URL and
  gets registered in `links.csv` (see step 3).

Content policy (repo AGENTS.md): no purity, expiration, laboratory, or
regulatory claims that the user did not provide. Print only the values
given. Purity stays on the COA behind the QR; it is not printed on the
label.

## 1. QR: reuse, or generate and decode-verify

No QR tooling is installed system-wide. One-off venv (fast, no repo noise):

```bash
python3 -m venv /tmp/qrtools
/tmp/qrtools/bin/pip install -q segno zxing-cpp pillow
```

Generate (EC level Q suits small curved vials; 4-module quiet zone; repo
convention is 1024x1024 PNG, same basename as its target) and
DECODE-ASSERT the saved file — generation alone is not verification:

```bash
/tmp/qrtools/bin/python - <<'EOF'
import segno, zxingcpp
from PIL import Image
url = "https://jorgitin02.github.io/public-images/coa/<coa-file>.pdf"
qr = segno.make(url, error='q')
qr.save("/tmp/qr.png", scale=1024 // (qr.version * 4 + 17 + 8), border=4)
img = Image.open("/tmp/qr.png").convert("L").resize((1024, 1024), Image.NEAREST)
img.save("qr/<basename>.png")
bars = zxingcpp.read_barcodes(Image.open("qr/<basename>.png"))
assert bars and bars[0].text == url, "QR decode mismatch"
print("OK")
EOF
```

(zxingcpp Barcode objects expose `.text` / `.format`; there is no
`error_correction_level` attribute.)

Verify the target public URL is live and returns the right media type
(`curl -sI`) before pointing a QR at it.

## 2. Design

Work in `labels/`. Copy the template and fill it in:

```bash
cp .agents/skills/niimbot-vial-label/assets/label-template-40x20.svg \
   labels/<compound>-<amount>-vial-label-<initials>-<yyyy-mm-dd>.svg
```

Naming: lowercase ASCII, hyphens, `<subject>-<amount>-vial-label-<who>-<date>`.
`<who>` is a short tag for who/what produced it (the user may ask for a
model name — e.g. `glm`). Never overwrite an existing file; use a new date
or tag.

CRITICAL — embed the QR as a base64 data URI. librsvg 2.62+ (rsvg-convert
on this Mac) SILENTLY drops `<image xlink:href="../qr/name.png">`: any file
reference escaping the SVG's directory renders blank with exit 0, and a
bare filename resolves into labels/ where no QR lives. Either way the PNG
and PDF come out with NO QR and no error. This killed the first retat10
render and the first two hgh/reta renders. Inject the data URI while
writing the SVG:

```bash
b64=$(base64 -i qr/<basename>.png | tr -d '\n')
# xlink:href="data:image/png;base64,$b64"
# and keep a comment in the SVG naming the source qr/ asset
```

Layout facts baked into the template (all units mm, viewBox 0 0 40 20):

- Text zone x = 1.7 to ~27.0. Fact lines are Helvetica Neue Condensed Bold
  2.0mm; keep each MEASURED width <= ~25.5mm. A line that clears the 26.9mm
  limit by a few hundredths of a mm (26.81 happened today) is a failure in
  waiting across renderers — rebalance the words between lines instead of
  squeezing (e.g. move the batch/cap color to line 1 and leave the date
  alone on line 2). Verify numerically in step 3.
- Title: 4.6mm, baseline y=5.6, rule below. Do not enlarge: at 4.9mm the
  title's arms reach into the QR column.
- RECON line (y=16.7): "RECON" text + underline rect x=8.6 y=16.75
  w=14.4 h=0.25 — blank for handwriting.
- QR: 11.2x11.2 at x=27.3, y=4.0 (data URI), "COA" caption under it.
- Black (#000) on white only. Thermal printing: white = no ink. Bold,
  high-contrast, no fine decorative lines, one simple border.

## 3. Render and verify

```bash
.agents/skills/niimbot-vial-label/scripts/build_and_check.sh \
  labels/<file>.svg
```

The script renders the print PNG (640x320, 16 px/mm) and an exact-40x20mm
page PDF next to the SVG, then checks: PNG is 640x320; PDF rasterizes to
~113x57 at 72dpi (= 40x20mm; note `magick identify` lies about rsvg PDF
page size — do not use it for this check); per-band ink extents
(`scripts/measure_ink.py`) so text overflow into the QR gutter is caught
numerically; and QR-zone ink — a blank QR now FAILS the build instead of
passing silently.

Then Read the PNG visually — nothing clipped, QR intact, text hierarchy
reads like a professional lab label — and decode the QR from the rendered
PNG at print resolution:

```bash
/tmp/qrtools/bin/python - <<'EOF'
import zxingcpp
from PIL import Image
img = Image.open("labels/<file>.png").convert("L")
qr = img.crop((436, 64, 616, 244)).resize((716, 716), Image.NEAREST)
bars = zxingcpp.read_barcodes(qr)
assert bars and bars[0].text == "<expected public url>"
print("OK")
EOF
```

If a fact line does not fit: shorten/rebalance the wording; failing that,
drop ALL fact lines to 1.9mm together, never one alone. Re-run until clean.

## 4. Register in links.csv

Append one label row (match header order exactly):

```csv
<id>,label,labels/<file>.svg,,<qr path>,<qr public url>,labels/<file>.png,<yyyy-mm-dd>,"<one-line description; QR destination; PDF twin note>"
```

`id` equals the SVG basename. `public_url` stays empty unless the label
itself is being hosted. Reference the embedded QR's path and its hosted URL
so the destination stays recoverable. If a NEW QR was generated, also fill
the COA row's `qr_path`/`qr_public_url` columns (update that row in place).
`qr_public_url` values 404 until the next push — record them anyway.

## 5. Import into NIIMBOT (computer use)

**ZCode:** load the `computer-use:computer-use` skill first.
**OpenCode:** skip that; drive the `open-computer-use` MCP directly and
launch/activate the app with shell `open -a NIIMBOT`. See the harness table
above for every tool-name difference.

Derive every pixel coordinate from the LATEST screenshot raster — never
reuse stale coordinates. After every action: wait 2–4s (`wait` on ZCode,
shell `sleep` on OpenCode), re-observe, verify. The app is Flutter-based and
only exposes its accessibility tree after
`open_application {"bundle_id": "com.niimbot.print", activate=true}` warms
it (OpenCode equivalent: `open -a NIIMBOT`; not yet re-verified — if the
tree returns ~8 generic elements, re-run `get_app_state` once the app is
frontmost and prefer element indexes from the fresh state).

Launch and editor:

1. Launch/activate. If an "Updates Available" dialog blocks the app, click
   **Do not update** (never update mid-task). While the screen is locked
   this dialog cannot be dismissed — see section 6.
2. If the editor is not open: click **Create a label**, then **Create with
   this label** on the EL\*20-345Laser Silver card (40x20mm, matches the
   stock). Never open or edit the user's existing templates (hgh24-glm,
   reta30-glm, retat10-glm, hgh25iu, kpv10, ss31-10mg, tirze10, ...).

Image import — semantic AX ONLY (OpenCode: use `perform_secondary_action`
where this says `perform_action`; `set_value` is the same name):

3. Click the **Image** tool (left toolbar). The native macOS open panel
   appears. Do NOT send Cmd+Shift+G — the Go-to-Folder sheet never opens
   (the chord is accepted-but-dropped, or refused as foreground_required).
   Do NOT click rows — element clicks, coordinate clicks, and event-strategy
   clicks are ALL dropped by this panel; Open stays disabled forever.
4. `set_value` the panel's **textfield Search** element (native AppKit —
   a11y writes DO work here) to the exact label PNG filename. Then
   `perform_action AXConfirm` on it. Wait ~3s: the panel switches to
   "Searching This Mac" and lists the file.
5. `perform_action AXOpen` on the result row's **cell** element. The panel
   closes and the image auto-fits the canvas; the Image Style panel opens.
   (The receipt may say `possibly_sent` with `attribute_unsupported` — it
   still works. Verify with a screenshot that the whole label is placed,
   nothing clipped, before saving.)

Save and rename:

6. Click **Save**. It saves silently under the auto tab name
   (`Templates-<timestamp>`); there is no name dialog. Verify on Home →
   Recent: a new card with the correct thumbnail must exist before
   renaming.
7. Reopen the template from Recent. **Double-click the tab title** —
   ZCode: the dedicated `double_click` tool; OpenCode: `click` with
   `click_count: 2`. Two separate single clicks do NOT register as a
   double-click — and the **Rename** dialog opens with
   the current name pre-selected. Send app-scoped `type` (OpenCode:
   `type_text`) with the new short
   name (keyboard reaches focused fields while the app is frontmost; send
   `cmd+a` first if the text is not selected), then click **Done**.
8. Final verify: Home → Recent shows the renamed template with the correct
   thumbnail. Report the saved name to the user.

Known dead ends — each one cost real time on 2026-09-19, do not retry:

- **There is no pencil icon next to the tab title.** The small icon there
  is the ✕ close — AXPress on it closes the editor and kicks you to Home.
- The ⌄ dropdown next to "+" has no rename (Select new template / New
  blank label / Select new label paper / Open local label). Single clicks
  or AXPress on the tab title do nothing.
- Cmd+Shift+G / typed paths / clicking result rows inside the file panel
  (see step 3–5 for the working path).
- AXPress on in-app Flutter content tools that need a dialog response,
  `set_value` on in-app Flutter text fields (writes never reach the app —
  native AppKit fields are fine), Cmd+S, typed text with stale focus.
- Do not click **Print** unless the user asks AND the app shows a connected
  printer — while it says "Unconnected" printing is impossible anyway.

## 6. Environment hazards

Tool names below are ZCode's; if you are on OpenCode, translate them via the
harness table above.

**Locked screen (mid-task killer).** When the Mac locks, `loginwindow`
takes front and everything degrades at once: `open_application
activate=true` fails with "never became foreground"; app-scoped chords and
clicks return accepted-but-never-executed; AX trees fill with ~1000 ghost
menu elements (zero-size bounds, duplicates of every app's menus); the
`screenshot` tool errors on screen recording. Detect:

```bash
lsappinfo info -only name "$(lsappinfo front)"   # contains "loginwindow"?
```

Test THIS command's output — `lsappinfo front` alone prints the ASN line
first, which has no name and makes naive greps false-positive "unlocked".
Recover: poll until unlocked; then, if the app's AX tree is still polluted
or windows are ghosts, quit and relaunch the app (`osascript -e 'quit app
"NIIMBOT"'` may print "User canceled" yet still quit — confirm with
`pgrep`; note System Events itself has no assistive access, so plain
`quit app` is the route). Templates saved before the wedge persist.
Relaunches may show the update dialog again — dismiss it.

**Screenshots.** The full-screen `screenshot` tool can fail with a stale
screen-recording helper error while `get_app_state include_screenshot=true`
(app-scoped) keeps working — prefer app-scoped captures for verification
regardless; they show exactly the app you are driving.

**Input reliability ranking** (use top-down; never trust a receipt alone —
`action_sent=true` means "possibly happened", always re-observe):

1. Semantic AX actions: AXPress / set_value / AXConfirm / AXOpen.
2. App-scoped `type` into a genuinely focused field while frontmost.
3. Dedicated `double_click` (the only thing that opens Rename).
4. Raw event clicks/keys — often accepted-but-dropped; last resort only.

**Zoom/coordinate mapping.** When clicking by pixel inside a native panel
captured as part of an app-window screenshot, coordinates can land in the
wrong space. `zoom` into the panel region first and click within the zoomed
frame — or skip coordinates entirely via the AX path in section 5.

## 7. Committing

Repo rule: commit and push only when the user explicitly asks. When they
do, include the SVG/PNG/PDF trio and the links.csv rows (new QR + COA-row
update first if a QR was generated).

Base directory for this skill: /Users/jorgitin/projects/print_farm/.agents/skills/niimbot-vial-label
