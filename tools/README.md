# Build tools

Python scripts that generate the PDA's UI layouts and textures, plus a few one-off asset utilities. The mod in `../PDA` already contains their output. Run them only when you change the UI.

**Needs:** Python 3.10+ and Pillow 11 or newer (`pip install pillow`); Pillow writes the DXT5 data used for the map icons. The fonts are bundled in `fonts/` (Inter and DejaVu, open licences included).

Run everything from the repository root. Order matters, because the layout reads `bezel_rect.json`, which `make_textures.py` writes:

```bash
python tools/make_textures.py   # icons, brand, bezel, reworked frame, map .paa icons  -> PDA/gui
python tools/gen_compass.py     # FI_Compass.layout, FI_SOS_Prompt.layout              -> PDA/gui/os
python tools/gen_layout.py      # FI_OS_Shell.layout (the whole PDA screen)            -> PDA/gui/os
python tools/preview.py         # optional: approximate render  -> tools/build/preview.png
```

| File | What it does |
|---|---|
| `make_textures.py` | Draws every UI icon and the brand art, reworks `pdaframe.edds` from `frame/pdaframe_original.edds`, writes the rounded screen bezel and the map-mark `.paa` icons |
| `gen_layout.py` | The main PDA layout. All geometry is in reference pixels of the 1067×554 screen and converted to the fractions DayZ expects |
| `gen_compass.py` | The compass HUD and S.O.S prompt layouts |
| `preview.py` | Renders a layout over the frame to check it without starting the game |
| `rap.py` | Decodes binarized configs / `.rvmat` files back to text |
| `repath_odol.py` | Rewrites texture and material paths inside binarized `.p3d` models (used for the v8.6 prefix move) |
| `bezel_rect.json` | Screen opening in frame pixels, written by `make_textures.py`, read by `gen_layout.py` |
| `art/wolf_source.png` | Source of the wolf emblem |
| `frame/pdaframe_original.edds` | Untouched frame art; the mod's `pdaframe.edds` is generated from it |
| `model_src_original/` | Models and materials as they were before the v8.6 re-path, kept for reference |

Generated files go to `tools/build/`, which is not part of the mod or the repository.
