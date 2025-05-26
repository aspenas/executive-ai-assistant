#!/usr/bin/env python3
"""Store LangSmith API key in AWS Secrets Manager."""

import sys
import os
from pathlib import Path
import getpass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set AWS environment
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from eaia.aws_secrets import SecretsManager


def main():
    """Store LangSmith API key in AWS."""
    print("Store LangSmith API Key in AWS Secrets Manager")
    print("=" * 50)
    
    print("\n📌 To get your LangSmith API key:")
    print("1. Go to https://smith.langchain.com")
    print("2. Click on your profile → Settings")
    print("3. Navigate to 'API Keys' section")
    print("4. Create a new API key or copy existing one")
    
    # Get API key from user
    print("\nEnter your LangSmith API key (input will be hidden):")
    api_key = getpass.getpass("LangSmith API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return 1
    
    # Validate format (basic check)
    if not api_key.startswith("ls__") or len(api_key) < 20:
        print("⚠️  Warning: API key doesn't match expected format (ls__...)")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            return 1
    
    # Store in AWS
    try:
        sm = SecretsManager()
        
        secret_data = {
            "api_key": api_key,
            "service": "langsmith",
            "description": "LangSmith API key for EAIA deployment"
        }
        
        arn = sm.create_or_update_secret(
            secret_name="eaia/langsmith-api-key",
            secret_value=secret_data,
            description="LangSmith API key for Executive AI Assistant"
        )
        
        print("\n✅ Successfully stored in AWS Secrets Manager!")
        print(f"   ARN: {arn}")
        print("   Secret name: eaia/langsmith-api-key")
        
        # Also export to environment for current session
        os.environ['LANGSMITH_API_KEY'] = api_key
        
        print("\n📌 The API key has been:")
        print("1. Stored in AWS Secrets Manager")
        print("2. Set in current environment")
        print("\nYou can now run the deployment setup again!")
        
    except Exception as e:
        print(f"\n❌ Error storing API key: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())