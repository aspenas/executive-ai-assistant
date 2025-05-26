#!/usr/bin/env python3
"""Set up and verify all environment variables needed for LangGraph Cloud deployment."""

import os
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set AWS environment
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

from eaia.aws_secrets import SecretsManager


def check_env_var(name: str, required: bool = True) -> tuple[bool, str]:
    """Check if environment variable exists."""
    value = os.environ.get(name, "")
    if value:
        # Mask sensitive values
        if "KEY" in name or "SECRET" in name or "TOKEN" in name:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            return True, masked
        return True, value
    return False, ""


def main():
    """Check and prepare all environment variables for LangGraph Cloud."""
    print("LangGraph Cloud Environment Setup")
    print("=" * 60)
    
    # Required environment variables
    env_vars = {
        "OPENAI_API_KEY": {"required": True, "source": "env"},
        "ANTHROPIC_API_KEY": {"required": True, "source": "env"},
        "LANGSMITH_API_KEY": {"required": True, "source": "env"},
        "AWS_ACCESS_KEY_ID": {"required": False, "source": "env"},
        "AWS_SECRET_ACCESS_KEY": {"required": False, "source": "env"},
    }
    
    print("\n📋 Checking Environment Variables:")
    print("-" * 40)
    
    missing = []
    found = []
    
    for var_name, config in env_vars.items():
        exists, value = check_env_var(var_name, config["required"])
        if exists:
            print(f"✅ {var_name}: {value}")
            found.append((var_name, os.environ.get(var_name)))
        else:
            if config["required"]:
                print(f"❌ {var_name}: NOT FOUND (required)")
                missing.append(var_name)
            else:
                print(f"⚠️  {var_name}: NOT FOUND (optional)")
    
    # Get Gmail credentials from AWS
    print("\n📧 Gmail Credentials from AWS:")
    print("-" * 40)
    
    try:
        sm = SecretsManager()
        secret_data = sm.get_secret("eaia/gmail-credentials")
        
        gmail_secret = secret_data.get("gmail_secret", "")
        gmail_token = secret_data.get("gmail_token", "")
        
        if gmail_secret and gmail_token:
            print("✅ GMAIL_SECRET: Found in AWS")
            print("✅ GMAIL_TOKEN: Found in AWS")
            found.append(("GMAIL_SECRET", gmail_secret))
            found.append(("GMAIL_TOKEN", gmail_token))
        else:
            print("❌ Gmail credentials incomplete in AWS")
            missing.extend(["GMAIL_SECRET", "GMAIL_TOKEN"])
            
    except Exception as e:
        print(f"❌ Error accessing AWS: {e}")
        missing.extend(["GMAIL_SECRET", "GMAIL_TOKEN"])
    
    # Summary
    print("\n" + "=" * 60)
    print("DEPLOYMENT READINESS")
    print("=" * 60)
    
    if not missing:
        print("✅ All required environment variables are available!")
        
        # Create deployment config file
        deployment_file = Path.home() / ".eaia_deployment_env.txt"
        
        print(f"\n💾 Creating deployment configuration file...")
        with open(deployment_file, 'w') as f:
            f.write("# LangGraph Cloud Environment Variables\n")
            f.write("# Copy these to your deployment configuration\n\n")
            
            for var_name, value in found:
                if var_name in ["GMAIL_SECRET", "GMAIL_TOKEN"]:
                    # These need special handling - full value
                    f.write(f"{var_name}={value}\n\n")
                else:
                    # Regular env vars
                    f.write(f"{var_name}={value}\n")
            
            # Add static configuration
            f.write("\n# Static Configuration\n")
            f.write("USE_AWS_SECRETS=false\n")
            f.write("AWS_REGION=us-west-2\n")
        
        print(f"✅ Saved to: {deployment_file}")
        print("\n📌 Next Steps:")
        print("1. Open the deployment file and copy ALL variables")
        print("2. Go to smith.langchain.com → Deployments")
        print("3. Create new deployment with these environment variables")
        print("4. Delete the deployment file after use!")
        
    else:
        print(f"❌ Missing required variables: {', '.join(missing)}")
        print("\n📌 How to fix:")
        
        if "OPENAI_API_KEY" in missing:
            print("\nOPENAI_API_KEY:")
            print("  export OPENAI_API_KEY='your-key-here'")
            print("  Get from: https://platform.openai.com/api-keys")
            
        if "ANTHROPIC_API_KEY" in missing:
            print("\nANTHROPIC_API_KEY:")
            print("  export ANTHROPIC_API_KEY='your-key-here'")
            print("  Get from: https://console.anthropic.com/settings/keys")
            
        if "LANGSMITH_API_KEY" in missing:
            print("\nLANGSMITH_API_KEY:")
            print("  export LANGSMITH_API_KEY='your-key-here'")
            print("  Get from: https://smith.langchain.com/settings")
    
    # Check for existing deployment
    print("\n🔍 Checking for existing LangGraph deployments...")
    if os.environ.get("LANGSMITH_API_KEY"):
        print("✅ LangSmith API key found - you can check deployments at:")
        print("   https://smith.langchain.com/deployments")
    
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())