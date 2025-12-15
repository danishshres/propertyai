import requests

url = "http://localhost:8000"
payload = {
    "street": "1C Raymel Crescent",
    "suburb": "Campbelltown",
    "state": "SA",
    "postcode": "5074"
}
# response = requests.get(f"{url}/health")
response = requests.post(f"{url}/search", json=payload)
print(response.json())