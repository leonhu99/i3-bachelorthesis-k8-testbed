import re
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

if len(sys.argv) != 3:
    print(f"Usage: py {os.path.basename(sys.argv[0])} <logfile> \"<plot_title>\"")
    sys.exit(1)

filename = sys.argv[1]
plot_title = sys.argv[2]

# read log file
with open(filename, "r") as f:
    log = f.read()

# extract times for each iteration
preproc_times = [float(x) for x in re.findall(r"image-preprocess: ([\d\.]+) s", log)]
filter_times  = [float(x) for x in re.findall(r"image-filter: ([\d\.]+) s", log)]
stats_times   = [float(x) for x in re.findall(r"image-stats: ([\d\.]+) s", log)]
total_times   = [float(x) for x in re.findall(r"Total pipeline time: ([\d\.]+) s", log)]

# check if all lists are non-empty
if not all([preproc_times, filter_times, stats_times, total_times]):
    print("Error: One or more time lists are empty. Please check the log file.")
    sys.exit(1)

# convert to ms
preproc_times = [t * 1000 for t in preproc_times]
filter_times  = [t * 1000 for t in filter_times]
stats_times   = [t * 1000 for t in stats_times]
total_times   = [t * 1000 for t in total_times]

# compute statistics
means = [
    np.mean(preproc_times),
    np.mean(filter_times),
    np.mean(stats_times),
    np.mean(total_times)
]
stds = [
    np.std(preproc_times, ddof=1),
    np.std(filter_times, ddof=1),
    np.std(stats_times, ddof=1),
    np.std(total_times, ddof=1)
]

functions = ["image-preprocess", "image-filter", "image-stats", "total"]
x = np.arange(len(functions))

plt.figure(figsize=(8,5))
plt.bar(x, means, yerr=stds, capsize=6, color=["#0072B2", "#E69F00", "#009E73", "#999999"])
plt.xticks(x, functions)

#plt.ylabel("Execution Time [ms]")
plt.yscale("log")
plt.ylabel("Execution Time [ms] (log scale)")

plt.title(plot_title)

# annotate means + stds on top of bars
for i, (mean, std) in enumerate(zip(means, stds)):
    offset = max(5, std + 2)  # Minimum 5ms offset to avoid overlap
    plt.text(i, mean + offset, f"{mean:.1f}ms ± {std:.1f}ms", ha='center', va='bottom', fontsize=10)


#plt.tight_layout()
out_file = f"plot_{plot_title.replace(' ','_')}.pdf"
plt.savefig(out_file, dpi=300)
print(f"Plot saved as {out_file}")
