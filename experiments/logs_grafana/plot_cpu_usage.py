import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

if len(sys.argv) < 5:
    print(f"Usage: python3 {os.path.basename(sys.argv[0])} <plot_title> <start_time-end_time> <csv1> <csv2> [<csv3> ...]")
    print("Example: python3 plot_cpu_usage.py \"CPU Usage (N=50)\" 11:42:00-11:43:45 file1.csv file2.csv file3.csv")
    sys.exit(1)

plot_title = sys.argv[1]
time_range = sys.argv[2]
csv_files = sys.argv[3:]

start_time, end_time = time_range.split("-")

# Hardcoded color map (function name -> color)
fixed_colors = {
    "image-preprocess": "#0072B2",  # Blue
    "image-filter": "#E69F00",      # Orange
    "image-stats": "#009E73",       # Green
    # Optional: add more function-color pairs here
}

plt.figure(figsize=(10,5))

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    cpu_col = df.columns[1]
    func_name = cpu_col.split('-')[0] + '-' + cpu_col.split('-')[1]
    df["cpu"] = df[cpu_col].str.replace(" cores", "").astype(float)
    df["Time"] = pd.to_datetime(df["Time"])
    mask = (df["Time"].dt.time >= pd.to_datetime(start_time).time()) & \
           (df["Time"].dt.time <= pd.to_datetime(end_time).time())
    df_filtered = df.loc[mask].copy()
    t0 = df_filtered["Time"].iloc[0]
    df_filtered["seconds"] = (df_filtered["Time"] - t0).dt.total_seconds()
    color = fixed_colors.get(func_name, "#333333")  # fallback dark grey
    plt.plot(df_filtered["seconds"], df_filtered["cpu"], label=func_name, color=color, linewidth=2)

plt.xlabel("Time [s]")
plt.yscale("log")

plt.ylabel("CPU Usage [cores] (log scale)")


plt.title(plot_title)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

out_file = f"plot_cpu_usage_{plot_title.replace(' ','_')}.pdf"
plt.savefig(out_file, dpi=300)
print(f"Plot saved as {out_file}")