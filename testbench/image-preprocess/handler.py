import base64
import io
from PIL import Image

def handle(event, context):
    # Input: JSON mit base64-Bild (z.B. {"img": "...."})
    try:
        data = event.body
        if isinstance(data, bytes):
            data = data.decode()

        import json
        payload = json.loads(data)
        img_b64 = payload.get("img")
        if not img_b64:
            return {
                "statusCode": 400,
                "body": "No 'img' field in input"
            }

        img_bytes = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_bytes))

        # Beispiel: Bild skalieren auf 100x100 Pixel
        img = img.resize((100, 100))

        # In JPEG exportieren und wieder in base64 kodieren
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        out_b64 = base64.b64encode(buf.read()).decode()

        # Output als JSON zurückgeben
        return {
            "statusCode": 200,
            "body": json.dumps({"img": out_b64}),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
