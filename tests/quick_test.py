# quick_test.py

import requests

url = (
    "https://www.redbus.in/rpw/api/searchResults"
    "?fromCity=66664"
    "&toCity=122"
    "&DOJ=1-Jul-2026"
    "&limit=10"
    "&offset=0"
    "&meta=true"
)

response = requests.post(
    url,
    json={"appliedFilterCount": 0},
    timeout=60,
)

print(response.status_code)
print(len(response.text))