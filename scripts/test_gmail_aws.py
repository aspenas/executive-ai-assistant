#!/usr/bin/env python3
"""Test Gmail functionality with AWS-stored credentials."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set AWS environment variables
os.environ['USE_AWS_SECRETS'] = 'true'
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from eaia.gmail import get_credentials
from googleapiclient.discovery import build


def main():
    print("Testing Gmail with AWS Secrets Manager...")
    print("=" * 50)
    
    try:
        # Get credentials from AWS
        print("🔐 Getting credentials from AWS...")
        creds = get_credentials()
        print("✅ Credentials loaded successfully!")
        
        # Build Gmail service
        print("\n📧 Connecting to Gmail API...")
        service = build("gmail", "v1", credentials=creds)
        
        # Test by getting user profile
        profile = service.users().getProfile(userId="me").execute()
        print(f"✅ Connected to Gmail!")
        print(f"   Email: {profile.get('emailAddress')}")
        print(f"   Total messages: {profile.get('messagesTotal')}")
        print(f"   Total threads: {profile.get('threadsTotal')}")
        
        # List recent messages
        print("\n📨 Recent messages:")
        results = service.users().messages().list(
            userId="me",
            maxResults=5
        ).execute()
        
        messages = results.get("messages", [])
        if messages:
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId="me",
                    id=msg["id"]
                ).execute()
                
                headers = msg_data["payload"].get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
                
                print(f"   - {subject[:50]}... (from {sender[:30]}...)")
        else:
            print("   No messages found")
        
        print("\n✅ Gmail integration working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS credentials are configured")
        print("2. Check that USE_AWS_SECRETS=true is set")
        print("3. Verify the secret exists in AWS Secrets Manager")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())