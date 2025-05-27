#!/usr/bin/env python3
"""Test the Executive AI Assistant functionality"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app"
# Read API key from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('LANGSMITH_API_KEY='):
            API_KEY = line.split('=', 1)[1].strip()
            break

def test_assistant():
    """Run comprehensive tests on the assistant"""
    print("🧪 Testing Executive AI Assistant...")
    print(f"📍 Base URL: {BASE_URL}")
    print("-" * 50)
    
    # Set up headers with authentication
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    # Test 1: Health check
    print("\n1️⃣ Testing API availability...")
    try:
        response = requests.get(f"{BASE_URL}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ API is reachable")
        else:
            print(f"⚠️  API returned status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to reach API: {e}")
        return
    
    # Test 2: Create a thread
    print("\n2️⃣ Creating a test thread...")
    try:
        response = requests.post(
            f"{BASE_URL}/threads",
            headers=headers,
            timeout=10
        )
        if response.status_code in [200, 201]:
            thread_data = response.json()
            thread_id = thread_data.get("thread_id") or thread_data.get("id")
            print(f"✅ Thread created: {thread_id}")
        else:
            print(f"❌ Failed to create thread: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return
    except Exception as e:
        print(f"❌ Error creating thread: {e}")
        return
    
    # Test 3: Send test messages
    test_messages = [
        "Hello, are you working?",
        "What can you help me with?",
        "Can you check my emails?",
    ]
    
    print("\n3️⃣ Testing assistant responses...")
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test {i}: '{message}'")
        try:
            response = requests.post(
                f"{BASE_URL}/threads/{thread_id}/runs",
                headers=headers,
                json={
                    "assistant_id": "main",
                    "input": {
                        "messages": [{
                            "role": "user",
                            "content": message
                        }]
                    }
                },
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"   ✅ Message sent successfully")
                
                # Try to get the response
                run_data = response.json()
                run_id = run_data.get("run_id") or run_data.get("id")
                
                # Poll for completion
                print("   ⏳ Waiting for response...", end="", flush=True)
                for _ in range(10):
                    time.sleep(2)
                    print(".", end="", flush=True)
                    
                    # Check run status
                    status_response = requests.get(
                        f"{BASE_URL}/threads/{thread_id}/runs/{run_id}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get("status") == "completed":
                            print("\n   ✅ Got response!")
                            break
                else:
                    print("\n   ⏱️  Response taking longer than expected")
                    
            else:
                print(f"   ❌ Failed to send message: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 4: Check available graphs
    print("\n4️⃣ Checking available graphs...")
    graphs = ["main", "cron", "general_reflection_graph", "multi_reflection_graph"]
    
    for graph in graphs:
        try:
            response = requests.post(
                f"{BASE_URL}/threads",
                headers=headers,
                json={"assistant_id": graph},
                timeout=10
            )
            if response.status_code in [200, 201, 404]:
                if response.status_code == 404:
                    print(f"   ⚠️  Graph '{graph}' not found")
                else:
                    print(f"   ✅ Graph '{graph}' is available")
            else:
                print(f"   ❌ Graph '{graph}' returned: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error checking graph '{graph}': {e}")
    
    print("\n" + "-" * 50)
    print("🏁 Testing complete!")
    print(f"\n📝 Summary:")
    print(f"   - API Base: {BASE_URL}")
    print(f"   - Studio: https://smith.langchain.com/studio/thread?baseUrl={BASE_URL}")
    print(f"   - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_assistant()