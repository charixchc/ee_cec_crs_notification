import os
import requests
import re
from datetime import datetime
from supabase import create_client, Client

# Load credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Ensure credentials are available
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing Supabase credentials! Ensure SUPABASE_URL and SUPABASE_KEY are set.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Express Entry draw data URL
DATA_URL = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_en.json"

def fetch_data():
    """Fetch the latest Express Entry draw data."""
    response = requests.get(DATA_URL)
    response.raise_for_status()
    return response.json()

def dynamic_extract(text, start_delimiter=None, end_delimiter=None, substring=None):
    if substring:
        pattern = re.escape(substring) + r'(.*)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    elif start_delimiter and end_delimiter:
        pattern = re.escape(start_delimiter) + r'(.*?)' + re.escape(end_delimiter)
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None
    
def transform_datetime(date_str):
    try:
        input_format = "%B %d, %Y at %H:%M:%S %Z"
        dt = datetime.strptime(date_str, input_format)
        output_format = "%Y-%m-%dT%H:%M:%S%z"
        return dt.strftime(output_format)
    except ValueError:
        return ""

def transform_data(data):
    """Transform the JSON response into a structured format."""
    latest_draw = data["rounds"][0]
    
    draw_date_str = latest_draw["drawDate"]
    draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d")

    # Only proceed if the draw date is today or later
    if draw_date.date() < datetime.today().date():
        print("No new draw data to process.")
        return None
    
    else: 
        url_path = dynamic_extract(latest_draw["drawNumberURL"], start_delimiter="'", end_delimiter="'")
        full_url = "https://www.canada.ca" + url_path if url_path else None

        transformed = {
            "draw_number": latest_draw["drawNumber"],
            "draw_name": latest_draw["drawName"],
            "draw_date": latest_draw["drawDate"],
            "draw_date_time": transform_datetime(latest_draw["drawDateTime"]) or None,
            "draw_size": int(latest_draw["drawSize"].replace(",","")),
            "draw_crs": int(latest_draw["drawCRS"].replace(",","")),
            "draw_url": full_url,
            "draw_cutoff": transform_datetime(latest_draw["drawCutOff"]) or None
        }
    
    return transformed

def load_data_to_supabase(data):
    """Insert or update the data into Supabase."""
    if data is None:
        return
    
    response = supabase.table("express_entry_draws").upsert([data]).execute()
    print(response)

def upsert_draw_round():
    raw_data = fetch_data()
    transformed_data = transform_data(raw_data)
    load_data_to_supabase(transformed_data)

upsert_draw_round()
