#!/usr/bin/env python3
import requests
import os

deployment_id = "334150fb-c682-489c-a9a1-e1dec7a864c7"

# Get API key
api_key = None
with open(".env", "r") as f:
    for line in f:
        if line.startswith("LANGSMITH_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip('"')
            break

print(f"🔍 Checking deployment {deployment_id[:8]}...")

# Check deployment health
url = f"https://prod-{deployment_id[:8]}.api.langgraph.com/health"
headers = {"x-api-key": api_key} if api_key else {}

try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 436:
        print("⏳ Status: Still building/parking")
    elif response.status_code == 200:
        if "parking" in response.text.lower():
            print("⏳ Status: Parking page (build in progress)")
        else:
            print("✅ Status: Running!")
    else:
        print(f"❓ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print(f"\n📊 Check logs at:")
print(f"https://smith.langchain.com/deployments/{deployment_id}")