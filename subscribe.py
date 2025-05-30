from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from urllib.parse import unquote
from main import initialize_subscription

app = FastAPI()

ACCESS_TOKEN = initialize_subscription()

@app.post("/notifications")
async def receive_notifications(request: Request):
    validation_token = request.query_params.get("validationToken")

    if validation_token:
        decoded_token = unquote(validation_token)
        print("[Webhook] Validation token received:", decoded_token)
        return PlainTextResponse(content=decoded_token, status_code=200)

    try:
        body = await request.json()
        print("[Webhook] Raw payload received:", body)

        for item in body.get("value", []):
            message_id = item.get("resourceData", {}).get("id")
            if message_id:
                message_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

                response = requests.get(message_url, headers=headers)
                if response.status_code == 200:
                    message = response.json()
                    print(f"\n📧 New/Updated Email Received:")
                    print("From   :", message.get('from', {}).get('emailAddress', {}).get('address'))
                    print("Subject:", message.get('subject'))
                    print("Body Preview:", message.get('bodyPreview'))
                else:
                    print("[Webhook] Failed to fetch message:", response.status_code, response.text)

        return {"status": "ok"}

    except Exception as e:
        print("[Webhook] Error parsing request:", str(e))
        return {"error": "Invalid or missing JSON body"}
