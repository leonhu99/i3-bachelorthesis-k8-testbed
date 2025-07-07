import requests
import base64
from concurrent.futures import ThreadPoolExecutor

FAAS_URL = "http://172.16.44.202:8081/function/image-preprocess"
IMG_PATH = "testimg.jpg"
N_PARALLEL = 100  # number of parallel requests

def send_request():
    with open(IMG_PATH, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    resp = requests.post(FAAS_URL, json={"img": img_b64})
    print(f'status_code: {resp.status_code}, time_elapsed: {resp.elapsed.total_seconds()}')

with ThreadPoolExecutor(max_workers=N_PARALLEL) as executor:
    for _ in range(N_PARALLEL):
        executor.submit(send_request)
