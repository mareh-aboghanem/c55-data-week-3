import requests
import json
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("AZURE_TOKEN")
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

url = f"https://management.azure.com/subscriptions/{subscription_id}/resourcegroups?api-version=2024-03-01"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()

#for rg in response.json()["value"]:
    #print(f"{rg['name']}: {rg['location']}")


azure_data = response.json()
output_file = OUTPUT_DIR / "azure_resource_groups.json"
with open(output_file, "w") as f:
    json.dump(azure_data, f, indent=2)

print(f"Successfully saved full response to {output_file}")
