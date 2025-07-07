import base64
import io
from PIL import Image, ImageFilter

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

        # Beispiel: Graustufen + Kantenfilter
        img = img.convert("L")
        img = img.filter(ImageFilter.FIND_EDGES)

        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        out_b64 = base64.b64encode(buf.read()).decode()
        return {
            "statusCode": 200,
            "body": json.dumps({"img": out_b64}),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
