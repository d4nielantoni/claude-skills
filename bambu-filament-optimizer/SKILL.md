---
name: bambu-filament-optimizer
description: "Tunes Bambu Studio (Bambu Lab A1 mini) settings to use less filament without losing quality. Use for saving filament, lighter parts, or cutting print cost/time."
---

# Bambu Studio filament optimizer

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

## 3. Pick the profile

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

## 4. Apply

- **Where to apply:**
  - Project with a single part: use the **Global** tab.
  - Project with several plates or parts that shouldn't change: use **Objects**. Select the part in the list and edit the values. A lock icon appears and the override applies only to that part, because the Global tab affects every plate.
- **Number fields:** triple-click the field, type the value, press Tab. Zoom in to confirm the value stuck (the label turns orange).
- **Scrolling the panel:** hover over the label column on the left side of the panel, never over the fields, because the mouse wheel changes numeric fields.
- **Infill pattern:** the dropdown (Sparse infill pattern) is long. Scroll the list and zoom in to find the item, since Support Cubic and Lightning are near the bottom.
- **Supports:** on the Support tab, check "Enable support" and confirm the type is tree(auto).

## 5. Validate and compare

1. Click **Slice plate** and wait 25–35 s for large parts.
2. Read the new "Slicing Result" and confirm the warnings are gone, especially floating-region ones.
3. When useful, drag the layer slider to the middle of the part to inspect the infill and walls.
4. When torn between two patterns, slice both and compare. It takes 30 s and beats guessing.

## 6. Reply to the user

Reply in the user's language, concisely:
- One sentence with the result (grams and time, before → after).
- A before/after table with filament, time and cost.
- A short list of what changed and why, including what was deliberately kept.
- Which profile was assumed and what changes if the part is decorative or functional.
- Real risks (where the part might flex) and Bambu Studio warnings, such as mesh errors.
- A reminder to save the project.

## Pitfalls (these already happened)

- **Stray keys in the 3D view:** Backspace or Delete removes the selected part, and number keys (0–6) change the camera. Only type when you're sure a text field has the cursor. If in doubt, click the field first.
- **Scale gizmo fields:** the floating fields of the Scale tool don't apply values typed through automation. Don't rely on them. If you need to scale, tell the user or find another way before typing.
- **Part name:** clicking the part's name in the list can open rename mode. Click elsewhere to exit, without pressing keys.
- **Global preset:** the user may switch projects or presets between requests. Re-run the diagnosis before assuming earlier changes still apply.
