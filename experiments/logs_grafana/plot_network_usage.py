import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import re

def parse_throughput(s):
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).replace("B/s", "").strip()
    match = re.match(r"([0-9\.,]+)\s*([kKmMgG]?)", s)
    if not match:
        return float('nan')
    num, unit = match.groups()
    num = float(num.replace(',', '.'))
    if unit.lower() == "k":
        num *= 1_000
    elif unit.lower() == "m":
        num *= 1_000_000
    elif unit.lower() == "g":
        num *= 1_000_000_000
    return num

def safe_filename(title, prefix="plot_network_usage_"):
    fname = re.sub(r'[^a-zA-Z0-9_-]+', '_', title)
    fname = re.sub(r'_+', '_', fname).strip('_')
    return f"{prefix}{fname}.pdf"

if len(sys.argv) < 5:
    print(f"Usage: python3 {os.path.basename(sys.argv[0])} <plot_title> <start_time-end_time> <csv1> <csv2> [<csv3> ...]")
    print("Example: python3 plot_network_usage.py \"Network Usage RX/TX (N=50)\" 11:42:00-11:43:45 rx.csv tx.csv")
    sys.exit(1)

plot_title = sys.argv[1]
time_range = sys.argv[2]
csv_files = sys.argv[3:]

start_time, end_time = time_range.split("-")

fixed_colors = {
    "rx": "#0072B2",
    "tx": "#E69F00",
}

plt.figure(figsize=(10,5))

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    value_col = df.columns[1]
    if "rx" in csv_file.lower() or "rx" in value_col.lower():
        label = "RX"
        color = fixed_colors["rx"]
    elif "tx" in csv_file.lower() or "tx" in value_col.lower():
        label = "TX"
        color = fixed_colors["tx"]
    else:
        label = os.path.basename(csv_file)
        color = "#333333"

    # Convert to Mbps (B/s * 8 / 1_000_000)
    df["Throughput"] = df[value_col].apply(parse_throughput) * 8 / 1_000_000
    df["Time"] = pd.to_datetime(df["Time"])
    mask = (df["Time"].dt.time >= pd.to_datetime(start_time).time()) & \
           (df["Time"].dt.time <= pd.to_datetime(end_time).time())
    df_filtered = df.loc[mask].copy()
    if df_filtered.empty:
        print(f"No data in range for {csv_file}, skipping.")
        continue
    t0 = df_filtered["Time"].iloc[0]
    df_filtered["seconds"] = (df_filtered["Time"] - t0).dt.total_seconds()
    plt.plot(df_filtered["seconds"], df_filtered["Throughput"], label=label, color=color, linewidth=2)

plt.xlabel("Time [s]")
plt.ylabel("Throughput [Mbps] (log scale)")
plt.yscale("log")
plt.title(plot_title)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
out_file = safe_filename(plot_title)
plt.savefig(out_file, dpi=300)
print(f"Plot saved as {out_file}")
