import asyncio
from auth import acquire_token
from graph_api import create_subscription

async def initialize_subscription():
    access_token = acquire_token()
    print(access_token)
    print("[Main] Access token acquired.")

    # Replace this with your actual ngrok URL
    public_webhook_url = "https://2ceb-183-82-117-42.ngrok-free.app/notifications"

    subscription_result = create_subscription(access_token, public_webhook_url)
    print("[Main] Subscription created:", subscription_result)
    return access_token

async def main():
    await initialize_subscription()

if __name__ == "__main__":
    asyncio.run(main())
