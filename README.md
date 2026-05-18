# CSC3002F 2026 – OS II Scheduling Assignment
### Allegra the Barman: Comparing Scheduling Policies for Bartending

**Student:** LNGLUL002  
**Course:** CSC3002F – Operating Systems II  
**Lecturer:** M. M. Kuttel

---

## Overview

This project simulates CPU process scheduling using a bar scenario. Patrons (processes) arrive at random times and place drink orders (CPU bursts). Allegra the Barman (the CPU) serves orders according to one of five scheduling algorithms. The simulation is used to experimentally compare algorithm performance across multiple metrics.

**Scheduling algorithms implemented:**

| Code | Algorithm | Description |
|------|-----------|-------------|
| `0` | FCFS | First-Come First-Served |
| `1` | SJF | Shortest Job First |
| `2` | Priority | Lower patron ID = higher priority |
| `3` | MLFQ | Multilevel Feedback Queue with aging |
| `4` | ASJF ⭐ | Adaptive SJF — bonus extension |

---

## Project Structure

```
.
├── src/
│   └── barScheduling/
│       ├── SchedulingSimulation.java   # Main entry point
│       ├── Barman.java                 # Scheduler logic (modified)
│       ├── Patron.java                 # Customer thread (unmodified)
│       └── DrinkOrder.java             # Drink data object (unmodified)
├── bin/                                # Compiled class files
├── results/                            # CSV output from runs
│   └── graphs/                         # Generated analysis graphs
├── Makefile
├── run_experiments.sh                  # Automated experiment runner
├── analyse.py                          # Data analysis and graphing script
└── README.md
```

---

## Building and Running

### Compile and run a single simulation

```bash
make run ARGS="<patrons> <scheduler> <switchTime> <seed>"
```

**Example:**
```bash
make run ARGS="30 2 5 30"
# 30 patrons, Priority scheduling, 5ms switch time, seed 30
```

**Arguments:**

| Argument | Description | Values |
|----------|-------------|--------|
| `patrons` | Number of patron threads | e.g. `10`, `30`, `50` |
| `scheduler` | Scheduling algorithm | `0`=FCFS, `1`=SJF, `2`=Priority, `3`=MLFQ, `4`=ASJF |
| `switchTime` | Context switch overhead (ms) | e.g. `0`, `5` |
| `seed` | RNG seed for reproducible workloads | any integer; `0` = random |

### Clean build artifacts

```bash
make clean
```

> **Note:** `make clean` also removes the `results/` folder. Back up your data first.

---

## Running Experiments

The shell script `run_experiments.sh` automates all runs across all scheduler/patron/seed combinations.

```bash
chmod +x run_experiments.sh
./run_experiments.sh
```

This runs **45 simulations** (5 schedulers × 3 patron counts × 3 seeds) and writes one CSV per run into `results/`. Each CSV is named `SCHEDULER_PATRONS_SEED.csv`, e.g. `MLFQ_30_42.csv`.

To customise the experiment parameters, edit these arrays at the top of `run_experiments.sh`:

```bash
PATRONS=(10 30 50)
SEEDS=(42 123 999)
SCHEDS=(0 1 2 3 4)
```

---

## Output Format

Each CSV file contains one row per completed drink order:

```
scheduler,patronID,drink,execTime,waitTime,turnaroundTime,queueLevel
FCFS,3,Mojito,75,120,195,0
```

| Column | Description |
|--------|-------------|
| `scheduler` | Algorithm name |
| `patronID` | Which patron placed the order |
| `drink` | Drink name |
| `execTime` | Preparation time (ms) — the CPU burst length |
| `waitTime` | Time from order placed to barman starting it (ms) |
| `turnaroundTime` | Time from order placed to completion (ms) |
| `queueLevel` | MLFQ queue level (0/1/2); always `0` for other schedulers |

**Metric relationships:**
```
waitTime       = serviceStartTime - arrivalTime
turnaroundTime = completionTime   - arrivalTime
turnaroundTime ≈ waitTime + execTime  (small overhead from real clock)
```

---

## Analysis

Once results are generated, run the analysis script to produce all graphs:

```bash
python3 analyse.py
```

Requires: `pandas`, `matplotlib`, `numpy`
```bash
pip install pandas matplotlib numpy
```

Graphs are saved to `results/graphs/`:

| File | Description |
|------|-------------|
| `fig1_waittime_boxplot.png` | Wait time distribution per scheduler (log scale) |
| `fig2_turnaround_boxplot.png` | Turnaround time distribution per scheduler |
| `fig3_scaling_waittime.png` | Mean & median wait time vs patron count |
| `fig4_starvation.png` | % orders waiting >3 s, by scheduler and patron count |
| `fig5_mlfq_queues.png` | MLFQ wait time broken down by queue level |
| `fig6_summary_table.png` | Summary statistics table |

---

## Bonus Extension — Adaptive SJF (ASJF)

ASJF is an improved scheduling algorithm designed to fix SJF's starvation problem while preserving its low average wait time.

**How it works:** each order is assigned an *effective burst time* that shrinks the longer the order waits in the queue:

```
effectiveBurst = execTime - (timeWaited / BOOST_FACTOR)
```

The barman always serves the order with the lowest effective burst. Short orders are still served first under low load, but long orders gradually rise in priority as they wait — preventing indefinite starvation. With `BOOST_FACTOR=8`, no order waits longer than ~1.6 seconds before it overtakes all newly-arrived orders.

**Key difference from plain SJF:** SJF sorts orders once at insertion time. ASJF re-evaluates priorities dynamically every time the barman picks the next order, by draining the queue into a list and selecting the current minimum.

---

## Key Results Summary

| Scheduler | Mean Wait | Median Wait | Std Dev | Max Wait | Starvation (>3s) |
|-----------|-----------|-------------|---------|----------|------------------|
| FCFS | 1192 ms | 772 ms | 1611 ms | 9742 ms | 2.9% |
| SJF | 674 ms | 60 ms | 1671 ms | 9956 ms | 8.4% |
| Priority | 775 ms | 71 ms | 1926 ms | 10464 ms | 9.3% |
| MLFQ | 1040 ms | 665 ms | 1067 ms | 5773 ms | 2.5% |
| **ASJF** | 924 ms | 692 ms | 879 ms | 4070 ms | 1.6% |

**Recommendation:** ASJF is proposed as the best overall algorithm — it targets SJF's starvation weakness directly while retaining low median wait times, making it the most suitable choice for a bar setting where both speed and fairness matter.

---

## Modifications Made

`Barman.java` and `SchedulingSimulation.java` were modified from the provided template:

- **`Barman.java`** — `recordCompletedOrder()` implemented to write per-order metrics to CSV. ASJF scheduler added as `case 4` (bonus extension), including `asjfQueue`, `effectiveBurst()`, `takeNextASJFOrder()`, and `runASJF()`.
- **`SchedulingSimulation.java`** — `validateScheduler()` and `schedulerName()` updated to accept and name scheduler `4` (ASJF).

`DrinkOrder.java` and `Patron.java` are unchanged from the provided template.

---

## AI Usage

Claude (Anthropic) was used for coding assistance during this assignment — specifically for implementing `recordCompletedOrder()`, designing and implementing the ASJF bonus algorithm, writing `run_experiments.sh`, and generating `analyse.py`. All experimental runs, data, graphs, and conclusions are based on actual simulation outputs. No AI tool was used to fabricate data or invent results.