#!/usr/bin/env python3
"""Export Gmail credentials from AWS Secrets Manager for LangGraph Cloud deployment."""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set AWS environment
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from eaia.aws_secrets import SecretsManager


def main():
    """Export credentials for LangGraph Cloud."""
    print("Exporting Gmail Credentials for LangGraph Cloud")
    print("=" * 50)
    
    try:
        sm = SecretsManager()
        
        # Get the primary account credentials
        print("\n📧 Fetching credentials for patrick@highline.work...")
        secret_data = sm.get_secret("eaia/gmail-credentials")
        
        gmail_secret = secret_data.get("gmail_secret", "")
        gmail_token = secret_data.get("gmail_token", "")
        
        if not gmail_secret or not gmail_token:
            print("❌ Error: Credentials incomplete in AWS")
            return 1
        
        print("✅ Credentials retrieved successfully!")
        
        print("\n" + "=" * 50)
        print("ENVIRONMENT VARIABLES FOR LANGGRAPH CLOUD")
        print("=" * 50)
        print("\nCopy these values to LangGraph Cloud deployment:\n")
        
        print("GMAIL_SECRET:")
        print("-" * 40)
        print(gmail_secret)
        print("-" * 40)
        
        print("\nGMAIL_TOKEN:")
        print("-" * 40)
        print(gmail_token)
        print("-" * 40)
        
        print("\n⚠️  IMPORTANT NOTES:")
        print("1. Copy the ENTIRE content between the dashed lines")
        print("2. Make sure no line breaks are added when pasting")
        print("3. These are sensitive credentials - handle with care")
        print("4. Set USE_AWS_SECRETS=false in LangGraph Cloud")
        print("   (since we're providing credentials directly)")
        
        # Also save to a temporary file for easier copying
        output_file = Path.home() / ".eaia_langgraph_creds.txt"
        with open(output_file, 'w') as f:
            f.write(f"GMAIL_SECRET={gmail_secret}\n\n")
            f.write(f"GMAIL_TOKEN={gmail_token}\n")
        
        print(f"\n💾 Also saved to: {output_file}")
        print("   (Delete this file after use!)")
        
        # Check if we need AWS credentials
        print("\n🔍 Checking if AWS credentials are needed...")
        if os.environ.get('AWS_ACCESS_KEY_ID'):
            print("\n✅ AWS credentials found in environment")
            print("   You can optionally add these to LangGraph Cloud")
            print("   to enable direct AWS Secrets Manager access:")
            print(f"\n   AWS_ACCESS_KEY_ID={os.environ.get('AWS_ACCESS_KEY_ID')}")
            print("   AWS_SECRET_ACCESS_KEY=<your-secret-key>")
            print("   AWS_REGION=us-west-2")
        else:
            print("\n📌 No AWS credentials in environment")
            print("   LangGraph Cloud will use the provided Gmail credentials directly")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS credentials are configured")
        print("2. Check that the secret exists in AWS Secrets Manager")
        print("3. Verify you have permissions to read secrets")
        return 1


def export_for_multiple_accounts():
    """Export credentials for multiple accounts (future enhancement)."""
    accounts = [
        ("patrick@highline.work", "eaia/gmail-credentials"),
        ("patrick.smith@gmail.com", "eaia/gmail-credentials-patrick-dot-smith-at-gmail-dot-com-v2")
    ]
    
    print("\n📧 Multiple Account Configuration")
    print("=" * 50)
    
    for email, secret_name in accounts:
        print(f"\nAccount: {email}")
        try:
            sm = SecretsManager()
            secret_data = sm.get_secret(secret_name)
            print(f"✅ Found in: {secret_name}")
        except Exception as e:
            print(f"❌ Not found: {e}")


if __name__ == "__main__":
    sys.exit(main())