#!/usr/bin/env python3
"""Direct API evaluation of the live deployment"""

import requests
import json
from datetime import datetime
import time

def evaluate_live_api():
    # Live deployment URL
    base_url = "https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app"
    
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
    
    print("🔍 DIRECT API EVALUATION")
    print("=" * 60)
    print(f"Deployment URL: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Check all base endpoints
    print("\n1️⃣ Checking Base Endpoints...")
    endpoints = [
        ("GET", "/", "Root"),
        ("GET", "/health", "Health"),
        ("GET", "/info", "Info"),
        ("GET", "/runs", "Runs"),
        ("GET", "/threads", "Threads"),
        ("GET", "/assistants", "Assistants"),
        ("GET", "/stores", "Stores"),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            print(f"   {name} ({endpoint}): {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"      Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   {name} ({endpoint}): Error - {str(e)[:50]}")
    
    # Test 2: Check graph endpoints
    print("\n2️⃣ Checking Graph Endpoints...")
    graphs = ["main", "cron", "general_reflection_graph", "multi_reflection_graph"]
    
    for graph in graphs:
        # Check graph info
        try:
            response = requests.get(f"{base_url}/{graph}", headers=headers, timeout=5)
            print(f"   /{graph}: {response.status_code}")
        except:
            print(f"   /{graph}: Error")
    
    # Test 3: Try to create a thread
    print("\n3️⃣ Testing Thread Creation...")
    thread_payload = {
        "thread_id": f"test-thread-{int(time.time())}",
        "metadata": {"test": True}
    }
    
    try:
        response = requests.post(
            f"{base_url}/threads",
            json=thread_payload,
            headers=headers,
            timeout=10
        )
        print(f"   Create thread: {response.status_code}")
        if response.status_code in [200, 201]:
            thread_data = response.json()
            thread_id = thread_data.get("thread_id", thread_payload["thread_id"])
            print(f"   Thread ID: {thread_id}")
        else:
            print(f"   Response: {response.text[:200]}...")
            thread_id = thread_payload["thread_id"]
    except Exception as e:
        print(f"   Error: {str(e)}")
        thread_id = thread_payload["thread_id"]
    
    # Test 4: Try different invocation patterns
    print("\n4️⃣ Testing Invocation Patterns...")
    
    # Pattern A: Direct invoke with messages
    print("\n   A) Direct message invoke:")
    message_payload = {
        "messages": [{
            "role": "human",
            "content": "Hello, what can you help me with?"
        }],
        "thread_id": thread_id
    }
    
    try:
        response = requests.post(
            f"{base_url}/runs",
            json=message_payload,
            headers=headers,
            timeout=30
        )
        print(f"      Status: {response.status_code}")
        if response.status_code in [200, 201, 202]:
            print("      ✅ Success!")
            run_data = response.json()
            print(f"      Run ID: {run_data.get('run_id', 'N/A')}")
        else:
            print(f"      Response: {response.text[:200]}...")
    except Exception as e:
        print(f"      Error: {str(e)}")
    
    # Pattern B: Graph-specific invoke
    print("\n   B) Graph-specific invoke:")
    graph_payload = {
        "input": {
            "messages": [{
                "role": "human",
                "content": "Test message"
            }]
        },
        "config": {
            "configurable": {
                "thread_id": f"{thread_id}-main"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/main/invoke",
            json=graph_payload,
            headers=headers,
            timeout=30
        )
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print("      ✅ Success!")
        else:
            print(f"      Response: {response.text[:200]}...")
    except Exception as e:
        print(f"      Error: {str(e)}")
    
    # Pattern C: Runs with graph specification
    print("\n   C) Runs with graph specification:")
    runs_payload = {
        "assistant_id": "main",
        "input": {
            "messages": [{
                "role": "human",
                "content": "Hello"
            }]
        },
        "thread_id": f"{thread_id}-runs"
    }
    
    try:
        response = requests.post(
            f"{base_url}/runs",
            json=runs_payload,
            headers=headers,
            timeout=30
        )
        print(f"      Status: {response.status_code}")
        if response.status_code in [200, 201, 202]:
            print("      ✅ Success!")
        else:
            print(f"      Response: {response.text[:200]}...")
    except Exception as e:
        print(f"      Error: {str(e)}")
    
    # Test 5: Check for logs/monitoring endpoints
    print("\n5️⃣ Checking Logs/Monitoring...")
    log_endpoints = [
        "/runs?limit=5",
        f"/threads/{thread_id}/runs",
        "/logs",
        "/metrics",
    ]
    
    for endpoint in log_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            print(f"   {endpoint}: {response.status_code}")
        except:
            print(f"   {endpoint}: Error")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API EVALUATION SUMMARY")
    print("=" * 60)
    
    print("\n🔍 Findings:")
    print("- Base URL is accessible")
    print("- Info endpoint returns empty graphs list")
    print("- Need to determine correct invocation pattern")
    print("- Check if graphs are properly registered")
    
    print("\n🚀 Recommended Next Steps:")
    print("1. Check deployment logs for initialization errors")
    print("2. Verify graphs are loading correctly")
    print("3. Test through LangGraph Studio interface")
    print("4. Check if deployment needs reconfiguration")

if __name__ == "__main__":
    evaluate_live_api()