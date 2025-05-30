from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from urllib.parse import unquote
import requests
import os
from auth import acquire_token

app = FastAPI()

ACCESS_TOKEN =  acquire_token() 

@app.post("/notifications")
async def receive_notifications(request: Request):
    validation_token = request.query_params.get("validationToken")

    if validation_token:
        decoded_token = unquote(validation_token)
        print("Validation token:", decoded_token)
        return PlainTextResponse(content=decoded_token, status_code=200)
    try:
        body = await request.json()
        print("webhook received:", body)
        for item in body.get("value", []):
            message_id = item.get("resourceData", {}).get("id")
            if message_id:
                message_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                response = requests.get(message_url, headers=headers)
                if response.status_code == 200:
                    message = response.json()
                    print("\nNew/Updated Email Received:")
                    print("From   :", message.get('from', {}).get('emailAddress', {}).get('address'))
                    print("Subject:", message.get('subject'))
                    print("Body Preview:", message.get('bodyPreview'))
                    has_attachments = message.get("hasAttachments", False)
                    print("Has Attachments :" ,has_attachments)
                    if has_attachments:
                        attachments_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments"
                        attachments_resp = requests.get(attachments_url,headers=headers)

                        if attachments_resp.status_code == 200:
                            attachments = attachments_resp.json().get("value", [])
                            for att in attachments:
                                print("- Name:", att.get("name"))
                                print("- Type:", att.get("@odata.type"))
                                print("- Size:", att.get("size"), "bytes")
                                content_bytes = att.get("contentBytes")
                                if content_bytes:
                                    import base64
                                    file_data = base64.b64decode(content_bytes)
                                    file_name = att.get("name")
                                    with open(file_name, "wb") as f:
                                        f.write(file_data)
                                    print(f"[Download] Saved attachment as {file_name}")
                else:
                    print("[Webhook] Failed to fetch message:", response.status_code, response.text)
        return {"status": "ok"}
    except Exception as e:
        print("[Webhook] Error parsing request:", str(e))
        return {"error": "Invalid or missing JSON body"}
