import os
from dotenv import load_dotenv

load_dotenv()

POE_API_KEY = os.getenv("POE_API_KEY")
POE_BASE_URL = "https://api.poe.com/v1"
POE_MODEL = os.getenv("POE_MODEL", "gpt-5")

if not POE_API_KEY:
    raise ValueError("Missing POE_API_KEY in environment")