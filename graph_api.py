import requests
import datetime

def create_subscription(access_token: str, notification_url: str) -> dict:
    """
    Create a Microsoft Graph subscription to listen for updates in the inbox.
    Subscription duration is 1 hour (max allowed for /me/mailFolders).
    """
    expiration_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat() + "Z"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "changeType": "updated",
        "notificationUrl": notification_url,
        "resource": "/me/mailFolders('inbox')/messages",
        "expirationDateTime": expiration_time,
        "clientState": "SecretClientState"
    }

    response = requests.post("https://graph.microsoft.com/v1.0/subscriptions", headers=headers, json=payload)
    print(f"[GraphAPI] Status: {response.status_code}")
    print("[GraphAPI] Response:", response.json())

    return response.json()
