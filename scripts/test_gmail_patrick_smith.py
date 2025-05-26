#!/usr/bin/env python3
"""Test Gmail functionality for patrick.smith@gmail.com with AWS-stored credentials."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set AWS environment variables
os.environ['USE_AWS_SECRETS'] = 'true'
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from eaia.aws_secrets import SecretsManager
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json


def main():
    print("Testing Gmail for patrick.smith@gmail.com with AWS Secrets Manager...")
    print("=" * 60)
    
    try:
        # Get credentials from AWS for specific account
        print("🔐 Getting credentials from AWS...")
        sm = SecretsManager()
        
        secret_name = "eaia/gmail-credentials-patrick-dot-smith-at-gmail-dot-com"
        secret_data = sm.get_secret(secret_name)
        
        print("✅ Credentials retrieved from AWS!")
        
        # Parse the token data
        gmail_token = json.loads(secret_data['gmail_token'])
        
        # Create credentials object
        creds = Credentials(
            token=gmail_token.get('token'),
            refresh_token=gmail_token.get('refresh_token'),
            token_uri=gmail_token.get('token_uri'),
            client_id=gmail_token.get('client_id'),
            client_secret=gmail_token.get('client_secret'),
            scopes=gmail_token.get('scopes'),
        )
        
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
        
        print("\n✅ Gmail integration working correctly for patrick.smith@gmail.com!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        # Check if it's a Gmail API not enabled error
        if "Gmail API has not been used" in str(e):
            print("\n📌 To enable Gmail API for this project:")
            print("   1. Visit: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=377858888563")
            print("   2. Click 'ENABLE'")
            print("   3. Wait 30 seconds and try again")
        else:
            print("\nTroubleshooting:")
            print("1. Ensure AWS credentials are configured")
            print("2. Check that the secret exists in AWS Secrets Manager")
            print("3. Verify Gmail API is enabled for the project")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())