import base64
import io
from PIL import Image
import numpy as np

def handle(event, context):
    try:
        data = event.body
        if isinstance(data, bytes):
            data = data.decode()
        import json
        payload = json.loads(data)
        img_b64 = payload.get("img")
        if not img_b64:
            return {"statusCode": 400, "body": "No 'img' field in input"}

        img_bytes = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_bytes))

        # In Graustufenbild umwandeln
        img = img.convert("L")
        arr = np.array(img)

        stats = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": int(np.min(arr)),
            "max": int(np.max(arr))
        }

        return {
            "statusCode": 200,
            "body": json.dumps(stats),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
