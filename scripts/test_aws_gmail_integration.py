#!/usr/bin/env python3
"""Test AWS Secrets Manager integration with Gmail."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.aws_secrets import get_gmail_credentials_from_aws  # noqa: E402
from eaia.gmail import get_credentials  # noqa: E402


def main():
    """Test AWS Secrets Manager integration."""
    print("Testing AWS Secrets Manager Gmail Integration")
    print("=" * 50)
    
    # Check environment
    use_aws = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
    aws_region = os.getenv("AWS_REGION", "not set")
    
    print(f"USE_AWS_SECRETS: {use_aws}")
    print(f"AWS_REGION: {aws_region}")
    
    if not use_aws:
        print("\n⚠️  AWS Secrets Manager is not enabled!")
        print("Set: export USE_AWS_SECRETS=true")
        return 1
    
    # Test direct AWS access
    print("\n1. Testing direct AWS Secrets Manager access...")
    try:
        gmail_secret, gmail_token = get_gmail_credentials_from_aws()
        print("✅ Successfully retrieved credentials from AWS!")
        print(f"   Secret length: {len(gmail_secret)} chars")
        print(f"   Token length: {len(gmail_token)} chars")
    except Exception as e:
        print(f"❌ Failed to retrieve from AWS: {e}")
        return 1
    
    # Test Gmail integration
    print("\n2. Testing Gmail integration with AWS credentials...")
    try:
        creds = get_credentials()
        print("✅ Gmail credentials loaded successfully!")
        print(f"   Valid: {creds.valid}")
        print(f"   Expired: {creds.expired}")
        if hasattr(creds, 'client_id'):
            print(f"   Client ID: ...{creds.client_id[-8:]}")
    except Exception as e:
        print(f"❌ Failed to load Gmail credentials: {e}")
        return 1
    
    # Test Gmail API
    print("\n3. Testing Gmail API access...")
    try:
        from googleapiclient.discovery import build
        service = build("gmail", "v1", credentials=creds)
        
        # Get user profile
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get('emailAddress', 'Unknown')
        print("✅ Gmail API working!")
        print(f"   Email: {email}")
        print(f"   Total messages: {profile.get('messagesTotal', 0)}")
        print(f"   Total threads: {profile.get('threadsTotal', 0)}")
    except Exception as e:
        print(f"❌ Failed to access Gmail API: {e}")
        return 1
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! AWS Secrets Manager integration is working.")
    print("\nYou can now run scripts with:")
    cmd = "USE_AWS_SECRETS=true AWS_REGION=us-west-2 "
    cmd += "poetry run python scripts/run_ingest.py"
    print(f"  {cmd}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 