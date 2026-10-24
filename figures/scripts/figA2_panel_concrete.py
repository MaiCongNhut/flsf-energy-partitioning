"""Fig. A2: hourly mean temperatures of the front- and back-panel surfaces, the air above and below the panel
and the concrete-pile surface (data/raw/AllTemperature.xlsx, sheet 'Data'; the above-panel air is rebuilt from the
tower record with the hour of each averaging period)."""
import os
import pandas as pd
import matplotlib.pyplot as plt
import style as S

S.apply()
df = pd.read_excel(os.path.join(S.paths.RAW, 'AllTemperature.xlsx'), sheet_name='Data'); h = df['Hour'].values
# above-panel air: tower air temperature (HMP155A, 2.4 m) over the same period, each 30-min record assigned to the
# hour in which its averaging period lies (time stamp - 30 min), like the instantaneous 10-min HOBO samples
r = pd.read_csv(S.paths.OBSERVED, skiprows=2, header=0).replace(-9999, float('nan'))
ta = r.set_index(pd.to_datetime(r['xlDateTime']))['Ta'].sort_index().loc[:'2025-04-30 23:59'].dropna()
df['Air Temperature (above panel)'] = ta.groupby((ta.index - pd.Timedelta(minutes=30)).hour).mean().reindex(h).values
series = [('Front_Panel_Surface', 'Front-panel surface (1–15 Aug 2023)', '#C0392B', '-'),
          ('Back_Panel_Surface', 'Back-panel surface', '#C0392B', '--'),
          ('Air Temperature (above panel)', 'Above-panel air', '#222222', '-'),
          ('Air Temperature (below panel)', 'Below-panel air', '#222222', '--'),
          ('Concrete_Temperature', 'Concrete-pile surface', '#0072B2', '-')]
fig, ax = plt.subplots(figsize=(S.ONE_HALF_COL, 3.4), layout='constrained'); S.grid(ax)
for col, lab, c, ls in series:
    ax.plot(h, df[col].values, color=c, lw=0.9, ls=ls, label=lab)
ax.set_xlim(0, 23); ax.set_xticks(range(0, 24, 3)); ax.set_xlabel('Hour (LST)'); ax.set_ylabel('Temperature (°C)')
fig.legend(loc='outside lower center', ncol=2, fontsize=7.8)
S.save(fig, 'FigA2_PanelConcrete.png')
