#!/usr/bin/env python3
"""Test deployment with correct runs format"""

import requests
import json
import uuid
from datetime import datetime

def test_deployment_runs():
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
    
    print("🧪 TESTING DEPLOYMENT WITH CORRECT FORMAT")
    print("=" * 60)
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Get assistants list
    print("\n1️⃣ Getting Assistants List...")
    try:
        response = requests.get(f"{base_url}/assistants", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            assistants = response.json()
            print(f"   Assistants: {json.dumps(assistants, indent=2)}")
            
            # Extract assistant IDs
            if assistants:
                assistant_id = assistants[0].get("assistant_id", assistants[0].get("graph_id", "main"))
            else:
                assistant_id = "main"
        else:
            print(f"   Response: {response.text}")
            assistant_id = "main"
    except Exception as e:
        print(f"   Error: {str(e)}")
        assistant_id = "main"
    
    # Test 2: Create a proper thread with UUID
    print("\n2️⃣ Creating Thread with UUID...")
    thread_id = str(uuid.uuid4())
    
    try:
        # Try PUT first (common pattern)
        response = requests.put(
            f"{base_url}/threads/{thread_id}",
            json={"metadata": {"created_at": datetime.now().isoformat()}},
            headers=headers,
            timeout=10
        )
        print(f"   PUT /threads/{thread_id}: {response.status_code}")
        if response.status_code not in [200, 201]:
            # Try POST to threads
            response = requests.post(
                f"{base_url}/threads",
                json={"thread_id": thread_id},
                headers=headers,
                timeout=10
            )
            print(f"   POST /threads: {response.status_code}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 3: Create a run with the assistant
    print(f"\n3️⃣ Creating Run with assistant_id='{assistant_id}'...")
    
    run_payload = {
        "assistant_id": assistant_id,
        "thread_id": thread_id,
        "input": {
            "messages": [{
                "role": "human",
                "content": "Hello! I'm testing the Executive AI Assistant. What can you help me with?"
            }]
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/runs",
            json=run_payload,
            headers=headers,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print("   ✅ Run created successfully!")
            run_data = response.json()
            run_id = run_data.get("run_id")
            print(f"   Run ID: {run_id}")
            
            # Test 4: Check run status
            if run_id:
                print("\n4️⃣ Checking Run Status...")
                import time
                for i in range(5):
                    try:
                        response = requests.get(
                            f"{base_url}/runs/{run_id}",
                            headers=headers,
                            timeout=10
                        )
                        if response.status_code == 200:
                            status_data = response.json()
                            status = status_data.get("status", "unknown")
                            print(f"   [{i+1}/5] Status: {status}")
                            
                            if status in ["success", "completed"]:
                                print("\n   ✅ Run completed!")
                                # Get the output
                                if "output" in status_data:
                                    output = status_data["output"]
                                    if "messages" in output:
                                        for msg in output["messages"]:
                                            if msg.get("role") == "assistant":
                                                print(f"\n   🤖 Assistant: {msg.get('content', '')[:300]}...")
                                break
                            elif status in ["error", "failed"]:
                                print(f"\n   ❌ Run failed: {status_data.get('error', 'Unknown error')}")
                                break
                        
                        time.sleep(2)
                    except Exception as e:
                        print(f"   Error checking status: {str(e)}")
        else:
            print(f"   ❌ Failed to create run")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 5: Try alternative formats
    print("\n5️⃣ Testing Alternative Formats...")
    
    # Try without thread_id (might create one automatically)
    alt_payload = {
        "assistant_id": assistant_id,
        "input": {
            "messages": [{
                "role": "human",
                "content": "Test message"
            }]
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/runs",
            json=alt_payload,
            headers=headers,
            timeout=30
        )
        print(f"   Without thread_id: {response.status_code}")
    except:
        print("   Without thread_id: Error")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print("\nThe deployment is accessible but graphs may not be loaded.")
    print("Check the deployment logs for initialization errors.")

if __name__ == "__main__":
    test_deployment_runs()