import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('TkAgg')

sites = ["site_1", "site_2", "site_3", "site_4"]
file_paths = [f"central/{site}_ndvi_stats2.csv" for site in sites]
data = [pd.read_csv(file, usecols=["year", "month", "avg_si"]) for file in file_paths]

min_y = min(df["avg_si"].min() for df in data)
max_y = max(df["avg_si"].max() for df in data)

fig, axes = plt.subplots(4, len(sites), figsize=(4*len(sites), 22), sharey=True)
fig.tight_layout(pad=3, h_pad=6)

for i, year in enumerate(range(2021, 2025)):
    for j, (df, site) in enumerate(zip(data, sites)):
        ax = axes[i, j]
        df_year = df[df["year"] == year]
        ax.plot(df_year["month"], df_year["avg_si"], marker="o")
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], rotation=45)
        ax.set_ylim(min_y, max_y)
        ax.set_title(f"{site.replace('_', ' ').title()} - {year}")
        if j == len(sites) // 2:
            ax.tick_params(axis='y', labelleft=True)

plt.savefig('plots/ndvi.png', dpi=300, bbox_inches='tight')
#plt.show()
