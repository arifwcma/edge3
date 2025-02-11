import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

file1 = "central/site_1_ndvi_stats2.csv"
file2 = "central/site_2_ndvi_stats2.csv"

data1 = pd.read_csv(file1, usecols=["year", "month", "avg_si"])
data2 = pd.read_csv(file2, usecols=["year", "month", "avg_si"])

fig, axes = plt.subplots(4, 2, figsize=(10, 15), sharey=True)
fig.tight_layout(pad=3, h_pad=6)

min_y = min(data1["avg_si"].min(), data2["avg_si"].min())
max_y = max(data1["avg_si"].max(), data2["avg_si"].max())

for i, year in enumerate(range(2021, 2025)):
    ax1 = axes[i, 0]
    ax2 = axes[i, 1]
    data1_year = data1[data1["year"] == year]
    data2_year = data2[data2["year"] == year]
    ax1.plot(data1_year["month"], data1_year["avg_si"], marker="o")
    ax2.plot(data2_year["month"], data2_year["avg_si"], marker="o")
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], rotation=45)
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], rotation=45)
    ax1.set_ylim(min_y, max_y)
    ax2.set_ylim(min_y, max_y)
    ax1.set_title(f"Site 1 - {year}")
    ax2.set_title(f"Site 2 - {year}")
    ax2.tick_params(axis='y', labelleft=True)

plt.show()