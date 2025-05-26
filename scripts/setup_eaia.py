#!/usr/bin/env python3
"""
EAIA Setup Script - Helps with initial setup of Executive AI Assistant
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"\n❌ Command failed with exit code {result.returncode}")
        if result.stdout:
            print("Output:", result.stdout)
        if result.stderr:
            print("Error:", result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    
    return result


def check_poetry_installed() -> bool:
    """Check if Poetry is installed."""
    result = run_command(["poetry", "--version"], check=False)
    return result.returncode == 0


def install_poetry():
    """Install Poetry if not already installed."""
    if not check_poetry_installed():
        print("\n📦 Poetry not found. Installing Poetry...")
        # Use the official installer
        cmd = ["curl", "-sSL", "https://install.python-poetry.org", "|",
               "python3", "-"]
        run_command(cmd, shell=True)
        print("✅ Poetry installed successfully!")
        print("⚠️  Please restart your terminal and run this script again.")
        sys.exit(0)
    else:
        print("✅ Poetry is already installed")


def install_dependencies():
    """Install project dependencies using Poetry."""
    print("\n📦 Installing project dependencies with Poetry...")
    try:
        run_command(["poetry", "install"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're in the project root directory")
        print("2. Try running 'poetry lock --no-update' first")
        print("3. Check Python version: poetry requires Python 3.11+")
        print("4. Try 'poetry env use python3.11' if you have multiple Python versions")
        sys.exit(1)


def setup_env_file():
    """Create or update .env file with required variables."""
    env_path = Path(".env")
    env_template = """# Executive AI Assistant Environment Variables

# API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LANGSMITH_API_KEY=

# Optional: LangGraph Cloud URL (for production deployment)
# LANGGRAPH_CLOUD_URL=
"""
    
    if not env_path.exists():
        print("\n📝 Creating .env file...")
        with open(env_path, 'w') as f:
            f.write(env_template)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    # Load existing env vars
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Prompt for missing API keys
    print("\n🔑 Setting up API credentials...")
    
    required_keys = {
        'OPENAI_API_KEY': 'OpenAI API key (from platform.openai.com)',
        'ANTHROPIC_API_KEY': 'Anthropic API key (from console.anthropic.com)',
        'LANGSMITH_API_KEY': 'LangSmith API key (from smith.langchain.com)'
    }
    
    updated = False
    for key, description in required_keys.items():
        if key not in env_vars or not env_vars[key]:
            value = input(f"Enter your {description}: ").strip()
            if value:
                env_vars[key] = value
                updated = True
            else:
                print(f"⚠️  Skipping {key} - "
                      "you'll need to add it manually later")
    
    # Write back to .env if updated
    if updated:
        with open(env_path, 'w') as f:
            f.write(env_template)
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print("✅ API keys saved to .env file")


def setup_google_credentials():
    """Guide user through Google API setup."""
    print("\n🔐 Setting up Google Gmail API credentials...")
    print("\nPlease follow these steps:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Gmail API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API' and click on it")
    print("   - Click 'Enable'")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - If prompted, configure the OAuth consent screen first:")
    print("     * For personal Gmail: Select 'External' as User Type")
    print("     * For Google Workspace: Select 'Internal'")
    print("     * Add your email as a test user (for External type)")
    print("   - Application type: 'Desktop app'")
    print("   - Name: 'EAIA'")
    print("5. Download the credentials JSON file")
    
    input("\nPress Enter when you've downloaded the credentials JSON file...")
    
    # Create .secrets directory
    secrets_dir = Path("eaia/.secrets")
    secrets_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created secrets directory at {secrets_dir}")
    
    # Prompt for credentials file
    while True:
        cred_path = input("\nEnter the path to your downloaded credentials JSON file: ").strip()
        cred_path = Path(cred_path).expanduser()
        
        if cred_path.exists() and cred_path.suffix == '.json':
            # Copy to secrets directory
            dest_path = secrets_dir / "secrets.json"
            shutil.copy2(cred_path, dest_path)
            print(f"✅ Credentials copied to {dest_path}")
            
            # Run Gmail setup script
            print("\n🔧 Running Gmail authentication setup...")
            result = run_command(["poetry", "run", "python", "scripts/setup_gmail.py"])
            if result.returncode == 0:
                print("✅ Gmail authentication completed successfully!")
            else:
                print("❌ Gmail authentication failed. Please check the error above.")
            break
        else:
            print("❌ File not found or not a JSON file. Please try again.")

def setup_config():
    """Help user configure EAIA settings."""
    config_path = Path("eaia/main/config.yaml")
    
    print("\n⚙️  Configuring EAIA settings...")
    print(f"\nPlease edit the configuration file at: {config_path}")
    print("\nRequired settings to update:")
    print("- email: Your Gmail address")
    print("- full_name: Your full name")
    print("- name: Your first name")
    print("- background: Brief description of who you are")
    print("- timezone: Your timezone (e.g., 'PST', 'EST', 'UTC')")
    print("- schedule_preferences: How you like meetings scheduled")
    print("- background_preferences: Any background info needed for responses")
    print("- response_preferences: How you want emails to be written")
    print("- rewrite_preferences: Your email tone and style preferences")
    print("- triage_no: Guidelines for emails to ignore")
    print("- triage_notify: Guidelines for emails to notify you about")
    print("- triage_email: Guidelines for emails EAIA should draft responses to")
    
    edit_now = input("\nWould you like to edit the config file now? (y/n): ").strip().lower()
    if edit_now == 'y':
        # Try to open with default editor
        editor = os.environ.get('EDITOR', 'nano' if sys.platform != 'darwin' else 'open')
        subprocess.run([editor, str(config_path)])

def check_python_version():
    """Check if Python version is compatible."""
    version_info = sys.version_info
    if version_info.major != 3 or version_info.minor < 11:
        print(f"❌ Python 3.11+ is required, but you have Python {version_info.major}.{version_info.minor}")
        return False
    elif version_info.minor > 12:
        print(f"⚠️  Warning: You're using Python {version_info.major}.{version_info.minor}")
        print("   Some dependencies may not support Python 3.13+ yet.")
        print("   Recommended: Use Python 3.11 or 3.12 for best compatibility")
        print("\n   To use Python 3.11 or 3.12:")
        print("   1. Install Python 3.11 or 3.12 if not already installed")
        print("   2. Run: poetry env use python3.11")
        print("      or: poetry env use python3.12")
        return False
    return True


def main():
    """Main setup function."""
    print("🚀 Executive AI Assistant (EAIA) Setup")
    print("=====================================")
    
    # Check we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: Please run this script from the EAIA project root directory")
        sys.exit(1)
    
    # Check Python version
    if not check_python_version():
        continue_anyway = input("\nDo you want to continue anyway? (y/n): ").strip().lower()
        if continue_anyway != 'y':
            print("Exiting setup. Please install Python 3.11 or 3.12 and try again.")
            sys.exit(1)
    
    # Step 1: Install Poetry if needed
    install_poetry()
    
    # Step 2: Install dependencies
    install_dependencies()
    
    # Step 3: Setup environment variables
    setup_env_file()
    
    # Step 4: Setup Google credentials
    setup_google = input("\nDo you want to set up Google Gmail API credentials now? (y/n): ").strip().lower()
    if setup_google == 'y':
        setup_google_credentials()
    else:
        print("⚠️  Skipping Google setup - you'll need to set this up manually later")
    
    # Step 5: Configure EAIA
    setup_config()
    
    print("\n✅ EAIA setup complete!")
    print("\nNext steps:")
    print("1. Make sure all API keys are set in .env")
    print("2. Ensure Google credentials are set up in eaia/.secrets/")
    print("3. Update config.yaml with your preferences")
    print("4. Run 'poetry run langgraph dev' to start EAIA locally")
    print("5. Or deploy to LangGraph Cloud for production use")

if __name__ == "__main__":
    main() 