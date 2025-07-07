import requests
import base64
import json
import os
import time

# OpenFaaS gateway address
GATEWAY = "http://172.16.44.202:8081"

OUTPUT_DIR = "output"
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "pipeline_times.log")
N_ITERATIONS = 50

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def invoke_function(function_name, data):
    start = time.time()
    url = f"{GATEWAY}/function/{function_name}"
    resp = requests.post(url, json=data)
    duration = time.time() - start
    try:
        return resp.json(), duration
    except Exception:
        print(f"Invalid response from {function_name}: {resp.text}")
        return None, duration

def main():
    # 1. Load and encode the input image as base64
    with open("testimg.jpg", "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    payload = {"img": img_b64}

    for i in range(1, N_ITERATIONS + 1):
        print(f"\n--- Iteration {i} ---")
        times = {}
        overall_start = time.time()

        # 2. Call image-preprocess
        print("Calling image-preprocess ...")
        res1, t1 = invoke_function("image-preprocess", payload)
        times["image-preprocess"] = t1
        if not res1 or "img" not in res1:
            print("Error in image-preprocess.")
            continue

        # 3. Call image-filter
        print("Calling image-filter ...")
        res2, t2 = invoke_function("image-filter", {"img": res1["img"]})
        times["image-filter"] = t2
        if not res2 or "img" not in res2:
            print("Error in image-filter.")
            continue

        # Save the filtered image (optional)
        filtered_image_name = os.path.join(OUTPUT_DIR, f"filtered_pipeline_{i}.jpg")
        with open(filtered_image_name, "wb") as out:
            out.write(base64.b64decode(res2["img"]))

        # 4. Call image-stats
        print("Calling image-stats ...")
        res3, t3 = invoke_function("image-stats", {"img": res2["img"]})
        times["image-stats"] = t3
        if not res3:
            print("Error in image-stats.")
            continue

        overall_duration = time.time() - overall_start

        # 5. Output the statistics
        print("\nImage statistics result:")
        print(json.dumps(res3, indent=2))

        print(f"\nFiltered image has been saved as {filtered_image_name}.")

        # 6. Log the timings
        with open(LOG_FILE, "a") as logf:
            logf.write(f"\n---\nRun #{i} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            logf.write(f"Total pipeline time: {overall_duration:.4f} s\n")
            for func, t in times.items():
                logf.write(f"{func}: {t:.4f} s\n")

        print(f"Timings have been logged in {LOG_FILE}.")

if __name__ == "__main__":
    main()
