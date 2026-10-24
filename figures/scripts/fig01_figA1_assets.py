"""Figs. 1 and A1: copy the two non-computed images (map and site photographs, figures/assets/) to
figures/output/, so that run_all.py produces every figure of the paper. The files are copied unchanged."""
import os, shutil
import style as S

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
for name in ('Fig01_StudyArea.png', 'FigA1_SitePhotographs.png'):
    shutil.copyfile(os.path.join(ASSETS, name), S.paths.fig(name))
    print('->', 'figures/output/' + name)
