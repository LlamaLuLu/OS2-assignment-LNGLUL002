"""
CSC3002F Scheduling Assignment – Data Validation Script
Run from the project root where results/ folder lives:
    python3 validate.py
Checks all CSV files in results/ for data integrity.
"""

import glob
import os
import pandas as pd
from collections import defaultdict

RESULTS_DIR = "results"
TOLERANCE_MS = 50  # max acceptable overhead between turnaround and wait+exec

# Valid drink preparation times from DrinkOrder.Drink enum
VALID_EXEC_TIMES = {20, 25, 40, 50, 60, 65, 70, 75, 100, 200}

# ── load data ─────────────────────────────────────────────────────────────────
csv_files = glob.glob(os.path.join(RESULTS_DIR, "*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {RESULTS_DIR}/")

frames = []
for f in csv_files:
    df = pd.read_csv(f)
    df["_filename"] = os.path.basename(f).replace(".csv", "")
    frames.append(df)

data = pd.concat(frames, ignore_index=True)

print("=" * 60)
print("VALIDATION REPORT")
print(f"Checking {len(data):,} rows across {len(csv_files)} files")
print("=" * 60)

passed = 0
failed = 0

def ok(msg):
    global passed
    print(f"  ✅ {msg}")
    passed += 1

def fail(msg):
    global failed
    print(f"  ❌ {msg}")
    failed += 1

def warn(msg):
    print(f"  ⚠️  {msg}")

# ── check 1: row count consistency across schedulers ─────────────────────────
print("\n[1] Row counts — same workload across schedulers?")
seed_patron_counts = defaultdict(dict)
for f in csv_files:
    base = os.path.basename(f).replace(".csv", "")
    parts = base.split("_")
    sched, n, seed = parts[0], parts[1], parts[2]
    seed_patron_counts[f"{n}_{seed}"][sched] = len(pd.read_csv(f))

all_match = True
for key in sorted(seed_patron_counts.keys()):
    counts = seed_patron_counts[key]
    vals = list(counts.values())
    if len(set(vals)) != 1:
        fail(f"{key}: mismatched row counts — {counts}")
        all_match = False
if all_match:
    ok("All scheduler/seed/patron-count combinations have matching row counts")

# ── check 2: turnaround > wait ────────────────────────────────────────────────
print("\n[2] turnaroundTime > waitTime for every row?")
bad = data[data["turnaroundTime"] <= data["waitTime"]]
if len(bad) == 0:
    ok("All rows pass")
else:
    fail(f"{len(bad)} rows where turnaroundTime <= waitTime:")
    print(bad[["scheduler", "patronID", "drink", "waitTime", "turnaroundTime"]].head(10).to_string(index=False))

# ── check 3: turnaround ≈ wait + execTime ────────────────────────────────────
print(f"\n[3] turnaroundTime ≈ waitTime + execTime (within {TOLERANCE_MS}ms)?")
data["_expected_tat"] = data["waitTime"] + data["execTime"]
data["_tat_diff"] = (data["turnaroundTime"] - data["_expected_tat"]).abs()
bad = data[data["_tat_diff"] > TOLERANCE_MS]
if len(bad) == 0:
    ok(f"All rows within {TOLERANCE_MS}ms overhead tolerance "
       f"(mean overhead: {data['_tat_diff'].mean():.1f}ms)")
else:
    pct = 100 * len(bad) / len(data)
    warn(f"{len(bad)} rows ({pct:.4f}%) exceed {TOLERANCE_MS}ms tolerance")
    print(f"     max diff={data['_tat_diff'].max():.0f}ms, "
          f"mean diff={data['_tat_diff'].mean():.1f}ms, "
          f"median diff={data['_tat_diff'].median():.1f}ms")
    print("     (likely OS scheduling jitter — acceptable if < 0.1% of rows)")

# ── check 4: no negative times ────────────────────────────────────────────────
print("\n[4] No negative wait or turnaround times?")
neg_wait = (data["waitTime"] < 0).sum()
neg_tat  = (data["turnaroundTime"] < 0).sum()
if neg_wait == 0 and neg_tat == 0:
    ok("No negative values found")
else:
    if neg_wait > 0:
        fail(f"{neg_wait} rows with negative waitTime")
    if neg_tat > 0:
        fail(f"{neg_tat} rows with negative turnaroundTime")

# ── check 5: queue level integrity ───────────────────────────────────────────
print("\n[5] Queue level integrity?")
non_mlfq = data[data["scheduler"] != "MLFQ"]
bad_non_mlfq = non_mlfq[non_mlfq["queueLevel"] != 0]
if len(bad_non_mlfq) == 0:
    ok("All non-MLFQ rows have queueLevel = 0")
else:
    fail(f"{len(bad_non_mlfq)} non-MLFQ rows have non-zero queueLevel")

mlfq = data[data["scheduler"] == "MLFQ"]
bad_mlfq = mlfq[~mlfq["queueLevel"].isin([0, 1, 2])]
if len(mlfq) == 0:
    warn("No MLFQ data found")
elif len(bad_mlfq) == 0:
    ok("All MLFQ rows have queueLevel in {0, 1, 2}")
else:
    fail(f"{len(bad_mlfq)} MLFQ rows have invalid queueLevel: "
         f"{bad_mlfq['queueLevel'].unique()}")

# ── check 6: scheduler name matches filename ──────────────────────────────────
print("\n[6] Scheduler name in CSV matches filename?")
mismatches = 0
for f in csv_files:
    base = os.path.basename(f).replace(".csv", "")
    expected = base.split("_")[0]
    df = pd.read_csv(f)
    actual = df["scheduler"].unique()
    if len(actual) != 1 or actual[0] != expected:
        fail(f"{base}: expected '{expected}', got {actual}")
        mismatches += 1
if mismatches == 0:
    ok("All scheduler names match their filenames")

# ── check 7: patron IDs in valid range ───────────────────────────────────────
print("\n[7] Patron IDs in expected range [0, noPatrons-1]?")
problems = 0
for f in csv_files:
    base = os.path.basename(f).replace(".csv", "")
    n = int(base.split("_")[1])
    df = pd.read_csv(f)
    out_of_range = df[df["patronID"] >= n]
    if len(out_of_range) > 0:
        fail(f"{base}: out-of-range patron IDs: {out_of_range['patronID'].unique()}")
        problems += 1
if problems == 0:
    ok("All patron IDs within expected range")

# ── check 8: valid execution times ───────────────────────────────────────────
print("\n[8] Execution times match known drink preparation times?")
invalid = data[~data["execTime"].isin(VALID_EXEC_TIMES)]
if len(invalid) == 0:
    ok(f"All execTime values are valid ({sorted(VALID_EXEC_TIMES)})")
else:
    fail(f"{len(invalid)} rows have unexpected execTime values: "
         f"{sorted(invalid['execTime'].unique())}")

# ── summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"SUMMARY: {passed} passed, {failed} failed")
print(f"Total rows validated: {len(data):,} across {len(csv_files)} files")
print("=" * 60)

if failed > 0:
    print("\n⚠️  Fix the failed checks before submitting.")
else:
    print("\n✅ All checks passed. Data is ready for analysis.")