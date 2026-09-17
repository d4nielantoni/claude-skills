# claude-skills

Custom [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for Claude, built from real work sessions. Each folder is a self-contained skill with its own `SKILL.md`.

## Skills

| Skill | What it does |
|---|---|
| [bambu-filament-optimizer](bambu-filament-optimizer/SKILL.md) | Tunes Bambu Studio print settings to use less filament without losing quality or strength, then re-slices to prove the savings. |

## bambu-filament-optimizer

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
cp -r claude-skills/bambu-filament-optimizer ~/.claude/skills/
```

**Claude.ai / Claude desktop:** zip the `bambu-filament-optimizer` folder and upload it in the Skills section of Claude's settings.

Then just ask something like *"this part is using too much filament, can you optimize the settings?"* with Bambu Studio open.

## License

[MIT](LICENSE)
