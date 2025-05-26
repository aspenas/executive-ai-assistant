#!/usr/bin/env python3
"""Migrate Gmail credentials from local files to AWS Secrets Manager."""

import sys
from pathlib import Path

# Add parent directory to path to import eaia modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.aws_secrets import SecretsManager  # noqa: E402


def main():
    """Migrate Gmail credentials to AWS Secrets Manager."""
    print("Gmail Credentials Migration to AWS Secrets Manager")
    print("=" * 50)
    
    # Check for local credential files
    secrets_dir = Path(__file__).parent.parent / "eaia" / ".secrets"
    secrets_path = secrets_dir / "secrets.json"
    token_path = secrets_dir / "token.json"
    
    if not secrets_path.exists() or not token_path.exists():
        print("❌ Local credential files not found!")
        print("   Expected files:")
        print(f"   - {secrets_path}")
        print(f"   - {token_path}")
        print("\nPlease run the Gmail setup first:")
        print("  python scripts/setup_gmail.py")
        return 1
    
    # Read local credentials
    print("\n📖 Reading local credentials...")
    try:
        with open(secrets_path, "r") as f:
            gmail_secret = f.read()
        with open(token_path, "r") as f:
            gmail_token = f.read()
        print("✅ Local credentials read successfully")
    except Exception as e:
        print(f"❌ Error reading local credentials: {e}")
        return 1
    
    # Initialize AWS Secrets Manager
    print("\n🔧 Initializing AWS Secrets Manager...")
    try:
        sm = SecretsManager()
        print("✅ AWS Secrets Manager initialized")
    except Exception as e:
        print(f"❌ Error initializing AWS Secrets Manager: {e}")
        print("\nPlease ensure:")
        print("  1. AWS CLI is configured: aws configure")
        print("  2. You have permissions to create/update secrets")
        return 1
    
    # Create/update the secret in AWS
    secret_name = "eaia/gmail-credentials"
    secret_value = {
        "gmail_secret": gmail_secret,
        "gmail_token": gmail_token
    }
    
    print("\n📤 Uploading credentials to AWS Secrets Manager...")
    print(f"   Secret name: {secret_name}")
    
    try:
        arn = sm.create_or_update_secret(
            secret_name=secret_name,
            secret_value=secret_value,
            description="Gmail OAuth credentials for EAIA"
        )
        print(f"✅ Secret created/updated successfully!")
        print(f"   ARN: {arn}")
    except Exception as e:
        print(f"❌ Error creating/updating secret: {e}")
        return 1
    
    # Verify the secret
    print("\n🔍 Verifying the secret...")
    try:
        retrieved = sm.get_secret(secret_name)
        if (retrieved.get("gmail_secret") == gmail_secret and 
            retrieved.get("gmail_token") == gmail_token):
            print("✅ Secret verified successfully!")
        else:
            print("❌ Secret verification failed - content mismatch")
            return 1
    except Exception as e:
        print(f"❌ Error verifying secret: {e}")
        return 1
    
    # Instructions for using AWS Secrets
    print("\n" + "=" * 50)
    print("✅ Migration completed successfully!")
    print("\nTo use AWS Secrets Manager for Gmail credentials:")
    print("1. Set the environment variable:")
    print("   export USE_AWS_SECRETS=true")
    print("\n2. Ensure AWS credentials are available:")
    print("   - Via AWS CLI: aws configure")
    print("   - Via environment variables:")
    print("     export AWS_ACCESS_KEY_ID=your-key")
    print("     export AWS_SECRET_ACCESS_KEY=your-secret")
    print("     export AWS_REGION=us-west-2")
    print("\n3. (Optional) Remove local credential files:")
    print(f"   rm -rf {secrets_dir}")
    print("\n4. When deploying to LangGraph Cloud, you no longer need")
    print("   GMAIL_SECRET and GMAIL_TOKEN environment variables.")
    print("   Just ensure the deployment has AWS credentials.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 