# FLSF energy partitioning: data and code

Data and code for

> Mai, N. C., Y.-Y. Chen, S.-C. Chang, and M.-H. Lo: Surface Energy Partitioning in a Humid Subtropical
> Utility-Scale Solar Farm: Insights from Field Observations and Numerical Simulations.
> *Journal of Applied Meteorology and Climatology* (manuscript JAMC-D-26-0098).

The repository contains the half-hourly tower record of the Feng-Lin Sheng-Feng (FLSF) solar farm in
Hualien, Taiwan (1 January 2024 to 1 February 2026), the process-based land surface model (LSM), the two
machine-learning baselines (PCR and a one-dimensional CNN), and every script that produces the numbers,
tables and figures of the paper. All results can be rebuilt from `data/raw/`.

## Layout

| Folder | Content |
|---|---|
| `data/raw/` | `FLSF_ObservedData.csv` (half-hourly tower record), `panel_concrete_temperature.xlsx` (10-min back-panel, cavity-air and concrete-pile temperatures recorded by HOBO MX2303 loggers), `AllTemperature.xlsx` (hourly composite of Fig. A2; its front-panel series comes from a short operator campaign whose raw file is not part of this release, and the other series are rebuilt from the raw records by `analysis/record_coverage.py`), `radiosonde_FLSF_2025-10-15_1435LST.txt` (on-site radiosonde sounding inside the solar farm; times in the file are UTC) |
| `data/build_datasets.py` | builds the three derived datasets in `data/derived/` (see `docs/datasets.md`) |
| `flsf/` | model code: `config.py` (all constants), `physics.py` (energy balance and Newton–Raphson solver), `preprocessing.py` (quality control and surface ground heat flux), `calibration.py` (canopy resistance, diurnal correction, metrics, folds), `cnn.py` (NumPy CNN), `paths.py` |
| `calibration/` | fits of the albedo (Eq. 3), ground-heat coefficients g1–g3 (Eq. 5), concrete-storage coefficients c1–c3 (Eq. 6), and the roughness-multiplier sweep |
| `models/` | cross-validation (LSM, PCR, CNN), hold-out test, Bowen-ratio map and management scenarios |
| `analysis/` | observational statistics (closure, ground heat flux, Bowen ratio, peak duration, concrete depth), record coverage, porosity sensitivity, LSM diagnostics, parameter sensitivity |
| `figures/scripts/` | one script per figure; output in `figures/output/` |
| `results/` | all numerical results (JSON, CSV and NPZ) quoted in the paper |
| `docs/` | description of the derived datasets (`datasets.md`) |

## Status

Release v1.0.0 accompanies the second revision of the manuscript. Changes relative to the analyses of the
first revised manuscript are listed in `CHANGELOG.md`.

## Quick start

```bash
pip install -r requirements.txt          # Python 3.9 or newer
playwright install chromium              # only for rendering Fig. A3
python run_all.py                        # full rebuild; the CNN and the Bowen-ratio map take most of the time
python run_all.py --fast                 # reuse the saved CNN, Bowen-ratio-map and hold-out f_m-sweep results (about 10 min)
```

Tested with Python 3.10 (NumPy 2.2, pandas 2.3) and Python 3.13 (NumPy 2.5, pandas 3.0); a `--fast` rebuild in
the second setup reproduced every number in `results/` to within floating-point rounding. Each script can also
be run on its own from the repository root, for example
`python models/lsm_cv.py` or `python figures/scripts/fig06_closure.py`.

## Where each result comes from

| Paper item | Script | Result file |
|---|---|---|
| Datasets (N = 11,415; 9,841; 11,176; 15,363) | `data/build_datasets.py` | `data/derived/*.csv` |
| Eq. (3) albedo constants | `calibration/fit_albedo.py` | `results/calibration/albedo_fit.json` |
| Eq. (5) g1–g3 | `calibration/fit_ground_heat_flux.py` | `results/calibration/ground_heat_flux_fit.json` |
| Eq. (6) c1–c3 | `calibration/fit_concrete_storage.py` | `results/calibration/concrete_storage_fit.json` |
| fm | `calibration/select_roughness_multiplier.py` | `results/calibration/roughness_multiplier_sweep.json` |
| Table 3, Figs. 8 and 9, Section 3d; solver convergence (Section 3c) and calm-wind share (Section 2d) | `models/lsm_cv.py`, `models/pcr_cv.py`, `models/cnn_cv.py`, `analysis/lsm_diagnostics.py` | `results/lsm_cv/`, `results/pcr_cv/`, `results/cnn_cv/` |
| Table A2, Section 3e hold-out | `models/holdout_lsm.py`, `models/holdout_ml.py` | `results/holdout/` |
| Fig. 10 (Section 3f) | `models/bowen_map.py` | `results/bowen_map/` |
| Scenario percentages of Sections 3f and 4c (2.2, 3.4 and 5.4 %), Eq. A1 | `models/bowen_scenarios.py` | `results/bowen_scenarios/` (the `scenarios` block of `results/bowen_map/bowen_results.json` is a nearest-grid-point estimate and differs in the second decimal) |
| H_BL of Eq. A1 (parcel method on the sounding) | `analysis/boundary_layer_height.py` | `results/observational/boundary_layer_height.json` |
| Sections 2d, 3a–3c, Table 2, Figs. 2–7, A5, A6 | `analysis/observational_statistics.py`, `figures/scripts/` | `results/observational/` |
| Sections 2a and 2c (air temperature and precipitation of the site, daytime window, SWC range), Section 2d (diurnal amplitudes of the panel and concrete temperatures), Fig. 2 caption (seasonal precipitation), Table 4 note f, Fig. A2 periods | `analysis/record_coverage.py` | `results/observational/record_coverage.json` |
| Porosity φ = 0.44 and the sensitivity of the surface ground heat flux and closure to it | `analysis/porosity_sensitivity.py` | `results/observational/porosity_sensitivity.json` |
| Fig. A4 | `analysis/parameter_sensitivity.py` | `results/parameter_sensitivity/` |
| Section 4b (diurnal amplitude of the modeled ΔQc), Fig. 3 hourly albedo | `figures/scripts/fig09_diurnal_by_season.py`, `figures/scripts/fig03_albedo.py` | `results/figures/` |

## Figures and tables

| Item | Produced by | Output |
|---|---|---|
| Fig. 1 | map and site photographs (not computed; `figures/assets/`), copied by `figures/scripts/fig01_figA1_assets.py` | `figures/output/Fig01_StudyArea.png` |
| Fig. 2 | `figures/scripts/fig02_time_series.py` | `figures/output/Fig02_TimeSeries.png` |
| Fig. 3 | `figures/scripts/fig03_albedo.py` | `figures/output/Fig03_Diurnal_Albedo.png` |
| Fig. 4 | `figures/scripts/fig04_diurnal_energy_balance.py` | `figures/output/Fig04_Seasonal_Diurnal_EB.png` |
| Fig. 5 | `figures/scripts/fig05_bowen_diurnal.py` | `figures/output/Fig05_Diurnal_Bowen.png` |
| Fig. 6 | `figures/scripts/fig06_closure.py` | `figures/output/Fig06_EBC.png` |
| Fig. 7, Table 2 (u* columns) | `figures/scripts/fig07_friction_velocity.py` | `figures/output/Fig07_FrictionVelocity.png`, `results/observational/friction_velocity_table2.json` |
| Fig. 8 | `figures/scripts/fig08_lsm_performance.py` | `figures/output/Fig08_LSM_Performance.png` |
| Fig. 9 | `figures/scripts/fig09_diurnal_by_season.py` | `figures/output/Fig09_Diurnal_Composite_Seasonal.png` |
| Fig. 10 | `figures/scripts/fig10_bowen_map.py` | `figures/output/Fig10_Bowen_Sensitivity_Map.png` |
| Fig. A1 | site photographs (not computed; `figures/assets/`), copied by `figures/scripts/fig01_figA1_assets.py` | `figures/output/FigA1_SitePhotographs.png` |
| Fig. A2 | `figures/scripts/figA2_panel_concrete.py` | `figures/output/FigA2_PanelConcrete.png` |
| Fig. A3 | `figures/scripts/figA3_flowchart.html`, rendered by `figures/scripts/figA3_render.py` (needs Playwright; run by `run_all.py` when Playwright is installed); editable Word version from the same source by `figures/scripts/figA3_docx.py` (needs python-docx; run by `run_all.py`) | `figures/output/FigA3_ModelFlowchart.png`, `figures/output/FigA3_ModelFlowchart.docx` |
| Fig. A4 | `figures/scripts/figA4_parameter_sensitivity.py` | `figures/output/FigA4_ParamSensitivity.png` |
| Fig. A5 | `figures/scripts/figA5_conventional_closure.py` | `figures/output/FigA5_ConventionalEBC.png` |
| Fig. A6 | `figures/scripts/figA6_wind_rose.py` | `figures/output/FigA6_WindRose.png` |
| Fig. A7 | `figures/scripts/figA7_pcr_diagnostics.py` | `figures/output/FigA7_PCR_Diagnostics.png` |
| Table 1 (instruments), Table 4 (literature), Table A1 (symbols) | compiled by the authors (no computation) | – |
| Tables 2, 3 and A2 | see the table above | `results/` |

`python run_all.py` writes every figure of the paper (Figs. 1–10 and A1–A7) to `figures/output/`.
All figure scripts share one style (`figures/scripts/style.py`): fonts, season colors, line conventions
(observed values solid, modeled values dashed) and a resolution of 600 dpi.

## Notes

* The ground heat flux used everywhere is the storage-corrected surface flux
  G = G_plate + Cs(SWC) Δz dT_soil/dt, with Cs = (1 − φ)C_m + SWC·C_w + (φ − SWC)C_a and φ = 0.44 (Section 2d).
* R² of the models (Tables 3 and A2) is 1 − SSE/SST; R² of the closure regressions is the squared Pearson
  correlation.
* The CNN uses fixed random seeds (42 for the cross-validation, 1 to 5 for the hold-out test), so a rerun on the
  same machine repeats the results. Across machines, floating-point differences can change the early-stopping
  path of single folds; the cross-validated R² of Table 3 is reproduced to the second decimal, and RMSE, MAE,
  slope and bias can differ slightly.
* The friction velocity of Fig. 7 and Table 2 is estimated from the measured wind speed with the neutral
  logarithmic profile (`figures/scripts/fig07_friction_velocity.py`).
* The convective boundary-layer depth H_BL = 1,271 m of Eq. (A1) (`flsf/config.py`) is the parcel height for a
  surface excess of 0.5 K of the virtual potential temperature in the on-site radiosonde sounding of 15 October
  2025; `analysis/boundary_layer_height.py` gives the parcel heights for excesses of 0 to 0.5 K (1,128 to 1,271 m)
  and checks the value in `flsf/config.py`.
* Time stamps of the tower record mark the end of each 30-min averaging period. Daytime records have time stamps
  from 06:00 to 18:30 LST and the sun above the horizon at the middle of the period; gap-filled turbulent fluxes
  (PyFluxPro) are treated as missing (`flsf/preprocessing.py`; `docs/datasets.md`).
* The reference height of the logarithmic wind profile is the height of the wind measurement, z = 4.7 m.
* dRn/dt in Eqs. (5) and (6) is the half-hourly tendency of the measured net radiation on the continuous record,
  (Rn(t) − Rn(t − 30 min)) / 1800 s, computed before any record is screened (column `dRn_dt` of the datasets).
* The skill of G (Section 3d, Fig. 8) is listed with the cross-validated skill of H and LE, but G depends on the
  measured net radiation and the full-record coefficients g1–g3 only, so it does not change between folds; the
  hold-out test (Table A2) is its independent check.
* The canopy stress-function slopes in `flsf/config.py` were set once by the authors against the full record
  (binned residual analysis) and are not refitted by a script; the hold-out test bounds their effect.
* `data/raw/FLSF_ObservedData.csv` is the EddyPro/PyFluxPro output after the quality control of Section 2c; its
  turbulent fluxes are gap-filled, and the columns `Fh2o_EP` and `ET_EP` keep the EddyPro values, which identify
  the measured records.
* The plant's metered electricity record is proprietary to Star Shining Energy Co., Ltd. and is not included;
  the efficiency η = 0.11 used by the model is stated in `flsf/config.py`.

## License and citation

Code: MIT license (`LICENSE`). Data in `data/raw/` and `data/derived/`, results in `results/` and figures in
`figures/output/`: Creative Commons Attribution 4.0 (`LICENSE-DATA`).
Please cite the paper and this release (v1.0.0; `CITATION.cff`).
