import requests
import base64

GATEWAY = "http://172.16.44.202:8081"
IMG_PATH = "testimg.jpg"
OUT_PATH = "resized.jpg"

# load image and encode in base64
with open(IMG_PATH, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# call image-preprocess
url = f"{GATEWAY}/function/image-preprocess"
response = requests.post(url, json={"img": img_b64})
response.raise_for_status()
data = response.json()

# decode result and save resized iamge
with open(OUT_PATH, "wb") as out_f:
    out_f.write(base64.b64decode(data["img"]))

print(f"Image saved as {OUT_PATH}")
