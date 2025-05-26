#!/usr/bin/env python3
"""Final setup for patrick.smith@gmail.com ensuring correct authentication."""

import sys
import json
import os
from pathlib import Path
import webbrowser

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.gmail import get_credentials  # noqa: E402
from eaia.aws_secrets import SecretsManager  # noqa: E402


def main():
    """Set up Gmail credentials for patrick.smith@gmail.com."""
    print("Gmail Setup for patrick.smith@gmail.com - Final Configuration")
    print("=" * 60)
    
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
    
    account_email = "patrick.smith@gmail.com"
    safe_email = account_email.replace('@', '-at-').replace('.', '-dot-')
    secret_name = f"eaia/gmail-credentials-{safe_email}-v2"
    
    # Use the tiller-auto OAuth file
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
            print(f"   Client ID: {oauth_data.get('installed', {}).get('client_id', 'Unknown')[:30]}...")
    except Exception as e:
        print(f"\n❌ Error reading OAuth file: {e}")
        return 1
    
    print("\n" + "⚠️ " * 20)
    print("CRITICAL AUTHENTICATION STEPS:")
    print("1. A browser window will open")
    print("2. You MUST sign out of all Google accounts first")
    print("3. Then sign in ONLY with: patrick.smith@gmail.com")
    print("4. Grant all requested permissions")
    print("⚠️ " * 20)
    
    input("\nPress Enter when you're ready to authenticate...")
    
    # Open Google logout page first
    print("\n🔓 Opening Google logout page...")
    webbrowser.open("https://accounts.google.com/Logout")
    
    input("\nPress Enter after you've logged out of all Google accounts...")
    
    # Temporarily save credentials for authentication
    secrets_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Write OAuth credentials temporarily
        with open(secret_path, 'w') as f:
            f.write(oauth_content)
        
        print(f"\n🔐 Now authenticating with Google...")
        print(f"⚠️  SIGN IN WITH: {account_email}")
        
        # Authenticate and get token
        get_credentials()
        
        print("\n✅ Authentication completed!")
        
        # Read the generated token
        with open(token_path, 'r') as f:
            token_content = f.read()
            token_data = json.loads(token_content)
        
        # Verify we got the right account by checking the token
        print("\n🔍 Verifying account...")
        
        # Now save to AWS Secrets Manager
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
            description=f"Gmail OAuth credentials for {account_email} (tiller-auto project)"
        )
        
        print("✅ Credentials saved to AWS Secrets Manager!")
        print(f"   ARN: {arn}")
        print(f"   Secret name: {secret_name}")
        
        # Clean up local files
        print("\n🧹 Cleaning up local files...")
        os.remove(secret_path)
        os.remove(token_path)
        
        print("\n" + "=" * 60)
        print("✅ Setup complete!")
        print(f"\nGmail accounts configured in AWS:")
        print("1. patrick@highline.work -> eaia/gmail-credentials")
        print(f"2. {account_email} -> {secret_name}")
        
        print("\n🔍 Let's verify the account immediately...")
        
        # Quick verification
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials.from_authorized_user_info(json.loads(token_content))
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        actual_email = profile.get('emailAddress')
        
        if actual_email == account_email:
            print(f"✅ VERIFIED: Successfully configured {actual_email}")
        else:
            print(f"⚠️  WARNING: Configured account is {actual_email}, not {account_email}")
            print("   You may need to run the setup again.")
        
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