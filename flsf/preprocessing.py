"""
================================================================================
 PREPROCESSING AND QUALITY CONTROL OF THE MODELING DATASET (Sections 2c and 2d)
================================================================================
 Builds the modeling dataset from the raw tower record, including the calorimetric
 storage correction of the ground heat flux. Every step is logged in a QC report.

 Steps:
   1. Read the half-hourly tower record; -9999 -> NaN; SWC = mean of the two 10-cm probes.
   2. Ground-heat-flux STORAGE CORRECTION (de Vries 1963), three-phase Cs:
          Cs = (1-phi)*C_MINERAL + theta*C_WATER + (phi-theta)*C_AIR
          G_surface = G_plate(-10cm) + Cs*dz*dTsoil/dt,   dz = SOIL_PLATE_DEPTH
      (the raw column Ts is the measured 10-cm soil temperature, T_soil in the paper),
      computed on the continuous 24-h series before the daytime subset; the half-hourly tendency of the
      measured net radiation, dRn/dt of Eqs. (5) and (6), is computed on the same continuous series.
   3. Exclude the commissioning period (January-April 2024); keep daytime records (time stamps 06:00 to
      18:30 LST with the sun above the horizon at the middle of the averaging period, solar_elevation) whose
      turbulent fluxes were measured, not gap-filled (flux_measured).
   4. Physical-limit tests (Foken 2008; Mauder et al. 2013).
   5. Double-difference spike detection (Papale et al. 2006) on the continuous half-hourly record, with
      per-season thresholds from the daytime records (spike_flags).
   6. Ts flat-line count (reported as Ts_flatline in the QC report; no record is removed).
   7. Dew flag (RH > 95 %, LE < 0): kept, because dew and condensation are physically
      real and simulated by the model (Section 2d).
   8. Remove implausible midday records (10:00-15:30 LST with LE < 0 or H < -50 W m-2).

 Returns (df_clean, qc_report). G_TARGET='surface' (used in the paper) sets the observed G
 to the storage-corrected surface flux.
================================================================================
"""
import numpy as np, pandas as pd
import config as C

LIMITS = {"Fh": (-200, 800), "Fe": (-100, 800), "Fg": (-200, 400), "Fn": (-200, 1200)}

def rn_tendency(r):
    """Half-hourly tendency of the measured net radiation on the continuous record r (sorted by time):
    dRn/dt = (Rn(t) - Rn(t - 30 min)) / 1800 s; NaN when the record 30 min earlier is missing."""
    step = r["DateTime"].diff().dt.total_seconds()
    return ((r["Fn"] - r["Fn"].shift()) / C.DT_SEC).where(step == C.DT_SEC)

def _season(m):
    return "DJF" if m in (12,1,2) else "MAM" if m in (3,4,5) else "JJA" if m in (6,7,8) else "SON"

def solar_elevation(t):
    """Solar elevation [deg] at the times t (pandas Series of LST time stamps); NOAA approximation."""
    doy = t.dt.dayofyear.values
    hr = (t.dt.hour + t.dt.minute / 60 + t.dt.second / 3600).values
    g = 2 * np.pi / 365 * (doy - 1 + (hr - 12) / 24)
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g) - 0.006758 * np.cos(2 * g)
            + 0.000907 * np.sin(2 * g) - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    eqt = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g) - 0.014615 * np.cos(2 * g)
                    - 0.040849 * np.sin(2 * g))
    tst = hr * 60 + eqt + 4 * C.SITE_LON - 60 * C.LST_UTC_OFFSET_H
    ha = np.radians(tst / 4 - 180); lat = np.radians(C.SITE_LAT)
    return np.degrees(np.arcsin(np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(ha)))


def sun_up(r):
    """True when the sun is above the horizon at the middle of the 30-min period that ends at the time stamp."""
    return pd.Series(solar_elevation(r["DateTime"] - pd.Timedelta(seconds=C.DT_SEC / 2)) > 0, index=r.index)


def flux_measured(r):
    """True when the turbulent fluxes of the record were measured, not gap-filled. The raw file keeps the EddyPro
    water-vapor flux (Fh2o_EP, missing where EddyPro gave no value); where it exists, the latent heat flux Fe equals
    lambda(Ta) * M_w * Fh2o_EP, and elsewhere Fe was gap-filled by PyFluxPro. A record is measured when Fh2o_EP
    exists and Fe agrees with it to within 1 % (at least 1 W m-2). No separate flag exists for H; H is taken from
    the same records (the sonic anemometer is needed for both fluxes)."""
    ep = r["Fh2o_EP"]
    lam = (2501.0 - 2.37 * r["Ta"].fillna(20.0)) * 1e3          # J kg-1 (Ta in degC)
    le_ep = lam * 18.015e-6 * ep                               # mmol m-2 s-1 -> W m-2
    return (ep.notna() & ((r["Fe"] - le_ep).abs() <= np.maximum(1.0, 0.01 * le_ep.abs()))).fillna(False)


def spike_flags(r, day_index, col, z=5.5):
    """Double-difference spike test (Papale et al. 2006). r is the continuous, time-sorted half-hourly record with
    non-measured values set to NaN; d_i = (x_i - x_{i-1}) - (x_{i+1} - x_i) is formed only from three consecutive
    half-hours. Median and MAD thresholds are computed per season over the daytime records day_index, and the
    flags are returned for those records."""
    x = r[col].values; t = r["DateTime"]
    d = np.full(len(x), np.nan)
    d[1:-1] = (x[1:-1] - x[:-2]) - (x[2:] - x[1:-1])
    step = t.diff().dt.total_seconds().values
    ok = np.zeros(len(x), bool); ok[1:-1] = (step[1:-1] == C.DT_SEC) & (step[2:] == C.DT_SEC)
    d[~ok] = np.nan
    d = pd.Series(d, index=r.index).loc[day_index]
    flag = pd.Series(False, index=day_index)
    for _, g in d.groupby(r.loc[day_index, "Season"]):
        md = np.nanmedian(g); mad = np.nanmedian(np.abs(g - md))
        if not np.isfinite(mad) or mad == 0: continue
        flag.loc[g.index[(np.abs(g - md) > z * mad / 0.6745).values]] = True
    return flag


def daytime_mask(r):
    """Daytime records after the commissioning period: time stamps 06:00-18:30 LST, sun above the horizon at the
    middle of the averaging period, turbulent fluxes measured."""
    return (sun_up(r) & r["Hour"].between(6, 18) & flux_measured(r)
            & ~((r["Year"] == 2024) & (r["Month"].isin([1, 2, 3, 4]))))


def screen(r, d):
    """Modeling screening of Section 2c on the daytime records d of the continuous record r. Returns the
    boolean removal mask and the counts of each test."""
    rep = {}
    lim = pd.Series(False, index=d.index)
    for c, (lo, hi) in LIMITS.items():
        b = ((d[c] < lo) | (d[c] > hi)).fillna(False); lim |= b; rep["limit_%s" % c] = int(b.sum())
    rm = r.copy(); meas = flux_measured(r)
    rm.loc[~meas, ["Fh", "Fe"]] = np.nan
    spike = pd.Series(False, index=d.index)
    for c in ("Fh", "Fe", "Fg"):
        sp = spike_flags(rm, d.index, c); spike |= sp; rep["spike_%s" % c] = int(sp.sum())
    dew = (d["RH"] > 95) & (d["Fe"] < 0); rep["dew_kept"] = int(dew.sum())
    midbad = (d["Hour"].between(10, 15)) & ((d["Fe"] < 0) | (d["Fh"] < -50)); rep["midday_bad"] = int(midbad.sum())
    remove = (lim | spike | midbad) & ~dew
    rep["removed"] = int(remove.sum())
    return remove, rep

def load_observed(data_file, G_TARGET="surface"):
    r = pd.read_csv(data_file, skiprows=2, header=0).rename(columns={"xlDateTime": "DateTime"})
    r.replace(-9999, np.nan, inplace=True)
    r["DateTime"] = pd.to_datetime(r["DateTime"], errors="coerce")
    r = r.dropna(subset=["DateTime"]).sort_values("DateTime").reset_index(drop=True)
    r["SWC"] = r[["Sws_10cma", "Sws_10cmb"]].mean(axis=1)
    r["Year"]=r["DateTime"].dt.year; r["Month"]=r["DateTime"].dt.month
    r["Hour"]=r["DateTime"].dt.hour; r["Date"]=r["DateTime"].dt.date; r["Season"]=r["Month"].map(_season)
    rep = {"raw_rows": int(len(r))}

    # 2. surface-G storage correction (continuous series)
    same = r["Date"].eq(r["Date"].shift())
    r["Cs"] = C.soil_heat_capacity(r["SWC"])
    r["dTs_dt"] = ((r["Ts"] - r["Ts"].shift()) / 1800.0).where(same, np.nan)
    r["Fg_surface"] = r["Fg"] + r["Cs"] * C.SOIL_PLATE_DEPTH * r["dTs_dt"]
    r["dRn_dt"] = rn_tendency(r)   # Eqs. (5) and (6), continuous series
    rep["Ts_flatline"] = int((r["Ts"].diff() == 0).sum())

    # 3. daytime, post-commissioning, measured fluxes
    post = ~((r["Year"] == 2024) & (r["Month"].isin([1, 2, 3, 4])))
    rep["daytime_window_post_commissioning"] = int((r["Hour"].between(6, 18) & post).sum())
    rep["sun_below_horizon"] = int((r["Hour"].between(6, 18) & post & ~sun_up(r)).sum())
    rep["gap_filled_daytime"] = int((r["Hour"].between(6, 18) & post & sun_up(r) & ~flux_measured(r)).sum())
    d = r[daytime_mask(r)].copy()
    rep["daytime_post_commissioning"] = int(len(d))

    # 4-8. physical limits, spikes, dew (kept), implausible midday records (removed)
    remove, rq = screen(r, d); rep.update(rq)
    d = d[~remove].copy()
    rep["retained"] = int(len(d)); rep["retained_pct"] = round(100*len(d)/rep["daytime_post_commissioning"], 1)

    d["Gobs"] = d["Fg_surface"] if G_TARGET == "surface" else d["Fg"]
    d["Season_short"] = d["Season"]; d["WindSpeed"] = d["Ws"]
    d = d.dropna(subset=["Fsd", "Fld", "Ta", "RH", "Ws", "SWC", "Fn", "Fe", "Fh", "Gobs", "dRn_dt"]).reset_index(drop=True)
    rep["final_rows"] = int(len(d))
    return d, rep
