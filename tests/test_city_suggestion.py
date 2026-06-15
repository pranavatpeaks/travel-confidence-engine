# test_city_suggestion.py

import requests

response = requests.get(
    "https://www.redbus.in/rpw/api/citySuggestion",
    params={
        "search": "hyderabad",
        "limit": 10,
        "routeDetection": "false",
    },
    timeout=30,
)

print(response.status_code)
print(response.json())