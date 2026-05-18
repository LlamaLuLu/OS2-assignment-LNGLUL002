"""
CSC3002F Scheduling Assignment – Analysis & Graphing
Run from the project root where results/ folder lives:
    python3 analyse.py
Outputs 6 PNG files into results/graphs/
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── config ────────────────────────────────────────────────────────────────────
RESULTS_DIR = "results"          # folder containing the CSVs
OUT_DIR     = "results/graphs"   # where PNGs will be saved
os.makedirs(OUT_DIR, exist_ok=True)

SCHEDULERS = ["FCFS", "SJF", "PRIORITY", "MLFQ", "ASJF"]
COLORS     = {"FCFS": "#4C72B0", "SJF": "#DD8452",
               "PRIORITY": "#55A868", "MLFQ": "#C44E52",
               "ASJF": "#9467BD"}
PATRON_COUNTS = [10, 30, 50]

# ── load data ─────────────────────────────────────────────────────────────────
csv_files = glob.glob(os.path.join(RESULTS_DIR, "*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSVs found in {RESULTS_DIR}/")

frames = []
for f in csv_files:
    df = pd.read_csv(f)
    # extract patron count and seed from filename e.g. FCFS_30_42.csv
    base = os.path.basename(f).replace(".csv", "")
    parts = base.split("_")
    df["patronCount"] = int(parts[1])
    df["seed"]        = int(parts[2])
    frames.append(df)

data = pd.concat(frames, ignore_index=True)
print(f"Loaded {len(data):,} rows from {len(csv_files)} files.\n")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 – Box plots: Wait Time per scheduler (all patron counts combined)
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

plot_data  = [data[data["scheduler"] == s]["waitTime"].values for s in SCHEDULERS]
bp = ax.boxplot(plot_data, patch_artist=True, notch=False,
                medianprops=dict(color="black", linewidth=2),
                flierprops=dict(marker=".", markersize=3, alpha=0.4))

for patch, sched in zip(bp["boxes"], SCHEDULERS):
    patch.set_facecolor(COLORS[sched])
    patch.set_alpha(0.75)

ax.set_xticks(range(1, 5))
ax.set_xticklabels(SCHEDULERS, fontsize=12)
ax.set_ylabel("Wait Time (ms)", fontsize=12)
ax.set_title("Figure 1 – Wait Time Distribution per Scheduler (all runs)", fontsize=13)
ax.set_yscale("log")
ax.yaxis.set_minor_formatter(plt.NullFormatter())
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/fig1_waittime_boxplot.png", dpi=150)
plt.close(fig)
print("Saved fig1_waittime_boxplot.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 – Box plots: Turnaround Time per scheduler
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

plot_data = [data[data["scheduler"] == s]["turnaroundTime"].values for s in SCHEDULERS]
bp = ax.boxplot(plot_data, patch_artist=True, notch=False,
                medianprops=dict(color="black", linewidth=2),
                flierprops=dict(marker=".", markersize=3, alpha=0.4))

for patch, sched in zip(bp["boxes"], SCHEDULERS):
    patch.set_facecolor(COLORS[sched])
    patch.set_alpha(0.75)

ax.set_xticks(range(1, 5))
ax.set_xticklabels(SCHEDULERS, fontsize=12)
ax.set_ylabel("Turnaround Time (ms)", fontsize=12)
ax.set_title("Figure 2 – Turnaround Time Distribution per Scheduler (all runs)", fontsize=13)
ax.set_yscale("log")
ax.yaxis.set_minor_formatter(plt.NullFormatter())
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/fig2_turnaround_boxplot.png", dpi=150)
plt.close(fig)
print("Saved fig2_turnaround_boxplot.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 – Mean & Median Wait Time vs Patron Count (line chart)
# ═══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

for ax, stat, label in zip(axes,
                            ["mean", "median"],
                            ["Mean Wait Time (ms)", "Median Wait Time (ms)"]):
    for sched in SCHEDULERS:
        ys = []
        for n in PATRON_COUNTS:
            vals = data[(data["scheduler"] == sched) &
                        (data["patronCount"] == n)]["waitTime"]
            ys.append(vals.mean() if stat == "mean" else vals.median())
        ax.plot(PATRON_COUNTS, ys, marker="o", linewidth=2,
                color=COLORS[sched], label=sched)

    ax.set_xlabel("Number of Patrons", fontsize=11)
    ax.set_ylabel(label, fontsize=11)
    ax.set_xticks(PATRON_COUNTS)
    ax.legend(fontsize=10)
    ax.grid(linestyle="--", alpha=0.4)
    title = "Mean" if stat == "mean" else "Median"
    ax.set_title(f"{title} Wait Time vs Load", fontsize=12)

fig.suptitle("Figure 3 – Scaling Behaviour: Wait Time as Patron Count Increases",
             fontsize=13, y=1.01)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/fig3_scaling_waittime.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved fig3_scaling_waittime.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 – Starvation: % orders waiting > 3 s, broken out by patron count
# ═══════════════════════════════════════════════════════════════════════════════
THRESHOLD = 3000   # ms

fig, ax = plt.subplots(figsize=(10, 5))
x      = np.arange(len(PATRON_COUNTS))
width  = 0.2
offsets = [-1.5, -0.5, 0.5, 1.5]

for i, sched in enumerate(SCHEDULERS):
    pcts = []
    for n in PATRON_COUNTS:
        sub = data[(data["scheduler"] == sched) & (data["patronCount"] == n)]
        pct = 100 * (sub["waitTime"] > THRESHOLD).sum() / len(sub)
        pcts.append(pct)
    ax.bar(x + offsets[i] * width, pcts, width,
           color=COLORS[sched], label=sched, alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels([f"{n} patrons" for n in PATRON_COUNTS], fontsize=11)
ax.set_ylabel("Orders waiting > 3 000 ms (%)", fontsize=11)
ax.set_title("Figure 4 – Starvation Risk: % Orders Waiting > 3 s", fontsize=13)
ax.legend(fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/fig4_starvation.png", dpi=150)
plt.close(fig)
print("Saved fig4_starvation.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 – MLFQ: Wait Time distribution broken out by queue level
# ═══════════════════════════════════════════════════════════════════════════════
mlfq = data[data["scheduler"] == "MLFQ"].copy()

fig, ax = plt.subplots(figsize=(9, 5))
q_colors = ["#2196F3", "#FF9800", "#E91E63"]
q_labels = ["Q0 (1st drink – highest priority)",
            "Q1 (2nd drink)",
            "Q2 (3rd+ drink – lowest priority)"]

plot_data = [mlfq[mlfq["queueLevel"] == q]["waitTime"].values for q in [0, 1, 2]]
bp = ax.boxplot(plot_data, patch_artist=True, notch=False,
                medianprops=dict(color="black", linewidth=2),
                flierprops=dict(marker=".", markersize=3, alpha=0.4))

for patch, col in zip(bp["boxes"], q_colors):
    patch.set_facecolor(col)
    patch.set_alpha(0.75)

ax.set_xticks([1, 2, 3])
ax.set_xticklabels(q_labels, fontsize=10)
ax.set_ylabel("Wait Time (ms)", fontsize=12)
ax.set_title("Figure 5 – MLFQ: Wait Time by Queue Level", fontsize=13)
ax.set_yscale("log")
ax.yaxis.set_minor_formatter(plt.NullFormatter())
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/fig5_mlfq_queues.png", dpi=150)
plt.close(fig)
print("Saved fig5_mlfq_queues.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 – Summary table: Mean, Median, Std Dev for all metrics × schedulers
#             Rendered as a heatmap-style table
# ═══════════════════════════════════════════════════════════════════════════════
summary_rows = []
for sched in SCHEDULERS:
    sub = data[data["scheduler"] == sched]
    for metric in ["waitTime", "turnaroundTime"]:
        m = sub[metric]
        summary_rows.append({
            "Scheduler": sched,
            "Metric": "Wait" if metric == "waitTime" else "Turnaround",
            "Mean":   round(m.mean()),
            "Median": round(m.median()),
            "Std Dev": round(m.std()),
            "Max":    int(m.max()),
            "% > 3s": round(100 * (m > 3000).sum() / len(m), 1),
        })

df_sum = pd.DataFrame(summary_rows)

fig, ax = plt.subplots(figsize=(13, 5))
ax.axis("off")

col_labels = ["Scheduler", "Metric", "Mean (ms)", "Median (ms)",
              "Std Dev (ms)", "Max (ms)", "% > 3 s"]
cell_vals = df_sum.values.tolist()

tbl = ax.table(cellText=cell_vals, colLabels=col_labels,
               cellLoc="center", loc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
tbl.scale(1, 1.6)

# colour header
for j in range(len(col_labels)):
    tbl[0, j].set_facecolor("#37474F")
    tbl[0, j].set_text_props(color="white", fontweight="bold")

# colour scheduler rows
sched_order = []
for row in cell_vals:
    sched_order.append(row[0])

for i, sched in enumerate(sched_order, start=1):
    for j in range(len(col_labels)):
        tbl[i, j].set_facecolor(COLORS[sched] + "33")   # 20% alpha hex

ax.set_title("Figure 6 – Summary Statistics: All Schedulers × Metrics",
             fontsize=13, pad=12)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/fig6_summary_table.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved fig6_summary_table.png")

print(f"\nAll done. Graphs saved to: {OUT_DIR}/")
print(df_sum.to_string(index=False))
