#!/usr/bin/env python3
"""
Python Data Visualization Engine
Generates Apple HIG-styled high-resolution visual comparison charts
using real empirical data from real_data.json.
"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Load Real Empirical Dataset
with open("real_data.json", "r") as f:
    data = json.load(f)

metros = data["metros"]
metro_names = [m["name"].split(",")[0] for m in metros.values()]
gross_wages = [m["blsWages"]["p50_median"] for m in metros.values()]
net_incomes = [m["computedMedian"]["tax"]["netAnnual"] for m in metros.values()]
annual_burns = [m["computedMedian"]["totalMonthlyBurn"] * 12 for m in metros.values()]
annual_surplus = [m["computedMedian"]["monthlySavingsSurplus"] * 12 for m in metros.values()]
months_to_save_50k = [m["computedMedian"]["monthsToSave50k"] for m in metros.values()]

# Set Apple HIG styling
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["-apple-system", "SF Pro Text", "Helvetica Neue", "Arial"]
plt.rcParams["axes.edgecolor"] = "none"
plt.rcParams["figure.facecolor"] = "#F5F5F7"
plt.rcParams["axes.facecolor"] = "#FFFFFF"

# Create Multi-Panel Figure
fig = plt.figure(figsize=(14, 9), dpi=200)
gs = fig.add_gridspec(2, 2, hspace=0.36, wspace=0.22, top=0.86, bottom=0.08, left=0.08, right=0.95)

fig.suptitle(
    "Real Metro Economics: BLS Wages, IRS Taxes & HUD Rents\n"
    "Quantitative Career Relocation & Capital Decision Model",
    fontsize=16, fontweight="700", color="#1D1D1F", y=0.95
)

# Panel 1: Gross Median Wage vs. Net Take-Home Pay (Real IRS + State Taxes)
ax1 = fig.add_subplot(gs[0, 0])
x = np.arange(len(metro_names))
width = 0.36

rects1 = ax1.bar(x - width/2, [g / 1000 for g in gross_wages], width, label="BLS Median Gross ($k)", color="#8E8E93", alpha=0.55, edgecolor="none", zorder=3)
rects2 = ax1.bar(x + width/2, [n / 1000 for n in net_incomes], width, label="Real Net Take-Home ($k)", color="#0071E3", edgecolor="none", zorder=3)

ax1.set_title("1. Real Gross vs. Net Take-Home (After Tax)", fontsize=13, fontweight="600", color="#1D1D1F", pad=12)
ax1.set_xticks(x)
ax1.set_xticklabels(metro_names, rotation=25, ha="right", fontsize=9.5, color="#1D1D1F")
ax1.set_ylabel("Annual Amount ($k USD)", fontsize=10, color="#86868B")
ax1.grid(axis="y", color="#E5E5EA", linestyle="--", linewidth=0.8, zorder=0)
ax1.legend(frameon=False, fontsize=9.5, loc="upper right")
ax1.tick_params(colors="#86868B", which="both")
for spine in ax1.spines.values():
    spine.set_visible(False)

# Panel 2: Total Real Living Cost (HUD Rent + MIT Essentials)
ax2 = fig.add_subplot(gs[0, 1])
rents = [m["hudFmr"]["oneBed"] * 12 / 1000 for m in metros.values()]
essentials = [m["mitLivingEssentials"] * 12 / 1000 for m in metros.values()]

ax2.bar(x, rents, width=0.55, label="HUD Fair Market Rent (1-Bed)", color="#FF9500", alpha=0.9, zorder=3)
ax2.bar(x, essentials, width=0.55, bottom=rents, label="MIT Living Essentials", color="#FFCC00", alpha=0.75, zorder=3)

ax2.set_title("2. Real Annual Living Burn (HUD Rent + Essentials)", fontsize=13, fontweight="600", color="#1D1D1F", pad=12)
ax2.set_xticks(x)
ax2.set_xticklabels(metro_names, rotation=25, ha="right", fontsize=9.5, color="#1D1D1F")
ax2.set_ylabel("Annual Burn ($k USD)", fontsize=10, color="#86868B")
ax2.grid(axis="y", color="#E5E5EA", linestyle="--", linewidth=0.8, zorder=0)
ax2.legend(frameon=False, fontsize=9.5, loc="upper left")
ax2.tick_params(colors="#86868B", which="both")
for spine in ax2.spines.values():
    spine.set_visible(False)

# Panel 3: True Real Net Annual Savings Surplus
ax3 = fig.add_subplot(gs[1, 0])
colors_surplus = ["#34C759" if s > 40000 else "#30B0C7" for s in annual_surplus]
bars_surplus = ax3.bar(x, [s / 1000 for s in annual_surplus], width=0.55, color=colors_surplus, zorder=3)

ax3.set_title("3. True Annual Discretionary Surplus (Net - Burn)", fontsize=13, fontweight="600", color="#1D1D1F", pad=12)
ax3.set_xticks(x)
ax3.set_xticklabels(metro_names, rotation=25, ha="right", fontsize=9.5, color="#1D1D1F")
ax3.set_ylabel("Net Surplus ($k USD)", fontsize=10, color="#86868B")
ax3.grid(axis="y", color="#E5E5EA", linestyle="--", linewidth=0.8, zorder=0)
ax3.tick_params(colors="#86868B", which="both")
for spine in ax3.spines.values():
    spine.set_visible(False)

# Add value labels on surplus bars
for bar in bars_surplus:
    height = bar.get_height()
    ax3.annotate(f"${height:.1f}k",
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 4), textcoords="offset points",
                 ha="center", va="bottom", fontsize=8.5, fontweight="600", color="#1D1D1F")

# Panel 4: Real Months Required to Accumulate $50,000 Capital Buffer
ax4 = fig.add_subplot(gs[1, 1])
colors_speed = ["#34C759" if m < 12 else ("#FF9500" if m < 15 else "#FF3B30") for m in months_to_save_50k]
bars_speed = ax4.bar(x, months_to_save_50k, width=0.55, color=colors_speed, zorder=3)

ax4.set_title("4. Speed to $50,000 Emergency Reserve (Months)", fontsize=13, fontweight="600", color="#1D1D1F", pad=12)
ax4.set_xticks(x)
ax4.set_xticklabels(metro_names, rotation=25, ha="right", fontsize=9.5, color="#1D1D1F")
ax4.set_ylabel("Months Required", fontsize=10, color="#86868B")
ax4.grid(axis="y", color="#E5E5EA", linestyle="--", linewidth=0.8, zorder=0)
ax4.tick_params(colors="#86868B", which="both")
for spine in ax4.spines.values():
    spine.set_visible(False)

for bar in bars_speed:
    height = bar.get_height()
    ax4.annotate(f"{height:.1f} mo",
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 4), textcoords="offset points",
                 ha="center", va="bottom", fontsize=8.5, fontweight="600", color="#1D1D1F")

# Save high-resolution chart
chart_path = "real_data_decision_chart.png"
plt.savefig(chart_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
print(f"Exported real data chart to {chart_path} successfully.")
