# claude-skills

Custom [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for Claude, built from real work sessions. Each folder is a self-contained skill with its own `SKILL.md`.

## Skills

| Skill | What it does |
|---|---|
| [bambu-print-optimizer](bambu-print-optimizer/SKILL.md) | Tunes Bambu Studio print settings to use less filament without losing quality or strength, then re-slices to prove the savings. |
| [tiktok-shop-launcher](tiktok-shop-launcher/SKILL.md) | Turns MakerWorld/Printables model links into live TikTok Shop listings: real measurements, Google Flow ad photos and videos, captioned posting videos, listing texts and Seller Center submission. |

## bambu-print-optimizer

Claude drives Bambu Studio through computer use: it reads the current slice result, checks the part's size and settings, picks a profile, applies it (globally or per object), re-slices and reports before/after numbers.

Measured on a 160 × 152 × 82 mm, nearly solid PLA part (Bambu Lab A1 mini, 0.4 mm nozzle, 0.20 mm layers):

| Configuration | Filament | Print time |
|---|---|---|
| Original (Grid 15%, 2 walls) | 382 g | 9h11 |
| **Balanced** (Cubic 10%, 3 walls, 6 top / 5 bottom layers) | **331 g** | **8h21** |
| Max savings (Support Cubic 10%, decorative only) | 230 g | 6h23 |

Savings depend on the part: bulky, solid parts gain the most, small parts gain less.

**Requirements**

- Claude with computer use (tested in Claude Cowork on macOS)
- Bambu Studio installed and open
- Tested on a Bambu Lab A1 mini with PLA; other Bambu printers should work, but re-check the numbers by slicing

## Installation

**Claude Code:** copy the skill folder into your skills directory:

```bash
git clone https://github.com/d4nielantoni/claude-skills.git
cp -r claude-skills/bambu-print-optimizer ~/.claude/skills/
```

**Claude.ai / Claude desktop:** zip the `bambu-print-optimizer` folder and upload it in the Skills section of Claude's settings.

Then just ask something like *"this part is using too much filament, can you optimize the settings?"* with Bambu Studio open.

## tiktok-shop-launcher

Claude drives Chrome (MakerWorld, Google Flow and TikTok Seller Center) plus a few Python/ffmpeg scripts to launch 3D-printed products on TikTok Shop Brasil, one product at a time:

1. Reads the model page and measures the real size from the linked print profile's 3MF (or STL).
2. Generates 7 ad photos per product in Google Flow (white background, 3/4, detail, in use, dimensions, scale, gift) from the user's own prompt templates, in a separate Flow project and chat session per product so results don't bleed between products. Prompts never mention 3D printing and always ask for a clean, burr-free finish.
3. Generates a short showcase video (Veo 3.1 Lite), checks it frame by frame, and builds a 16–22 s 1080×1920 posting video with captions.
4. Writes the title, description, caption and hashtags, then fills TikTok Seller Center's single-product form (photos, category, colour variations, price, shipping) and submits it.

Content-policy refusals are never worked around: the product gets a photo-only video instead.

**Requirements**

- Claude with the Claude in Chrome extension, logged in to MakerWorld, Google Flow and TikTok Seller Center (Brazil)
- Python 3 with Pillow and numpy, and ffmpeg
- Google Flow daily credits for videos (about 5 Veo 3.1 Lite videos per day); photos are free

**Installation**

```bash
cp -r claude-skills/tiktok-shop-launcher ~/.claude/skills/
```

**Claude.ai / Claude desktop:** zip the `tiktok-shop-launcher` folder and upload it in the Skills section of Claude's settings (browser control is still required).

Then ask something like *"aqui estão os links dos modelos, crie as fotos e vídeos e suba no TikTok Shop"*.

## License

[MIT](LICENSE)
