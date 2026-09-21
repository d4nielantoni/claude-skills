---
name: bambu-print-optimizer
description: "Tunes Bambu Studio (Bambu Lab A1 mini) print settings - walls, top/bottom, infill, supports - to spend less filament and time without losing quality, then re-slices to prove the savings. Use when the user wants to save filament, make a part lighter, cut the cost or print time of a part, or asks if a print can be made cheaper."
---

# Bambu Studio print optimizer

The goal is to cut filament where nobody sees it (the part's interior) and reinforce what gives quality and strength (walls, top, bottom, supports). Validate every change by re-slicing and comparing the numbers. An estimate made without slicing does not count as a result.

## 1. Accessing Bambu Studio

This skill assumes Claude can control the computer (computer use). Tool names vary by environment, so the notes below describe behavior and use Cowork's tool names only as examples. Tested with Bambu Studio on macOS, a Bambu Lab A1 mini, PLA and a 0.4 mm nozzle. The method carries over to other Bambu printers, but re-check every number by slicing.

- Request access to Bambu Studio. On macOS it is listed as **BambuStudio** (bundle `com.bambulab.bambu-studio`).
- Background app control (e.g. `computer_app_*` in Cowork) works for screenshots and simple clicks, but it often fails in this app: tab clicks don't register, fields don't accept Enter, and drags don't work. To edit settings, request full-screen control at the start.
- Apps that live in the notch / Dynamic Island area can block interactions near the top center of the screen, where Bambu Studio keeps its toolbar and gizmo panels. If a click there is refused or doesn't land, send that click through background app control instead (e.g. `computer_app_click`), which goes straight to Bambu Studio, or ask the user to hide the notch app for a moment.
- Don't save the project on your own. At the end, remind the user to save (Cmd+S on macOS).

## 2. Diagnose before changing anything

1. **Current slice result:** the "Slicing Result" panel (top right of the Preview tab) shows grams per filament, support, purge, total time and cost. Record these as "before". If the plate hasn't been sliced yet, slice it first.
2. **Part size and volume:** click the part in the 3D view (Prepare tab). The notification shows `Size` and `Volume`. A large, nearly solid part (volume close to its bounding box) spends most of its filament on infill, so that's where the savings are.
3. **Process settings (Global tab):** check Strength (walls, top/bottom layers, infill), Support, and Others (prime tower). Orange labels with an undo icon mark values changed from the preset.
4. **Per-object overrides:** switch to "Objects" and check whether the part already has its own settings (a lock icon next to the value and an icon on the part's row in the object list).
5. **Warnings:** a "floating cantilever" or floating-region warning means the part needs supports.

## 3. Route: which job is this?

The diagnosis tells you what is on the plate. The user's complaint tells you which job you are doing. Pick one before touching a setting: the three jobs use different settings, have different success signals, and only the first one uses the profile table.

| What the user says | Job | Success signal |
|---|---|---|
| "too much filament", "too heavy", "too expensive", "takes too long" | **A — Use less filament** (§4) | grams before → after |
| "the text doesn't show", "it disappears when I slice", fine relief missing | **B — Small text that vanishes** (§5) | that filament's **Model** grams leave `0.00 g` |
| "I don't have an AMS", "too many colour changes", a part looks like it is floating | **C — One filament change** (§6) | **Filament change times** in the Slicing Result |

One request can be two jobs — a plate can need B and C. Do them one at a time and re-slice in between, so you know which change caused which effect.

If the part is thin, flat or tiny, job A has almost nothing to give: there is barely any infill to cut. Say so plainly instead of running the profile table on it anyway.

## 4. Job A — Use less filament

*This section is job A. Skip it for jobs B and C — their settings are elsewhere and the profile table does not apply.*

If the user doesn't say what the part is for, use the **Balanced** profile and state that choice in your reply. By default, parts should not flex when someone squeezes them.

| Profile | Walls | Top | Bottom | Infill | When to use |
|---|---|---|---|---|---|
| **Balanced (default)** | 3 | 6 layers | 5 layers | Cubic 10% | Customer orders and parts that will be handled |
| Max savings | 3 | 6 layers | 3 layers | Support Cubic 10% | Decorative only, when the user explicitly asks for the lightest option |
| Functional | 3–4 | 6 layers | 5 layers | Gyroid or Cubic 15–20% | Parts that take load, snap fits, or impacts |

Measured reference on a 160 × 152 × 82 mm part (nearly solid, PLA, 0.4 nozzle, 0.20 mm layers):

| Configuration | Filament | Time |
|---|---|---|
| Original: Grid 15%, 2 walls, top 5, bottom 3 | 382 g | 9h11 |
| Max savings (Support Cubic 10%) | 230 g | 6h23 |
| Balanced with Gyroid 10% | 326 g | 9h04 |
| **Balanced with Cubic 10%** | **331 g** | **8h21** |

Why each choice matters, so you can explain it to the user and adapt it to other parts:
- **Infill** is almost all the weight of bulky parts. Support Cubic only densifies under top surfaces, so it saves a lot but leaves the side walls with no internal bracing. Cubic and Gyroid tie the walls together in every direction. Cubic prints faster than Gyroid at a similar weight.
- **Top:** with less infill, raise it to at least 6 layers (1.2 mm) so the surface doesn't sag between infill lines.
- **3 walls** keep the sides stiff and hide the infill pattern. They cost little compared to what the infill change saves.
- **A 5-layer bottom** avoids a thin base that flexes when pressed.
- **Supports:** keep them on (tree auto, 30°) when there are floating regions. They usually cost under 10 g.
- **Prime tower:** it can stay off when there are only a few color changes (purge stays under 1 g).
- **Layer height** barely changes filament use. Only touch it if the user asks for a shorter print time.
- **Small parts:** infill is a smaller share of the total, so the percentage savings are lower. Say so instead of promising the percentages seen on large parts.

## 5. Job B — Small text that vanishes when slicing

Embossed or engraved lettering below roughly 3 mm cap height often disappears in the slice even though it is clearly present in the model. The letter strokes are narrower than the nozzle, so the slicer generates no toolpath for them at all.

**Confirm it is this problem before changing anything.** In the "Slicing Result" panel, read the row for the text's filament. If **Model** shows `0.00 g` while **Purged** still shows grams, the printer is loading that colour and purging it without depositing any of it. That is proof the text produces no toolpath — it is not a colour or contrast problem. Use that same number as the pass/fail signal afterwards: when it leaves zero, the text is printing.

**The fix — apply all four together, as per-object overrides on the text part:**

| Setting | Where | Change |
|---|---|---|
| Wall generator | Quality | Classic → **Arachne** |
| Outer wall speed | Speed | **halve it** |
| Outer wall line width | Quality → Line width | **halve it** |
| Inner wall line width | Quality → Line width | **halve it** |

If you can't find "Wall generator", use the search icon next to the process preset name.

**Switch to Arachne first — the order matters.** Arachne varies the extrusion width along the path, so it can render a stroke thinner than one nominal line. Classic cannot: it only lays fixed-width loops, so halving the line width while still on Classic makes the slicer try to fit two thin perimeters into a stroke with room for only one, and the letters come out broken. Measured on a 2.9 mm-tall text part with Classic: 0.42/0.45 mm outer/inner wall gave readable letters, and dropping both to 0.35 mm broke the "d" and the "r". Halving the width is only safe once Arachne is generating the walls.

Halving the outer wall speed gives the thin extrusions time to bond. At full speed the fine strokes tend to lift or break up.

Keep these as per-object overrides so the rest of the plate keeps its normal speed and width — halved speed applied globally costs real print time for no benefit.

**When settings are not enough.** There is a floor: a 0.4 mm nozzle cannot draw a stroke thinner than about 0.35 mm, and no setting creates material below that. If the text is still ragged after the four changes, the fix is geometric — make the letters bolder or larger. Measure before promising anything: select the text part and read `Size` and `Volume` from the notification, and use `Volume` to compare variants, since it tracks how much ink the letters actually have. Bolder is not automatically better: past a point the counters (the holes in "e", "o", "d") close up and the word turns into a row of blobs, which reads worse than thin letters.

## 6. Job C — One filament change: align where parts start

Printing without an AMS makes every colour change a manual swap, so the goal is exactly one. That happens when every part of the second colour starts on the same layer, and nothing of the first colour prints above it.

**Read the number first.** "Filament change times" in the Slicing Result is the metric, and it is also the pass/fail signal at the end.

**Measure where each part starts.** Select the part, open the Move tool and read `Position Z`; read `Size Z` from the part notification. `Position Z` is the centre of the bounding box, so:

```
base = Position Z − (Size Z ÷ 2)
```

Compare the bases of the parts that share a colour. A gap smaller than one layer still costs changes: the lower part starts a layer earlier, and that layer ends up holding both colours.

**Do not compute this from the .3mf transforms.** It is tempting, since the component matrices sit right there in `Metadata/model_settings.config`, but that arithmetic disagreed with what the app reported and produced a confident, wrong diagnosis. Read the values from the app.

**The fix** is to set the offending part's `Position Z` so its base matches the others. When two parts have the same thickness, that means giving them the same `Position Z`.

**Relief sitting on top of another part is not a misalignment.** Text embossed on a plate can only start where the plate ends. That is exactly what produces a single change: one colour up to that height, one swap, the other colour above.

**Validate by looking, not only by the counter.** Drag the layer slider to the transition. The layer below should be entirely one colour, and every part of the second colour should appear together on the next one.

Measured examples:
- A wifi plaque: the white backdrop topped out at ~2.46 mm and the black parts started between 2.479 and 2.496 mm — all inside the same layer, so one change.
- A flag with a pole: the flag base sat at −0.085 mm and the pole base at −0.015 mm. Only 0.07 mm apart, but the layer height was 0.08 mm, so the pole lost the first layer and read as "floating". Setting both to `Position Z` 0.79 put them on the bed together.

## 7. Applying settings in the UI

- **Where to apply:**
  - Project with a single part: use the **Global** tab.
  - Project with several plates or parts that shouldn't change: use **Objects**. Select the part in the list and edit the values. A lock icon appears and the override applies only to that part, because the Global tab affects every plate.
- **Number fields:** triple-click the field, type the value, press Tab. Zoom in to confirm the value stuck (the label turns orange).
- **Scrolling the panel:** hover over the label column on the left side of the panel, never over the fields, because the mouse wheel changes numeric fields.
- **Infill pattern:** the dropdown (Sparse infill pattern) is long. Scroll the list and zoom in to find the item, since Support Cubic and Lightning are near the bottom.
- **Supports:** on the Support tab, check "Enable support" and confirm the type is tree(auto).

## 8. Validate and compare

1. Click **Slice plate** and wait 25–35 s for large parts.
2. Read the new "Slicing Result" and confirm the warnings are gone, especially floating-region ones.
3. When useful, drag the layer slider to the middle of the part to inspect the infill and walls.
4. When torn between two patterns, slice both and compare. It takes 30 s and beats guessing.

## 9. Reply to the user

Reply in the user's language, concisely:
- One sentence with the result (grams and time, before → after).
- A before/after table with filament, time and cost.
- A short list of what changed and why, including what was deliberately kept.
- Which profile was assumed and what changes if the part is decorative or functional.
- Real risks (where the part might flex) and Bambu Studio warnings, such as mesh errors.
- A reminder to save the project.

## Pitfalls (these already happened)

- **Stray keys in the 3D view:** Backspace or Delete removes the selected part, and number keys (0–6) change the camera. Only type when you're sure a text field has the cursor. If in doubt, click the field first.
- **Numeric fields in floating gizmos:** triple-clicking these grabs the underlying slider and jumps the value instead of selecting the text — a Boldness field went from 394 to 788 that way. What works: single-click the field, `Cmd+A`, type, then `Tab` or `Return`, and zoom in to confirm. With that method the Scale and Move fields do accept typed values.
- **Text tool is single-line:** pressing Enter in the text field closes the panel, and every letter typed after that lands in the 3D view as a keyboard shortcut (`r` opens Rotate, and so on). Pasting a string with a newline just strips it. To get a second line, duplicate the text part with `Cmd+C` / `Cmd+V` and move the copy with the Move tool's numeric Position fields.
- **The text tool creates instead of edits:** opening it while a non-text part is selected adds a brand new text part rather than editing the existing one. Select the text part first and confirm its name in the notification before opening the tool. If a stray one appears, select it, check its size in the notification, and delete it.
- **New text lands where you didn't ask:** with Mode set to "Surround surface", a new text placed on a narrow part wraps around it. Clicking elsewhere on the model does not move it. Duplicating an existing, correctly placed text part is more reliable than placing a new one.
- **Part name:** clicking the part's name in the list can open rename mode. Click elsewhere to exit, without pressing keys.
- **Global preset:** the user may switch projects or presets between requests. Re-run the diagnosis before assuming earlier changes still apply.
