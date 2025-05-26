#!/usr/bin/env python3
"""Test both Gmail accounts configured in AWS Secrets Manager."""

import os
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set AWS environment variables
os.environ['USE_AWS_SECRETS'] = 'true'
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from eaia.aws_secrets import SecretsManager
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def test_gmail_account(secret_name, expected_email):
    """Test a specific Gmail account."""
    print(f"\n📧 Testing {expected_email}...")
    print("-" * 50)
    
    try:
        # Get credentials from AWS
        sm = SecretsManager()
        secret_data = sm.get_secret(secret_name)
        
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
        service = build("gmail", "v1", credentials=creds)
        
        # Get user profile
        profile = service.users().getProfile(userId="me").execute()
        actual_email = profile.get('emailAddress')
        
        print(f"✅ Connected successfully!")
        print(f"   Email: {actual_email}")
        print(f"   Total messages: {profile.get('messagesTotal')}")
        print(f"   Total threads: {profile.get('threadsTotal')}")
        
        # Check if it's the expected account
        if actual_email != expected_email:
            print(f"⚠️  WARNING: Expected {expected_email} but got {actual_email}")
            print("   The credentials may be for the wrong account!")
        
        # List a few recent messages
        results = service.users().messages().list(
            userId="me",
            maxResults=3
        ).execute()
        
        messages = results.get("messages", [])
        if messages:
            print("\n   Recent messages:")
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId="me",
                    id=msg["id"]
                ).execute()
                
                headers = msg_data["payload"].get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                print(f"   - {subject[:60]}...")
        
        return True, actual_email
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Check if it's a Gmail API not enabled error
        if "Gmail API has not been used" in str(e):
            # Extract project ID from error
            import re
            project_match = re.search(r'project (\d+)', str(e))
            if project_match:
                project_id = project_match.group(1)
                print(f"\n📌 To enable Gmail API:")
                print(f"   Visit: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project={project_id}")
                print("   Click 'ENABLE' and wait 30 seconds")
        
        return False, None


def main():
    print("Testing Both Gmail Accounts in AWS Secrets Manager")
    print("=" * 60)
    
    accounts = [
        {
            "secret": "eaia/gmail-credentials",
            "email": "patrick@highline.work",
            "project": "project-0l0"
        },
        {
            "secret": "eaia/gmail-credentials-patrick-dot-smith-at-gmail-dot-com-v2",
            "email": "patrick.smith@gmail.com", 
            "project": "tiller-auto"
        }
    ]
    
    results = []
    
    for account in accounts:
        success, actual_email = test_gmail_account(account["secret"], account["email"])
        results.append({
            "expected": account["email"],
            "actual": actual_email,
            "success": success,
            "secret": account["secret"],
            "project": account["project"]
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary of Gmail Account Configuration:")
    print("=" * 60)
    
    all_success = True
    for result in results:
        if result["success"]:
            if result["actual"] == result["expected"]:
                print(f"✅ {result['expected']}")
                print(f"   Secret: {result['secret']}")
                print(f"   Project: {result['project']}")
            else:
                print(f"⚠️  {result['expected']} -> Actually connected to {result['actual']}")
                print(f"   Secret: {result['secret']}")
                print("   NEEDS RECONFIGURATION!")
                all_success = False
        else:
            print(f"❌ {result['expected']} - FAILED")
            print(f"   Secret: {result['secret']}")
            all_success = False
    
    print("\n" + "=" * 60)
    if all_success:
        print("✅ Both Gmail accounts are properly configured!")
        print("\nTo use in your code:")
        print("  export USE_AWS_SECRETS=true")
    else:
        print("⚠️  Some accounts need attention. See details above.")
    
    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())