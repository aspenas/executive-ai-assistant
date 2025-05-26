#!/usr/bin/env python3
"""Set up Gmail credentials for patrick.smith@gmail.com using tiller-auto project."""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.gmail import get_credentials  # noqa: E402
from eaia.aws_secrets import SecretsManager  # noqa: E402


def main():
    """Set up Gmail credentials for patrick.smith@gmail.com."""
    print("Gmail Setup for patrick.smith@gmail.com (Personal Account)")
    print("=" * 60)
    
    # Clear any existing cached credentials first
    secrets_dir = Path(__file__).parent.parent / "eaia" / ".secrets"
    token_path = secrets_dir / "token.json"
    secret_path = secrets_dir / "secrets.json"
    
    if token_path.exists():
        os.remove(token_path)
        print("✅ Cleared existing token cache")
    if secret_path.exists():
        os.remove(secret_path)
        print("✅ Cleared existing secrets cache")
    
    account_email = "patrick.smith@gmail.com"
    safe_email = account_email.replace('@', '-at-').replace('.', '-dot-')
    secret_name = f"eaia/gmail-credentials-{safe_email}"
    
    # Use the tiller-auto OAuth file (different from the one used for highline.work)
    oauth_path = "/Users/patricksmith/Downloads/client_secret_114921781254-s50uqje14285om1b218dofle8noglqnr.apps.googleusercontent.com.json"
    
    # Ensure the file exists
    oauth_path = Path(oauth_path).expanduser()
    if not oauth_path.exists():
        print(f"❌ OAuth file not found: {oauth_path}")
        return 1
    
    print(f"✅ OAuth credentials file loaded")
    
    # Read the OAuth credentials
    try:
        with open(oauth_path, 'r') as f:
            oauth_content = f.read()
            oauth_data = json.loads(oauth_content)
            project_id = oauth_data.get('installed', {}).get('project_id', 'Unknown')
            print(f"   Project ID: {project_id}")
            print(f"   Note: Using different project than highline.work to avoid conflicts")
    except Exception as e:
        print(f"\n❌ Error reading OAuth file: {e}")
        return 1
    
    # Temporarily save credentials for authentication
    secrets_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Write OAuth credentials temporarily
        with open(secret_path, 'w') as f:
            f.write(oauth_content)
        
        print(f"\n🔐 Authenticating with Google for {account_email}...")
        print("A browser window will open for authentication.")
        print(f"\n⚠️  CRITICAL: You MUST log in with {account_email}")
        print("   If you see patrick@highline.work, click 'Use another account'")
        print("   or sign out and sign in with patrick.smith@gmail.com")
        
        # Authenticate and get token
        get_credentials()
        
        print("\n✅ Authentication successful!")
        
        # Read the generated token
        with open(token_path, 'r') as f:
            token_content = f.read()
        
        # Now save to AWS Secrets Manager
        print("\n📤 Saving credentials to AWS Secrets Manager...")
        
        sm = SecretsManager()
        secret_value = {
            "gmail_secret": oauth_content,
            "gmail_token": token_content,
            "account_email": account_email,
            "project_id": project_id
        }
        
        # Use a new secret name to avoid deletion conflicts
        secret_name_v2 = f"{secret_name}-v2"
        
        arn = sm.create_or_update_secret(
            secret_name=secret_name_v2,
            secret_value=secret_value,
            description=f"Gmail OAuth credentials for {account_email} (tiller-auto project)"
        )
        
        print("✅ Credentials saved to AWS Secrets Manager!")
        print(f"   ARN: {arn}")
        print(f"   Secret name: {secret_name_v2}")
        
        # Clean up local files
        print("\n🧹 Cleaning up local files...")
        os.remove(secret_path)
        os.remove(token_path)
        
        print("\n" + "=" * 60)
        print("✅ Setup complete!")
        print(f"\nBoth Gmail accounts are now configured in AWS:")
        print("1. patrick@highline.work -> eaia/gmail-credentials (project-0l0)")
        print(f"2. {account_email} -> {secret_name_v2} ({project_id})")
        print("\nYour credentials are securely stored in AWS.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        # Clean up on error
        if secret_path.exists():
            os.remove(secret_path)
        return 1
    finally:
        # Ensure cleanup
        if secret_path.exists() and secret_path.exists():
            os.remove(secret_path)


if __name__ == "__main__":
    # Set correct AWS region
    os.environ['AWS_REGION'] = 'us-west-2'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    sys.exit(main())