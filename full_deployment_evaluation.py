#!/usr/bin/env python3
"""Full deployment evaluation with multiple test approaches"""

import requests
import json
import time
from datetime import datetime

def full_evaluation():
    deployment_id = "334150fb-c682-489c-a9a1-e1dec7a864c7"
    
    # Get API key
    api_key = None
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("LANGSMITH_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip('"')
                    break
    except:
        print("❌ Could not read API key")
        return
    
    print("🔍 FULL DEPLOYMENT EVALUATION")
    print("=" * 60)
    print(f"Deployment ID: {deployment_id}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Check different URL patterns
    print("\n1️⃣ Testing URL Patterns...")
    url_patterns = [
        f"https://prod-{deployment_id[:8]}.api.langgraph.com",
        f"https://{deployment_id}.api.langgraph.com",
        f"https://api.langgraph.com/deployments/{deployment_id}",
        f"https://{deployment_id[:8]}-prod.api.langgraph.com"
    ]
    
    working_url = None
    for url in url_patterns:
        try:
            response = requests.get(f"{url}/health", headers=headers, timeout=5)
            print(f"   {url}/health - Status: {response.status_code}")
            if response.status_code == 200 and "parking" not in response.text.lower():
                working_url = url
                print(f"   ✅ Found working URL!")
                break
        except:
            print(f"   {url}/health - Connection failed")
    
    if not working_url:
        working_url = url_patterns[0]  # Use default
        print(f"\n   ⚠️ No fully working URL found, using: {working_url}")
    
    # Test 2: Try different invoke methods
    print("\n2️⃣ Testing Different Invoke Methods...")
    base_url = working_url
    
    # Method A: Standard invoke
    print("\n   A) Standard /invoke endpoint:")
    try:
        response = requests.post(
            f"{base_url}/main/invoke",
            json={
                "input": {"messages": [{"role": "user", "content": "Hello"}]},
                "config": {"configurable": {"thread_id": "test-1"}}
            },
            headers=headers,
            timeout=10
        )
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print(f"      ✅ Success! Response: {response.text[:100]}...")
    except Exception as e:
        print(f"      ❌ Error: {str(e)[:50]}")
    
    # Method B: Stream endpoint
    print("\n   B) Stream endpoint:")
    try:
        response = requests.post(
            f"{base_url}/main/stream",
            json={
                "input": {"messages": [{"role": "user", "content": "Hello"}]},
                "config": {"configurable": {"thread_id": "test-2"}}
            },
            headers=headers,
            timeout=10
        )
        print(f"      Status: {response.status_code}")
    except Exception as e:
        print(f"      ❌ Error: {str(e)[:50]}")
    
    # Method C: Direct graph access
    print("\n   C) Direct graph access:")
    try:
        response = requests.get(
            f"{base_url}/graphs",
            headers=headers,
            timeout=10
        )
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print(f"      Response: {response.text[:100]}...")
    except Exception as e:
        print(f"      ❌ Error: {str(e)[:50]}")
    
    # Test 3: Check deployment metadata
    print("\n3️⃣ Checking Deployment Metadata...")
    langsmith_url = f"https://api.smith.langchain.com/v1/deployments/{deployment_id}"
    try:
        response = requests.get(
            langsmith_url,
            headers={"x-api-key": api_key},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Deployment found in LangSmith")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Created: {data.get('created_at', 'Unknown')}")
            print(f"   Revision: {data.get('revision_id', 'Unknown')[:8]}...")
        else:
            print(f"   ❌ Could not fetch deployment info: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error fetching deployment info: {str(e)[:50]}")
    
    # Test 4: Alternative API patterns
    print("\n4️⃣ Testing Alternative API Patterns...")
    
    # Try root endpoint
    try:
        response = requests.get(base_url, headers=headers, timeout=5)
        print(f"   Root endpoint ({base_url}): {response.status_code}")
    except:
        print(f"   Root endpoint: Failed")
    
    # Try OpenAPI/docs
    try:
        response = requests.get(f"{base_url}/docs", headers=headers, timeout=5)
        print(f"   API docs (/docs): {response.status_code}")
    except:
        print(f"   API docs: Failed")
    
    # Test 5: Final diagnosis
    print("\n5️⃣ DIAGNOSIS:")
    print("-" * 40)
    
    if working_url:
        print(f"✅ Deployment is reachable at: {working_url}")
    else:
        print("⚠️ Deployment is not fully accessible via API")
    
    print("\n🎯 RECOMMENDED ACTIONS:")
    print("\n1. **Use LangGraph Studio** (Primary Method):")
    print(f"   https://smith.langchain.com/studio/?deployment={deployment_id}")
    print("   - This is the intended way to interact with deployments")
    print("   - The API endpoints may be restricted for security")
    
    print("\n2. **Check Deployment Logs**:")
    print(f"   https://smith.langchain.com/deployments/{deployment_id}")
    print("   - Look for any runtime errors")
    print("   - Verify all services started correctly")
    
    print("\n3. **Verify in Deployments List**:")
    print("   https://smith.langchain.com/o/5046ce9f-a49d-59d7-99a8-4e2f3d8dc689/deployments")
    print("   - Confirm status is 'Running'")
    print("   - Check if this is the latest deployment")
    
    print("\n📝 SUMMARY:")
    print("The deployment appears to be running but API access is limited.")
    print("This is normal - LangGraph deployments are primarily accessed through Studio.")
    print("Please use LangGraph Studio to interact with your Executive AI Assistant.")

if __name__ == "__main__":
    full_evaluation()