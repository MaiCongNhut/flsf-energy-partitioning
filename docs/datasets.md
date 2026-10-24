# Datasets

All datasets are built by `data/build_datasets.py` from `data/raw/FLSF_ObservedData.csv`
(half-hourly, 1 January 2024 to 1 February 2026, 36,624 records; missing values coded −9999).
This file is the output of EddyPro v7.0.9 and PyFluxPro v3.4 after the quality control of Section 2c of the
paper. Its time stamps mark the end of each 30-min averaging period. PyFluxPro fills the gaps of the turbulent
fluxes; the EddyPro values are kept in `Fh2o_EP` and `ET_EP`, so a record counts as measured when `Fh2o_EP` exists
and LE agrees with it (`preprocessing.flux_measured`). Gap-filled values are treated as missing. The code of this
repository applies the modeling screening on top of the file.

| Step | Records | Used for |
|---|---|---|
| Time stamps 06:00–18:30 LST after the commissioning period (from 1 May 2024) | 16,692 | – |
| … with the sun above the horizon at the middle of the averaging period (1,329 removed) | 15,363 | CNN input series (`cnn_daytime_series.csv`, with the flag `QC_bad` for gap-filled or screened-out targets) |
| … with measured, not gap-filled, turbulent fluxes (3,940 removed) | 11,423 | – |
| … with all six model drivers present (Fsd, Fld, Ta, RH, Ws, SWC): daytime record | 11,415 | `daytime_record.csv` |
| … with Fsd > 50 W m⁻²: flux-characterization (FC) dataset | 9,841 | Figs. 3, 4, 6, 7, A5, A6; Table 2; closure statistics |
| FC records with LE > 20 W m⁻² | 9,349 | Bowen ratio (Section 3c) and Fig. 5 |
| Modeling dataset: daytime records after the modeling screening (physical limits; double-difference spike test on H, LE and G formed from three consecutive half-hours of the continuous record, with per-season thresholds; implausible midday records; 32 dew records kept) | 11,176 | LSM and PCR calibration and evaluation, Figs. 8, 9, A4, A7; Table 3 |
| Modeling dataset with Fsd > 50 W m⁻² | 9,607 | albedo fit (Eq. 3), Bowen-ratio map and scenarios |
| CNN windows scored in cross-validation (24 consecutive daytime records, windows across fold boundaries and flagged targets removed) | 10,746 | Table 3 (CNN) |
| Hold-out split of the modeling dataset: training 1 May 2024–30 April 2025 / test 1 May 2025–1 February 2026 | 6,326 / 4,850 | Table A2 |

Screening counts of the modeling dataset (`results/lsm_cv/metrics.json`, field `qc`): physical limits on LE 2,
spikes H 133, LE 39, G 73 (overlapping), implausible midday records 7; 239 records removed in total (a record
flagged by more than one test is counted once; dew records are exempt), and 8 further records with a missing
driver or flux, leaving 11,176.

## Columns added to the raw record

| Column | Definition |
|---|---|
| `SWC` | mean of the two 10-cm probes, Sws_10cma and Sws_10cmb (m³ m⁻³) |
| `Cs` | soil volumetric heat capacity, (1 − φ)C_m + SWC·C_w + (φ − SWC)C_a, φ = 0.44 (J m⁻³ K⁻¹) |
| `dTs_dt` | tendency of the 10-cm soil temperature `Ts` between consecutive records of the same day (K s⁻¹) |
| `Fg_surface` (`Gobs` in the modeling dataset) | storage-corrected surface ground heat flux, Fg + Cs·0.10·dTs_dt (W m⁻²) |
| `dRn_dt` | half-hourly tendency of the measured net radiation `Fn` on the continuous record, (Fn(t) − Fn(t − 30 min)) / 1800 s (W m⁻² s⁻¹); dRn/dt of Eqs. (5) and (6) |
| `albedo` | Fsu/Fsd |

Note: in the raw file the column `Ts` is the measured soil temperature at 10 cm (TDR-315H), called T_soil in
the paper; T_s in the paper is the modeled surface temperature.
