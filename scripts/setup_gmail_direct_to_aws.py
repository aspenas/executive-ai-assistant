#!/usr/bin/env python3
"""Set up Gmail credentials directly in AWS Secrets Manager."""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.gmail import get_credentials  # noqa: E402
from eaia.aws_secrets import SecretsManager  # noqa: E402


def main():
    """Set up Gmail credentials directly in AWS."""
    print("Gmail Setup with AWS Secrets Manager")
    print("=" * 50)
    
    # Check if we already have credentials in AWS
    try:
        sm = SecretsManager()
        sm.get_secret("eaia/gmail-credentials")
        print("✅ Gmail credentials already exist in AWS Secrets Manager")
        
        response = input("\nRe-authenticate? (y/n): ")
        if response.lower() != 'y':
            print("\nTo use these credentials, set:")
            print("  export USE_AWS_SECRETS=true")
            return 0
    except Exception:
        # No existing credentials, continue with setup
        pass
    
    print("\n📋 Prerequisites:")
    print("1. Google Cloud project with Gmail API enabled")
    print("2. OAuth 2.0 credentials downloaded")
    print("3. AWS CLI configured with proper permissions")
    
    # Get the OAuth credentials file path
    print("\n📁 Please provide the path to your OAuth credentials JSON file")
    print("   (downloaded from Google Cloud Console)")
    
    oauth_path = input("\nPath to OAuth JSON file: ").strip()
    
    # Remove quotes if present
    if oauth_path.startswith('"') and oauth_path.endswith('"'):
        oauth_path = oauth_path[1:-1]
    if oauth_path.startswith("'") and oauth_path.endswith("'"):
        oauth_path = oauth_path[1:-1]
    
    # Expand user path
    oauth_path = os.path.expanduser(oauth_path)
    
    if not os.path.exists(oauth_path):
        print(f"\n❌ File not found: {oauth_path}")
        return 1
    
    # Read the OAuth credentials
    try:
        with open(oauth_path, 'r') as f:
            oauth_content = f.read()
            # Validate it's JSON
            json.loads(oauth_content)
    except Exception as e:
        print(f"\n❌ Error reading OAuth file: {e}")
        return 1
    
    print("✅ OAuth credentials file loaded")
    
    # Temporarily save credentials for authentication
    secrets_dir = Path(__file__).parent.parent / "eaia" / ".secrets"
    secrets_dir.mkdir(parents=True, exist_ok=True)
    temp_secret_path = secrets_dir / "secrets.json"
    
    try:
        # Write OAuth credentials temporarily
        with open(temp_secret_path, 'w') as f:
            f.write(oauth_content)
        
        print("\n🔐 Authenticating with Google...")
        print("A browser window will open for authentication.")
        print("Please log in and grant permissions.")
        
        # Authenticate and get token
        get_credentials()
        
        print("\n✅ Authentication successful!")
        
        # Read the generated token
        token_path = secrets_dir / "token.json"
        with open(token_path, 'r') as f:
            token_content = f.read()
        
        # Now save to AWS Secrets Manager
        print("\n📤 Saving credentials to AWS Secrets Manager...")
        
        sm = SecretsManager()
        secret_value = {
            "gmail_secret": oauth_content,
            "gmail_token": token_content
        }
        
        arn = sm.create_or_update_secret(
            secret_name="eaia/gmail-credentials",
            secret_value=secret_value,
            description="Gmail OAuth credentials for EAIA"
        )
        
        print("✅ Credentials saved to AWS Secrets Manager!")
        print(f"   ARN: {arn}")
        
        # Clean up local files
        print("\n🧹 Cleaning up local files...")
        os.remove(temp_secret_path)
        os.remove(token_path)
        
        print("\n" + "=" * 50)
        print("✅ Setup complete!")
        print("\nTo use AWS Secrets Manager for Gmail:")
        print("  export USE_AWS_SECRETS=true")
        print("\nYour credentials are now securely stored in AWS.")
        print("No local credential files are needed.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        # Clean up on error
        if temp_secret_path.exists():
            os.remove(temp_secret_path)
        return 1
    finally:
        # Ensure cleanup
        if temp_secret_path.exists():
            os.remove(temp_secret_path)


if __name__ == "__main__":
    sys.exit(main()) 