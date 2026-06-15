# scrapers/abhibus_test.py

import requests

url = "https://www.abhibus.com/buslist/v2/services"

payload = {
    "source": "Hyderabad",
    "sourceid": 3,
    "destination": "Tirupathi",
    "destinationid": 12,
    "jdate": "2026-06-15",
    "prd": "mobile",
    "filters": "1",
    "isReturnJourney": "0",
    "version": "105",
}

response = requests.post(
    url,
    json=payload,
)

print(response.status_code)
print(response.text[:1000])