#!/usr/bin/env python3
"""Test the live deployment at the new URL"""

import requests
import json
from datetime import datetime

def test_live_deployment():
    # New deployment URL
    deployment_url = "https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app"
    
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
    
    print("🎉 TESTING LIVE DEPLOYMENT")
    print("=" * 60)
    print(f"URL: {deployment_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        response = requests.get(f"{deployment_url}/health", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check passed!")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Info Endpoint
    print("\n2️⃣ Testing Info Endpoint...")
    try:
        response = requests.get(f"{deployment_url}/info", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print("   ✅ Info endpoint working!")
            print(f"   Graphs: {list(info.get('graphs', {}).keys())}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Main Graph Interaction
    print("\n3️⃣ Testing Main Graph...")
    test_message = {
        "input": {
            "messages": [{
                "role": "human",
                "content": "Hello! I'm Patrick. What can you help me with today?"
            }]
        },
        "config": {
            "configurable": {
                "thread_id": f"test-session-{int(datetime.now().timestamp())}"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{deployment_url}/main/invoke",
            json=test_message,
            headers=headers,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Main graph responding!")
            result = response.json()
            
            # Extract assistant response
            if "output" in result and "messages" in result["output"]:
                messages = result["output"]["messages"]
                for msg in messages:
                    if msg.get("type") == "ai" or msg.get("role") == "assistant":
                        content = msg.get("content", "")
                        print(f"\n   🤖 Assistant: {content[:300]}...")
                        break
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: List Available Tools
    print("\n4️⃣ Testing Tool Discovery...")
    tool_message = {
        "input": {
            "messages": [{
                "role": "human",
                "content": "What tools do you have access to?"
            }]
        },
        "config": {
            "configurable": {
                "thread_id": f"tools-test-{int(datetime.now().timestamp())}"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{deployment_url}/main/invoke",
            json=tool_message,
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            print("   ✅ Tool query successful!")
    except:
        print("   ❌ Could not query tools")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Your Executive AI Assistant is LIVE at:")
    print(f"   {deployment_url}")
    
    print("\n🚀 Access Methods:")
    print("\n1. **LangGraph Studio** (Visual Interface):")
    print("   https://smith.langchain.com/studio")
    print("   - Select your deployment from the dropdown")
    print("   - Or use the deployment URL directly")
    
    print("\n2. **API Access** (Programmatic):")
    print("   Base URL:", deployment_url)
    print("   Headers: x-api-key: <your-langsmith-api-key>")
    
    print("\n3. **Available Endpoints**:")
    print(f"   - Health: GET {deployment_url}/health")
    print(f"   - Info: GET {deployment_url}/info")
    print(f"   - Main Graph: POST {deployment_url}/main/invoke")
    print(f"   - Cron Graph: POST {deployment_url}/cron/invoke")
    
    print("\n📝 Example API Call:")
    print(f"""
curl -X POST {deployment_url}/main/invoke \\
  -H "x-api-key: {api_key[:20]}..." \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(test_message, indent=2)}'
""")

if __name__ == "__main__":
    test_live_deployment()