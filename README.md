# CSC3002F 2026 – OS II Scheduling Assignment
### Allegra the Barman: Comparing Scheduling Policies for Bartending

**Student:** LNGLUL002  
**Course:** CSC3002F (Networks & Operating Systems)

---

## Overview

This project simulates CPU process scheduling using a bar scenario. Patrons (processes) arrive at random times and place drink orders (CPU bursts). Allegra the Barman (the CPU) serves orders according to one of four scheduling algorithms. The simulation is used to experimentally compare algorithm performance across multiple metrics.

**Scheduling algorithms implemented:**

| Code | Algorithm | Description |
|------|-----------|-------------|
| `0` | FCFS | First-Come First-Served |
| `1` | SJF | Shortest Job First |
| `2` | Priority | Lower patron ID = higher priority |
| `3` | MLFQ | Multilevel Feedback Queue with aging |

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
| `scheduler` | Scheduling algorithm | `0`=FCFS, `1`=SJF, `2`=Priority, `3`=MLFQ |
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

This runs **36 simulations** (4 schedulers × 3 patron counts × 3 seeds) and writes one CSV per run into `results/`. Each CSV is named `SCHEDULER_PATRONS_SEED.csv`, e.g. `MLFQ_30_42.csv`.

To customise the experiment parameters, edit these arrays at the top of `run_experiments.sh`:

```bash
PATRONS=(10 30 50)
SEEDS=(42 123 999)
SCHEDS=(0 1 2 3)
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
waitTime      = serviceStartTime - arrivalTime
turnaroundTime = completionTime  - arrivalTime
turnaroundTime ≈ waitTime + execTime  (small overhead from real clock)
```

---

## Analysis

Once results are generated, run the analysis script to produce all graphs:

```bash
python3 analyse.py
```

Requires: `pandas`, `matplotlib`, `numpy`  

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

## Key Results Summary

| Scheduler | Mean Wait | Median Wait | Std Dev | Max Wait | Starvation (>3s) |
|-----------|-----------|-------------|---------|----------|------------------|
| FCFS | 1192 ms | 772 ms | 1611 ms | 9742 ms | 2.9% |
| SJF | 674 ms | 60 ms | 1671 ms | 9956 ms | 8.4% |
| Priority | 775 ms | 71 ms | 1926 ms | 10464 ms | 9.3% |
| **MLFQ** | 1040 ms | 665 ms | **1067 ms** | 5773 ms | **2.5%** |

**Recommendation:** MLFQ offers the best balance of fairness, predictability, and starvation resistance for a bar setting. SJF achieves the lowest median wait but causes significant starvation for long drinks at high load.

---

## Modifications Made

Only `Barman.java` was modified, as permitted by the assignment specification. The single change is the implementation of `recordCompletedOrder()`, which appends a CSV row to the results file after each drink is served.

All other files (`DrinkOrder.java`, `Patron.java`, `SchedulingSimulation.java`) are unchanged from the provided template.

---

## AI Usage

GitHub Copilot and Claude (Anthropic) were used for coding assistance, specifically for implementing `recordCompletedOrder()`, writing the shell automation script, and generating the Python analysis and graphing code. All experimental runs, data, and conclusions are based on actual simulation outputs.
