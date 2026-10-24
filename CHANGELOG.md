# Changelog

## v1.0.0 (release accompanying the second revision of JAMC-D-26-0098)

First public release. All datasets, results and figures of the paper are rebuilt from `data/raw/` by
`run_all.py`.

### Differences from the analyses of the first revised manuscript

1. **Soil heat capacity.** The storage correction of the ground heat flux uses the three-phase form
   Cs = (1 − φ)C_m + SWC·C_w + (φ − SWC)C_a with φ = 0.44 (de Vries 1963). The earlier form,
   Cs = (1.94 + 4.18·SWC) × 10⁶ J m⁻³ K⁻¹, omitted the solid volume fraction. The coefficients g1–g3 of
   Eq. (5) are refitted (`calibration/fit_ground_heat_flux.py`).
2. **Ground heat flux in the closure analysis.** Figs. 2, 4, 6 and A5 and Table 2 use the storage-corrected
   surface ground heat flux, as the model does. With the heat-flux-plate signal the conventional closure
   slope is 0.672; with the surface flux it is 0.732.
3. **Albedo constants.** α_noon and Δα of Eq. (3) are fitted to the CNR4 albedo record
   (0.098 and 0.0057, `calibration/fit_albedo.py`), in place of the previously prescribed values of 0.115
   and 0.02.
4. **Concrete storage.** The effective depth d_c = 0.04 m and the sensitivity of the closure to it are
   reported (`analysis/observational_statistics.py`, `concrete_depth`).
5. **Model runs.** Cross-validation, Bowen-ratio map, management scenarios and parameter sensitivity are
   rerun with items 1 to 3. The full-record sweep of the array-roughness multiplier is flat around the value
   used (`results/calibration/roughness_multiplier_sweep.json`), and the training-year sweep of the hold-out
   test selects the same value.
6. **Independent hold-out test** (new): `models/holdout_lsm.py`, `models/holdout_ml.py` (Table A2).
7. **Record coverage** (new): `analysis/record_coverage.py` documents the daytime window (time stamps
   06:00 to 18:30 LST), the soil-water range, the periods of the Fig. A2 series and the panel
   air-temperature contrast of Table 4 (note f), and also the air temperature and precipitation of 2024 and 2025
   (Section 2a, Fig. 2 caption) and the diurnal amplitudes of the panel and concrete temperatures (Section 2d).
8. **Reference height of the wind profile.** z is now the height of the wind measurement, 4.7 m (previously
   10 m). z enters the neutral aerodynamic resistance only through a constant factor, so the array-roughness
   multiplier is rescaled from 1.1 to 1.57 (1.1 × 1.425) and the swept values from 0.9–1.4 to 1.28–2.00; the
   modeled fluxes and skill scores are unchanged. The friction velocity of Fig. 7 and Table 2 rises by 24 %,
   and the elasticities for z0m and d in Fig. A4 change slightly (H: z0m 0.025 to 0.037, d 0.001 to 0.003; with the final data, z0m 0.055 and d 0.005).
9. **Radiosonde sounding** (new): `data/raw/radiosonde_FLSF_2025-10-15_1435LST.txt` and
   `analysis/boundary_layer_height.py` (convective boundary-layer depth H_BL of Eq. A1, parcel method).
10. **Solver diagnostics** (new): `analysis/lsm_diagnostics.py` reports the energy-balance residual left by the
   Newton–Raphson solver (99.0 % of the records within 0.1 W m⁻²) and the share of calm-wind records
   (2.0 %) for which the wind speed is set to 2.5 m s⁻¹.
11. **Net radiation, Eq. (2).** The downwelling longwave flux enters Eq. (2) without the emissivity factor,
   Rn = (1 − α)Fsd + Fld − εσTs⁴ (`flsf/config.py`, `RN_EMISSIVITY = False`; also used by `models/bowen_map.py`).
   The analyses of the first revision applied the emissivity to it (εFld). Cross-validation, hold-out test,
   Bowen-ratio map, management scenarios, diagnostics, parameter sensitivity and Figs. 8, 9, 10 and A4 are rerun,
   and the Fig. A3 flowchart gives the new equation, base canopy resistances and hold-out skill.
   The array-roughness sweeps still select f_m = 1.57 on the training year and are flat between 1.43 and 1.57 on
   the full record. Panel (d) of Fig. A4 shows that the fluxes now depend on the assumed emissivity (H bias from
   +16.9 to −4.8 W m⁻² for ε = 0.90 to 0.99, with the final data). `analysis/lsm_diagnostics.py` also reports the share of records
   whose canopy resistance reaches its upper limit (Section 3f).
12. **Tendency of the net radiation, Eqs. (5) and (6).** dRn/dt is the half-hourly tendency of the measured net
   radiation on the continuous record, computed before the screening (`preprocessing.rn_tendency`, column
   `dRn_dt`). The earlier code took the difference from the previous retained record of the same day, so for
   8.8 % of the modeling records the tendency either spanned a screening gap or was zero (first record of each day;
   15.9 % of the modeling dataset of item 14).
   g1–g3 are refitted, and every LSM result, the
   Bowen-ratio map, the scenarios, the closure statistics and Figs. 6, 8, 9, 10, A3 and A4 are rebuilt; c1–c3 do
   not change (they were already fitted with the continuous tendency).
13. **Final check.** `analysis/observational_statistics.py` also reports the calendar-month mean Bowen ratios and the
   summer-midday (JJA, 10:00–15:00 LST) ratio of the mean fluxes (Section 3c; note g of Table 4), and the
   correlation of daily SWC with Rn and the partial correlations of H, LE and G with SWC at fixed Rn (Section 3a).
   Figs. 10, A2, A6 and A7 are redrawn with clearer labels (contour labels inside the frame, legend names of Fig. A2,
   radial labels of Fig. A6 in an empty sector, the overlapping RH and SWC labels of Fig. A7); their data do not
   change, and no other result changes.
14. **Data selection.** (a) Gap-filled turbulent fluxes are no longer used as observations: a record is measured
   when the EddyPro water-vapor flux (`Fh2o_EP`) exists and LE agrees with it (`preprocessing.flux_measured`);
   3,940 of the 15,363 daytime records had gap-filled fluxes. (b) The double-difference spike test is formed from
   three consecutive half-hours of the continuous record (`preprocessing.spike_flags`); it was applied to the
   daytime series and compared the first record of each day with the last record of the previous day. (c) Daytime
   requires the sun above the horizon at the middle of the averaging period (`preprocessing.sun_up`) instead of
   Fsd > 0 W m⁻², which admitted 1,329 dark records (pyranometer offset). (d) The time stamps of the tower record
   mark the end of the 30-min averaging period (EddyPro); the 10-min HOBO records are averaged into 30-min bins
   labeled the same way (`calibration/fit_concrete_storage.py`, `analysis/record_coverage.py`, Fig. A2); c1–c3 of
   Eq. (6) are refitted (0.0483, 76 s, −4.85 W m⁻²). (e) H_BL of Eq. (A1) is the parcel height for a surface excess
   of 0.5 K, 1,271 m (`analysis/boundary_layer_height.py` checks `flsf/config.py`). Datasets: daytime record 11,415,
   FC dataset 9,841, modeling dataset 11,176 records. Δα, g1–g3 and c1–c3 are refitted and every result and figure
   is rebuilt; f_m = 1.57 is kept (the training-year sweep of the hold-out test selects it; the full-record sweep is
   flat between 1.43 and 1.57). The rainfall row of Fig. 9 shows all daytime half-hours
   (`results/figures/fig09_rainfall.json`).
15. **Fig. 3.** The albedo axis spans 0.08 to 0.17 (the data range from 0.086 to 0.158), and the legend has two columns.
16. **All figures from one command.** `run_all.py` also writes Figs. 1 and A1 (map and photographs, copied from
   `figures/assets/`), the editable Word version of Fig. A3 and, when Playwright is installed, the Fig. A3 PNG.
17. **Figure layout.** Fig. 8: a bias that rounds to zero is written "0.00" (panels d and f). Fig. A4: the
   x-axes of panels (a)–(c) extend to 1.3 times the largest elasticity, so that the value labels stay inside the
   frame, and the legend of panel (d) no longer covers the points at ε = 0.97 and 0.99. Fig. A7: the y-axis of
   panel (e) extends to 1.0, so that the R² labels of JJA (0.87) and SON (0.86) are visible. No data or result
   changes (`figures/scripts/fig08_lsm_performance.py`, `figA4_parameter_sensitivity.py`,
   `figA7_pcr_diagnostics.py`).

| Quantity | First revision | This release |
|---|---|---|
| LSM H R² / RMSE (cross-validation) | 0.89 / 35.3 W m⁻² | 0.91 / 33.5 W m⁻² |
| LSM LE R² / RMSE (cross-validation) | 0.66 / 33.3 W m⁻² | 0.66 / 34.7 W m⁻² |
| LSM G R² / RMSE (cross-validation) | 0.80 / 19.7 W m⁻² | 0.82 / 15.6 W m⁻² |
| Conventional / augmented closure slope | 0.662 / 0.839 | 0.732 / 0.945 |
| Annual β reduction, albedo / SWC / combined scenario | 2.1 / 3.8 / 5.8 % | 2.2 / 3.4 / 5.4 % |
