"""
Rebuild every dataset, result and figure of the paper from data/raw/.

    python run_all.py           full rebuild
    python run_all.py --fast    reuse the saved CNN, Bowen-ratio-map and hold-out f_m-sweep results (the slow steps)

Steps run in order; the script stops at the first failure.
"""
import os, sys, subprocess, time, importlib.util

ROOT = os.path.dirname(os.path.abspath(__file__))
FAST = '--fast' in sys.argv
SEASONS = ['MAM', 'JJA', 'SON', 'DJF']

STEPS = [
    ('datasets', ['data/build_datasets.py']),
    ('albedo fit (Eq. 3)', ['calibration/fit_albedo.py']),
    ('ground-heat fit (Eq. 5)', ['calibration/fit_ground_heat_flux.py']),
    ('concrete-storage fit (Eq. 6)', ['calibration/fit_concrete_storage.py']),
    ('roughness-multiplier sweep', ['calibration/select_roughness_multiplier.py']),
    ('LSM cross-validation', ['models/lsm_cv.py']),
    ('PCR cross-validation', ['models/pcr_cv.py']),
]
if not FAST:
    STEPS += [('CNN cross-validation', ['models/cnn_cv.py']),
              ('LSM hold-out, fm sweep', ['models/holdout_lsm.py', 'sweep'])]
STEPS += [
    ('LSM hold-out', ['models/holdout_lsm.py']),
    ('PCR hold-out', ['models/holdout_ml.py', 'pcr']),
]
if not FAST:
    STEPS += [('CNN hold-out, seed %d' % s, ['models/holdout_ml.py', 'cnn', str(s)]) for s in range(1, 6)]
    STEPS += [('Bowen-ratio map, %s' % s, ['models/bowen_map.py', '--season', s]) for s in SEASONS]
STEPS += [
    ('CNN hold-out summary', ['models/holdout_ml.py', 'summary']),
    ('Bowen-ratio map, merge', ['models/bowen_map.py', '--merge']),
    ('management scenarios', ['models/bowen_scenarios.py']),
    ('observational statistics', ['analysis/observational_statistics.py']),
    ('record coverage', ['analysis/record_coverage.py']),
    ('boundary-layer depth (Eq. A1)', ['analysis/boundary_layer_height.py']),
    ('porosity sensitivity', ['analysis/porosity_sensitivity.py']),
    ('LSM diagnostics', ['analysis/lsm_diagnostics.py']),
    ('parameter sensitivity', ['analysis/parameter_sensitivity.py']),
]
FIGS = ['fig01_figA1_assets', 'fig02_time_series', 'fig03_albedo', 'fig04_diurnal_energy_balance', 'fig05_bowen_diurnal', 'fig06_closure',
        'fig07_friction_velocity', 'fig08_lsm_performance', 'fig09_diurnal_by_season', 'fig10_bowen_map',
        'figA2_panel_concrete', 'figA4_parameter_sensitivity', 'figA5_conventional_closure', 'figA6_wind_rose',
        'figA7_pcr_diagnostics']
STEPS += [('figure %s' % f, ['figures/scripts/%s.py' % f]) for f in FIGS]
STEPS += [('figure figA3_docx (editable Word version of Fig. A3)', ['figures/scripts/figA3_docx.py'])]
if importlib.util.find_spec('playwright'):   # Fig. A3 is rendered from HTML with headless Chromium (playwright)
    STEPS += [('figure figA3_render', ['figures/scripts/figA3_render.py'])]
    A3_NOTE = ''
else:
    A3_NOTE = (' Fig. A3 PNG not rendered: pip install playwright && playwright install chromium, then'
               ' python figures/scripts/figA3_render.py.')


def main():
    t0 = time.time()
    for name, cmd in STEPS:
        print('\n=== %s' % name, flush=True)
        t = time.time()
        r = subprocess.run([sys.executable] + cmd, cwd=ROOT)
        if r.returncode != 0:
            sys.exit('failed: %s' % ' '.join(cmd))
        print('    (%.0f s)' % (time.time() - t), flush=True)
    print('\nall steps done in %.1f min.%s' % ((time.time() - t0) / 60, A3_NOTE))


if __name__ == '__main__':
    main()
