import os
from dotenv import load_dotenv
from atproto import Client

load_dotenv()


BS_USERNAM = os.getenv("BLUESKY_USERNAM")
BS_PASSWORD = os.getenv("BLUESKY_PASSWORD")


print(f"Username: {BS_USERNAM}")
print(f"Password: {BS_PASSWORD}")
try:
    client = Client()
    client.login(BS_USERNAM, BS_PASSWORD)
    print("Authentication successful!")
except Exception as e:
    print(f"Authentication failed: {e}")
