import requests
import os
import time
from dotenv import load_dotenv
import re
from selenium import webdriver
from bs4 import BeautifulSoup

os.environ['ONEMAP_EMAIL'] = "resaleranger1@gmail.com"
os.environ['ONEMAP_EMAIL_PASSWORD'] = "Denisthegoat3101"

# Load environment variables
load_dotenv()

# Constants
TOKEN_URL = "https://www.onemap.gov.sg/api/auth/post/getToken"
GEOCODE_URL = "https://www.onemap.gov.sg/api/common/elastic/search"
TOKEN_EXPIRY_SECONDS = 72 * 3600  # 3 days

# Global token cache
token_data = {
    'access_token': None,
    'timestamp': 0
}

def get_new_token():
    """Get a fresh token using OneMap credentials."""
    payload = {
        "email": os.environ['ONEMAP_EMAIL'],
        "password": os.environ['ONEMAP_EMAIL_PASSWORD']
    }

    response = requests.post(TOKEN_URL, json=payload)
    token_json = response.json()

    print("🧾 Token API Response:", token_json)  # Debug print (optional)

    if response.status_code == 200 and 'access_token' in token_json:
        token_data['access_token'] = token_json['access_token']  # <-- fixed key name
        token_data['timestamp'] = time.time()
        return token_json['access_token']
    else:
        raise Exception(f"Token fetch failed: {response.status_code} | {token_json}")


def get_valid_token():
    """Check if token is still valid or refresh it."""
    if token_data['access_token'] is None or (time.time() - token_data['timestamp']) > TOKEN_EXPIRY_SECONDS:
        return get_new_token()
    return token_data['access_token']

def extract_postal_code(address):
    """Extract 6-digit postal code from address string (Singapore-style)."""
    match = re.search(r"\b\d{6}\b", address)
    return match.group(0) if match else "Not found"

def geocode_address(address):
    """Perform geocoding for a given address string."""
    token = get_valid_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "searchVal": address,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": 1
    }

    response = requests.get(GEOCODE_URL, headers=headers, params=params)

    # Token expired? Refresh and retry once
    if response.status_code == 401:
        print("Token expired, refreshing...")
        token = get_new_token()
        headers["Authorization"] = f"Bearer {token}"
        response = requests.get(GEOCODE_URL, headers=headers, params=params)

    if response.status_code == 200:
        result = response.json()
        if result['found'] > 0:
            data = result['results'][0]
            address_text = data.get('ADDRESS', "")
            postal_code = data.get("POSTALCODE")
            if not postal_code:
                postal_code = extract_postal_code(address_text)
            return {
        "address": address_text,
        "latitude": data.get("LATITUDE"),
        "longitude": data.get("LONGITUDE"),
        "postal_code": postal_code
        }
        else:
            return {"error": "No matching result found."}
    else:
        raise Exception(f"Geocode failed: {response.status_code}, {response.text}")
    
## Example usage
#f __name__ == "__main__":
#    input_address = "1 Marina Boulevard, Singapore"  # replace with any address
#    result = geocode_address(input_address)
#    print(result)