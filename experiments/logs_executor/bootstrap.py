import numpy as np
import sys

def compute_bootstrap(arr):
    """
    Berechnet das 95%-Konfidenzintervall für den Mittelwert eines Arrays
    mittels Bootstrap-Methode.
    """
    if len(arr) == 0:
        raise ValueError("Das Array darf nicht leer sein.")
    
    N_bootstrap = 10000
    means = np.empty(N_bootstrap)
    for i in range(N_bootstrap):
        resample = np.random.choice(arr, size=len(arr), replace=True)
        means[i] = resample.mean()

    lower = np.percentile(means, 2.5)
    upper = np.percentile(means, 97.5)

    return lower, upper, means.mean()

def parse_log_file(file_path):
    total_times = []
    with open(file_path, 'r') as file:
        for line in file:
            if "Total pipeline time:" in line:
                # Zeit extrahieren und in Millisekunden umwandeln
                total_time = float(line.split(': ')[1].strip().replace(' s', '')) * 1000
                total_times.append(total_time)
    return np.array(total_times)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bootstrap.py <log_file_path>")
        sys.exit(1)
    log_file_path = sys.argv[1]
    try:
        total_times = parse_log_file(log_file_path)
        if total_times.size == 0:
            print("Keine 'Total pipeline time' in der Log-Datei gefunden.")
            sys.exit(1)

        lower, upper, mean = compute_bootstrap(total_times)
        print(f"95%-Konfidenzintervall: [Lower: {lower:.2f} ms, Upper: {upper:.2f} ms]")
        print(f"Durchschnittliche Zeit: {mean:.2f} ms")

    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)
