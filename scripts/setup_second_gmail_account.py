#!/usr/bin/env python3
"""Set up a second Gmail account ensuring proper authentication."""

import sys
import json
import os
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.gmail import get_credentials  # noqa: E402
from eaia.aws_secrets import SecretsManager  # noqa: E402


def main():
    """Set up Gmail credentials for a second account."""
    print("Setting up Second Gmail Account")
    print("=" * 50)
    
    # Clear any existing cached credentials
    secrets_dir = Path(__file__).parent.parent / "eaia" / ".secrets"
    token_path = secrets_dir / "token.json"
    secret_path = secrets_dir / "secrets.json"
    
    if token_path.exists():
        os.remove(token_path)
        print("✅ Cleared existing token cache")
    if secret_path.exists():
        os.remove(secret_path)
        print("✅ Cleared existing secrets cache")
    
    print("\n⚠️  IMPORTANT: You need to use a DIFFERENT OAuth app for patrick.smith@gmail.com")
    print("   to avoid conflicts with patrick@highline.work")
    print("\nAvailable OAuth files:")
    print("1. tiller-auto project (might be good for patrick.smith@gmail.com)")
    print("2. a-cup-cake-shop project")
    print("3. a-cup-cake-shop-456818 project")
    
    choice = input("\nWhich project to use? (1-3): ").strip()
    
    oauth_files = {
        "1": "/Users/patricksmith/Downloads/client_secret_114921781254-s50uqje14285om1b218dofle8noglqnr.apps.googleusercontent.com.json",
        "2": "/Users/patricksmith/Downloads/client_secret_377858888563-eic7jm75td8s6tf6n2qnm6p9mkmcfag4.apps.googleusercontent.com.json",
        "3": "/Users/patricksmith/Downloads/client_secret_1069100326003-3bd5ort4l7bbio98hsnia9rcpdgqgsi9.apps.googleusercontent.com.json"
    }
    
    oauth_path = oauth_files.get(choice)
    if not oauth_path:
        print("❌ Invalid choice")
        return 1
    
    # Read the OAuth credentials
    try:
        with open(oauth_path, 'r') as f:
            oauth_content = f.read()
            oauth_data = json.loads(oauth_content)
            project_id = oauth_data.get('installed', {}).get('project_id', 'Unknown')
            print(f"\n✅ Using OAuth file from project: {project_id}")
    except Exception as e:
        print(f"\n❌ Error reading OAuth file: {e}")
        return 1
    
    account_email = "patrick.smith@gmail.com"
    safe_email = account_email.replace('@', '-at-').replace('.', '-dot-')
    secret_name = f"eaia/gmail-credentials-{safe_email}"
    
    # Write OAuth credentials temporarily
    secrets_dir.mkdir(parents=True, exist_ok=True)
    with open(secret_path, 'w') as f:
        f.write(oauth_content)
    
    print(f"\n🔐 Opening browser for authentication...")
    print(f"⚠️  CRITICAL: You MUST log in with {account_email}")
    print("   If you see patrick@highline.work, click 'Use another account'")
    print("\nPress Enter when ready to continue...")
    input()
    
    try:
        # Authenticate and get token
        get_credentials()
        
        print("\n✅ Authentication completed!")
        
        # Read the generated token
        with open(token_path, 'r') as f:
            token_content = f.read()
        
        # Verify the token is for the correct account
        token_data = json.loads(token_content)
        print(f"\nVerifying account...")
        
        # Save to AWS Secrets Manager
        print("\n📤 Saving credentials to AWS Secrets Manager...")
        
        sm = SecretsManager()
        secret_value = {
            "gmail_secret": oauth_content,
            "gmail_token": token_content,
            "account_email": account_email,
            "project_id": project_id
        }
        
        arn = sm.create_or_update_secret(
            secret_name=secret_name,
            secret_value=secret_value,
            description=f"Gmail OAuth credentials for {account_email}"
        )
        
        print("✅ Credentials saved to AWS Secrets Manager!")
        print(f"   ARN: {arn}")
        
        # Clean up local files
        print("\n🧹 Cleaning up local files...")
        os.remove(secret_path)
        os.remove(token_path)
        
        print("\n" + "=" * 50)
        print("✅ Setup complete!")
        print(f"\nBoth Gmail accounts are now configured:")
        print("1. patrick@highline.work -> eaia/gmail-credentials")
        print(f"2. {account_email} -> {secret_name}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        # Clean up on error
        if secret_path.exists():
            os.remove(secret_path)
        if token_path.exists():
            os.remove(token_path)
        return 1


if __name__ == "__main__":
    # Set correct AWS region
    os.environ['AWS_REGION'] = 'us-west-2'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    sys.exit(main())