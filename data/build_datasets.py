"""
Build the three derived datasets from the raw tower record.

  daytime_record.csv      daytime records after the four-month commissioning period (time stamps 06:00-18:30 LST,
                          sun above the horizon at the middle of the averaging period), with measured (not
                          gap-filled) turbulent fluxes and all six model drivers present. Used for the
                          descriptive analyses; the flux-characterization (FC) dataset is its subset with
                          Fsd > 50 W m-2.
  modeling_dataset.csv    the same records after the modeling screening of Section 2c.
  cnn_daytime_series.csv  all daytime records, measured or gap-filled, with a QC_bad flag (gap-filled or screened
                          out), so that the CNN input windows stay continuous while flagged targets are excluded.
Record counts: results/lsm_cv/metrics.json (field qc) and docs/datasets.md.

All three carry the storage-corrected surface ground heat flux Fg_surface (Section 2d) and the half-hourly
tendency of the measured net radiation dRn_dt (Eqs. 5 and 6), both computed on the continuous record.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'flsf'))
import paths, config as C
from preprocessing import load_observed, _season, rn_tendency, sun_up, flux_measured, screen

DRIVERS = ['Fsd', 'Fld', 'Ta', 'RH', 'Ws', 'SWC']


def raw_with_surface_g():
    r = pd.read_csv(paths.OBSERVED, skiprows=2, header=0).rename(columns={'xlDateTime': 'DateTime'})
    r.replace(-9999, np.nan, inplace=True)
    r['DateTime'] = pd.to_datetime(r['DateTime'])
    r = r.sort_values('DateTime').reset_index(drop=True)
    r['SWC'] = r[['Sws_10cma', 'Sws_10cmb']].mean(axis=1)
    r['Year'] = r.DateTime.dt.year; r['Month'] = r.DateTime.dt.month; r['Day'] = r.DateTime.dt.day
    r['Hour'] = r.DateTime.dt.hour; r['DOY'] = r.DateTime.dt.dayofyear; r['Date'] = r.DateTime.dt.date
    r['Season'] = r['Month'].map(_season)
    same = r['Date'].eq(r['Date'].shift())
    r['Cs'] = C.soil_heat_capacity(r['SWC'])
    r['dTs_dt'] = ((r['Ts'] - r['Ts'].shift()) / C.DT_SEC).where(same, np.nan)
    r['Fg_surface'] = r['Fg'] + r['Cs'] * C.SOIL_PLATE_DEPTH * r['dTs_dt']
    r['dRn_dt'] = rn_tendency(r)   # half-hourly tendency of the measured net radiation, Eqs. (5) and (6)
    r['albedo'] = r['Fsu'] / r['Fsd']
    r['sun_up'] = sun_up(r)                  # sun above the horizon at the middle of the averaging period
    r['flux_measured'] = flux_measured(r)    # turbulent fluxes measured, not gap-filled
    return r


def main():
    os.makedirs(paths.DERIVED, exist_ok=True)
    r = raw_with_surface_g()
    post = ~((r.Year == 2024) & r.Month.isin([1, 2, 3, 4]))
    day = r[r.sun_up & r.Hour.between(6, 18) & post].copy()          # all daytime records (CNN input series)
    meas = day[day.flux_measured]
    # CNN targets: flagged when gap-filled or removed by the modeling screening (same tests as load_observed)
    remove, _ = screen(r, meas)
    day['QC_bad'] = ~day.flux_measured
    day.loc[remove.index[remove.values], 'QC_bad'] = True
    cnn = day.drop(columns=['Day', 'DOY', 'albedo'])
    cnn.to_csv(paths.CNN_SERIES, index=False)

    d6 = meas.dropna(subset=DRIVERS)
    d6.to_csv(paths.DAYTIME, index=False)

    m, rep = load_observed(paths.OBSERVED, G_TARGET='surface')
    m['albedo'] = (m['Fsu'] / m['Fsd']).clip(0, 1)
    m.to_csv(paths.MODELING, index=False)

    print('daytime (sun up, post-commissioning): ', len(day), ' measured fluxes:', len(meas))
    print('daytime_record (six drivers):        ', len(d6))
    print('  of which Fsd > 50 W m-2:            ', int((d6.Fsd > 50).sum()))
    print('modeling_dataset:                     ', len(m), rep)
    print('cnn_daytime_series:                   ', len(cnn), 'QC_bad =', int(cnn.QC_bad.sum()))


if __name__ == '__main__':
    main()
