#!/usr/bin/env python3
"""Test LangGraph Studio access and provide guidance"""

import webbrowser
from datetime import datetime

def test_studio_access():
    deployment_id = "334150fb-c682-489c-a9a1-e1dec7a864c7"
    
    print("🔍 LangGraph Studio Access Test")
    print("=" * 60)
    print(f"Deployment ID: {deployment_id}")
    print(f"Test Time: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Studio URLs
    studio_direct = f"https://smith.langchain.com/studio/?deployment={deployment_id}"
    studio_base = "https://smith.langchain.com/studio"
    deployments_list = "https://smith.langchain.com/o/5046ce9f-a49d-59d7-99a8-4e2f3d8dc689/deployments"
    
    print("\n📍 Access Methods:\n")
    
    print("1️⃣ **Direct Studio Link** (Recommended):")
    print(f"   {studio_direct}")
    print("   - This should open Studio with your deployment selected")
    print("   - If you see 404, try method 2\n")
    
    print("2️⃣ **Manual Selection**:")
    print(f"   {studio_base}")
    print("   - Open Studio")
    print("   - Look for deployment dropdown (top-right)")
    print("   - Select deployment ID: 334150fb...")
    print("   - If not in dropdown, click refresh icon\n")
    
    print("3️⃣ **Check Deployments List**:")
    print(f"   {deployments_list}")
    print("   - Verify deployment shows as 'Running'")
    print("   - Check for any new deployment IDs")
    print("   - Look for error messages\n")
    
    print("🧪 Testing in Studio:")
    print("-" * 40)
    print("Once in Studio, try these test messages:\n")
    
    test_messages = [
        "Hello! What can you help me with?",
        "Can you check my emails?",
        "What tools do you have access to?",
        "Tell me about your capabilities"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"{i}. \"{msg}\"")
    
    print("\n⚠️  Common Issues:")
    print("-" * 40)
    print("• **404 Error**: Deployment might have a new ID")
    print("• **Not in dropdown**: Try refreshing or check deployments list")
    print("• **Connection error**: Check if you're logged in")
    print("• **No response**: Check deployment logs for errors")
    
    print("\n🔧 If Studio shows 404:")
    print("1. Go to deployments list (link above)")
    print("2. Find the deployment with status 'Running'")
    print("3. Copy the new deployment ID")
    print("4. Use it in Studio")
    
    print("\n🚀 Opening Studio...")
    try:
        webbrowser.open(studio_direct)
        print("✅ Opened in browser")
    except:
        print("⚠️  Could not auto-open browser")
        print("Please copy the URL above")

if __name__ == "__main__":
    test_studio_access()