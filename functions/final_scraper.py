import requests
import os
import time
from dotenv import load_dotenv
import re
from selenium import webdriver
from bs4 import BeautifulSoup, Comment
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

#api token check
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

    #print("Token API Response:", token_json)  # Debug print (optional)

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

#flat type conversion
def map_flat_type(flat_str: str):
    """
    Returns a tuple: (one-hot list, readable label)
    """
    s = flat_str.strip().upper()

    if s.startswith('1'):
        return [1,0,0,0,0,0,0], "1 ROOM"
    elif s.startswith('2'):
        return [0,1,0,0,0,0,0], "2 ROOM"
    elif s.startswith('3'):
        return [0,0,1,0,0,0,0], "3 ROOM"
    elif s.startswith('4'):
        return [0,0,0,1,0,0,0], "4 ROOM"
    elif s.startswith('5'):
        return [0,0,0,0,1,0,0], "5 ROOM"
    elif s.startswith('EA') or s.startswith('E'):
        return [0,0,0,0,0,1,0], "EXECUTIVE"
    elif s.startswith('MG'):
        return [0,0,0,0,0,0,1], "MULTI-GENERATION"
    else:
        return "UNKNOWN", "UNKNOWN"
    
# propguru gives area in terms of sqft
def get_sqft_sqm(area_sqft):
    ratio = 0.092903
    area_sqm = round(area_sqft * ratio)

    return area_sqm

def extract_sqft_number(area_str):
    # Remove commas and extract the numeric part before "sqft"
    match = re.search(r"[\d,]+", area_str)
    if match:
        return int(match.group(0).replace(",", ""))
    return None  # if not matched


def scraper_guru(input_link):
    # --- Step 1: Launch browser and scrape page ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.get(input_link)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # --- Step 2: Scrape data ---
    address_tag = soup.find("span", class_="full-address__address")
    address = address_tag.get_text(strip=True) if address_tag else ""

    #listed price
    price_tag = soup.find("h2", class_="amount", attrs={"data-automation-id": "overview-price-txt"})
    listed_price = price_tag.get_text(strip=True) if price_tag else ""

    #HDB type
    hdb_type_tag = soup.find("div", class_="meta-table__item__wrapper__value", string=re.compile("HDB for sale"))
    hdb_type = hdb_type_tag.get_text(strip=True) if hdb_type_tag else ""
    flat_type_encoded, flat_type_label = map_flat_type(hdb_type) if hdb_type else ("UNKNOWN", "UNKNOWN")

    #lease year
    lease_year_tag = soup.find("div", class_="meta-table__item__wrapper__value", string=re.compile("^TOP in"))
    lease_year = ""
    remaining_lease = ""

    if lease_year_tag:
        text_val = lease_year_tag.get_text(strip=True)
        match = re.search(r"\b\d{4}\b", text_val)
        if match:
            lease_year = int(match.group(0))        #remaining lease year conversion
            remaining_lease = 99 - (2025 - lease_year)
    
    #sqft -> sqm
    amenity_tags = soup.find_all("h4", class_="amenity__text")
    
    sqft = ""
    # Check if we have at least three such elements
    if len(amenity_tags) >= 3:
        # The third element (index 2) is where sqft is located
        sqft_tag = amenity_tags[2]
        
        # Approach: extract text from the tag while ignoring comment nodes
        lines = []
        for element in sqft_tag.descendants:
            if isinstance(element, Comment):
                continue
            if element.string and element.string.strip():
                lines.append(element.string.strip())
                
        # Debug print to inspect what we got:
        # print("Extracted lines:", lines)
        
        # Expecting something like: ['1,109 == $0', 'sqft']
        if len(lines) >= 2:
            # Extract the number using regex from the first part
            match = re.search(r'([\d,]+)', lines[0])
            if match and "sqft" in lines[1].lower():
                sqft_number = match.group(1)
                sqft = f"{sqft_number} sqft"
        else:
            # Fallback: try to extract using the entire text content
            text_val = sqft_tag.get_text(separator=" ", strip=True)
            match = re.search(r'([\d,]+).*?sqft', text_val, re.IGNORECASE)
            if match:
                sqft = f"{match.group(1)} sqft"

    floor_area_sqm = get_sqft_sqm(extract_sqft_number(sqft))

    driver.quit()

    # --- Step 3: Geocode using OneMap ---
    token = get_valid_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "searchVal": address,
        "returnGeom": "Y",
        "getAddrDetails": "Y",
        "pageNum": 1
    }

    response = requests.get(GEOCODE_URL, headers=headers, params=params)
    #if expire get new token
    if response.status_code == 401:
        print("Token expired, refreshing...")
        token = get_new_token()
        headers["Authorization"] = f"Bearer {token}"
        response = requests.get(GEOCODE_URL, headers=headers, params=params)

    latitude, longitude, postal_code, matched_address = None, None, None, None
    #geocode
    if response.status_code == 200:
        result = response.json()
        if result.get("found", 0) > 0:
            data = result['results'][0]
            matched_address = data.get("ADDRESS", "")
            latitude = data.get("LATITUDE")
            longitude = data.get("LONGITUDE")
            postal_code = data.get("POSTALCODE") or extract_postal_code(matched_address)
        else:
            print(f"No geocode result found for: {address}")
    else:
        raise Exception(f"Geocode failed: {response.status_code}, {response.text}")

    # --- Step 4: Return all combined data ---
    return {
        "address": address,
        "listed_price": listed_price,
        "flat_type_encoded": flat_type_encoded,
        "flat_type_label": flat_type_label,
        "lease_year": lease_year,
        "remaining_lease_year": remaining_lease,
        "floor_area_sqm": floor_area_sqm,
        "latitude": latitude,
        "longitude": longitude,
        "postal_code": str(int(postal_code))
    }


