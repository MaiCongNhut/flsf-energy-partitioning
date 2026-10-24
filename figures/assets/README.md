# Figure assets that are not computed

| File | Figure | Content and origin |
|---|---|---|
| `Fig01_StudyArea.png` | Fig. 1 | Location map of the FLSF solar farm and site photographs, prepared by the authors (map made with GIS software; photographs taken at the site). |
| `FigA1_SitePhotographs.png` | Fig. A1 | Photographs of the FLSF solar farm and the instruments, taken by the authors. |

These two images contain no computed data. `figures/scripts/fig01_figA1_assets.py` copies them, unchanged, to
`figures/output/` so that `python run_all.py` produces every figure of the paper (Figs. 1–10 and A1–A7) in one
folder. They are the images placed in the manuscript (pixel for pixel).
