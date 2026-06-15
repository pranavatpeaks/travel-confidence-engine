from scrapers.city_resolver import resolve_city


cities = [
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Tirupati",
    "Vizag",
]


for city in cities:

    print("=" * 60)

    result = resolve_city(city)

    print(f"Input         : {city}")
    print(f"RedBus ID     : {result['id']}")
    print(f"Name          : {result['name']}")
    print(f"Location Name : {result['location_name']}")