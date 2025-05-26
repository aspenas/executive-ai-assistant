#!/usr/bin/env python3
"""Set up Gmail credentials with optional AWS Secrets Manager storage."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.gmail import get_credentials  # noqa: E402


def main():
    """Set up Gmail credentials."""
    print("Gmail Setup for EAIA")
    print("=" * 50)
    
    # Check if credentials already exist
    secrets_dir = Path(__file__).parent.parent / "eaia" / ".secrets"
    secrets_path = secrets_dir / "secrets.json"
    token_path = secrets_dir / "token.json"
    
    if secrets_path.exists() and token_path.exists():
        print("✅ Gmail credentials already exist locally")
        
        # Ask if user wants to migrate to AWS
        response = input("\nMigrate to AWS Secrets Manager? (y/n): ")
        use_aws = response.lower() == 'y'
        if use_aws:
            print("\nTo migrate to AWS, run:")
            print("  poetry run python scripts/migrate_secrets_to_aws.py")
        return 0
    
    print("\n📋 Prerequisites:")
    print("1. Google Cloud project with Gmail API enabled")
    print("2. OAuth 2.0 credentials downloaded as JSON")
    print("3. The JSON file should be at: eaia/.secrets/secrets.json")
    
    print("\n🔧 Setting up Gmail credentials...")
    
    # Create secrets directory
    secrets_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if secrets.json exists
    if not secrets_path.exists():
        print("\n❌ OAuth credentials file not found!")
        print(f"   Expected at: {secrets_path}")
        print("\nPlease:")
        print("1. Go to Google Cloud Console")
        print("2. Create OAuth 2.0 credentials")
        print("3. Download the JSON file")
        print("4. Save it as: eaia/.secrets/secrets.json")
        print("\nThen run this script again.")
        return 1
    
    print("✅ Found OAuth credentials file")
    print("\n🔐 Authenticating with Google...")
    print("A browser window will open for authentication.")
    print("Please log in and grant permissions.")
    
    try:
        # This will open a browser for authentication
        get_credentials()  # This creates and saves the token
        print("\n✅ Authentication successful!")
        print(f"   Token saved to: {token_path}")
        
        # Ask about AWS Secrets Manager
        print("\n" + "=" * 50)
        use_aws = input("Store credentials in AWS Secrets Manager? (y/n): ")
        
        if use_aws.lower() == 'y':
            print("\nTo store in AWS Secrets Manager, run:")
            print("  poetry run python scripts/migrate_secrets_to_aws.py")
            print("\nThen set environment variable:")
            print("  export USE_AWS_SECRETS=true")
        else:
            print("\n✅ Setup complete!")
            print("\nYour Gmail credentials are stored locally.")
            print("For production deployment, you'll need to set:")
            print("  GMAIL_SECRET - contents of eaia/.secrets/secrets.json")
            print("  GMAIL_TOKEN - contents of eaia/.secrets/token.json")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 