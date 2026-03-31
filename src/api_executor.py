import os
import requests
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

STRIPE_BASE_URL = "https://api.stripe.com"
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")


def execute_request(method: str, endpoint: str, params: dict = None) -> dict:
    url = STRIPE_BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {STRIPE_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params or {})
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, data=params or {})
        else:
            return {"error": f"Unsupported method: {method}"}

        return response.json()

    except Exception as e:
        return {"error": str(e)}