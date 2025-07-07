import re
import numpy as np
import os

LOG_FILE = "logs/pipeline_times.log"

# Regular Expressions
rx_run = re.compile(r"^---\nRun #(?P<run>\d+) at (?P<date>.+)$", re.MULTILINE)
rx_total = re.compile(r"Total pipeline time:\s*([\d.]+) s")
rx_func = re.compile(r"([a-zA-Z0-9\-_]+):\s*([\d.]+) s")

# Read and split the log file into blocks
with open(LOG_FILE, "r") as f:
    content = f.read()

blocks = content.strip().split("\n---\n")
runs = []
for block in blocks:
    if not block.strip():
        continue
    lines = block.strip().splitlines()
    run = {}
    for line in lines:
        m_total = rx_total.search(line)
        if m_total:
            run["total"] = float(m_total.group(1))
        m_func = rx_func.search(line)
        if m_func and m_func.group(1) != "Total pipeline time":
            run[m_func.group(1)] = float(m_func.group(2))
    if run:
        runs.append(run)

# Automatically detect functions in log
all_funcs = set()
for run in runs:
    all_funcs.update(run.keys())
all_funcs.discard("total")
all_funcs = sorted(all_funcs)

# Statistical analysis
def stats(arr):
    arr = np.array(arr)
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)
    median = np.median(arr)
    ci95 = 1.96 * std / np.sqrt(len(arr)) if len(arr) > 1 else 0
    return {
        "mean": mean,
        "std": std,
        "median": median,
        "min": np.min(arr),
        "max": np.max(arr),
        "n": len(arr),
        "ci95": ci95
    }

# Extract stats
all_stats = {}
for key in ["total"] + all_funcs:
    values = [run.get(key) for run in runs if key in run]
    if values:
        all_stats[key] = stats(values)

# Print results
print("Pipeline Timing Statistics (all values in seconds):\n")
for key in ["total"] + all_funcs:
    if key not in all_stats: continue
    s = all_stats[key]
    print(f"{key:>20}: mean={s['mean']:.4f}, std={s['std']:.4f}, median={s['median']:.4f}, min={s['min']:.4f}, max={s['max']:.4f}, n={s['n']}, 95%-CI=±{s['ci95']:.4f}")

# Optional: Write to CSV
import csv
CSV_OUT = "logs/pipeline_analysis.csv"
with open(CSV_OUT, "w", newline='') as f:
    w = csv.writer(f)
    w.writerow(["step", "mean", "std", "median", "min", "max", "n", "ci95_95"])
    for key in ["total"] + all_funcs:
        if key in all_stats:
            s = all_stats[key]
            w.writerow([key, s['mean'], s['std'], s['median'], s['min'], s['max'], s['n'], s['ci95']])
print(f"\nStatistics also saved to {CSV_OUT}")
