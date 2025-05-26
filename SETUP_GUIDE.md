# Executive AI Assistant (EAIA) Setup Guide

This guide will walk you through setting up the Executive AI Assistant, including installing dependencies with Poetry, configuring credentials, and personalizing EAIA with your preferences.

## Prerequisites

- **Python 3.11 or 3.12** (Python 3.13+ is not yet fully supported due to dependency constraints)
- macOS, Linux, or Windows with WSL
- Gmail account (personal or Google Workspace)
- API keys from OpenAI, Anthropic, and LangSmith

## Step 1: Install Dependencies with Poetry

### 1.1 Install Poetry (if not already installed)

```bash
# Check if Poetry is installed
poetry --version

# If not installed, install it:
curl -sSL https://install.python-poetry.org | python3 -
```

After installation, restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc on macOS
```

### 1.2 Install Project Dependencies

From the project root directory, run:
```bash
poetry install
```

This will create a virtual environment and install all required dependencies.

## Step 2: Set Up Credentials

### 2.1 Create Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following content to `.env`:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here

# Optional: for production deployment
# LANGGRAPH_CLOUD_URL=your_langgraph_cloud_url_here
```

Replace the placeholder values with your actual API keys:
- **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com)
- **Anthropic API Key**: Get from [console.anthropic.com](https://console.anthropic.com)
- **LangSmith API Key**: Get from [smith.langchain.com](https://smith.langchain.com)

### 2.2 Set Up Google Gmail API

1. **Enable Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and click on it
   - Click "Enable"

2. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Configure OAuth consent screen (if prompted):
     - **For personal Gmail**: Select "External" as User Type
     - **For Google Workspace**: Select "Internal"
     - Add required information (app name, user support email, etc.)
     - Add your email as a test user (required for External type)
   - For Application type, select "Desktop app"
   - Name it "EAIA"
   - Click "Create"
   - Download the credentials JSON file

3. **Set Up Credentials Locally:**
   ```bash
   # Create secrets directory
   mkdir -p eaia/.secrets
   
   # Move downloaded credentials to secrets folder
   mv ~/Downloads/client_secret_*.json eaia/.secrets/secrets.json
   
   # Run Gmail authentication setup
   poetry run python scripts/setup_gmail.py
   ```
   
   This will open a browser window for authentication. Log in with your Gmail account and grant the necessary permissions.

## Step 3: Configure EAIA with Your Preferences

Edit the configuration file at `eaia/main/config.yaml`:

```bash
# Open with your preferred editor
nano eaia/main/config.yaml  # or vim, code, etc.
```

Update the following required fields:

### Basic Information
- **email**: Your Gmail address (e.g., "john.doe@gmail.com")
- **full_name**: Your full name (e.g., "John Doe")
- **name**: Your first name (e.g., "John")
- **background**: Brief description of who you are
- **timezone**: Your timezone (e.g., "PST", "EST", "UTC")

### Preferences
- **schedule_preferences**: How you like meetings scheduled
  ```yaml
  schedule_preferences: |
    - Default meeting length: 30 minutes
    - Prefer mornings for meetings
    - No meetings on Fridays
  ```

- **background_preferences**: Context for email responses
  ```yaml
  background_preferences: |
    - I work at TechCorp as a Product Manager
    - My assistant's name is Sarah
    - CC sarah@techcorp.com on scheduling emails
  ```

- **response_preferences**: Email writing guidelines
  ```yaml
  response_preferences: |
    - Be professional but friendly
    - Keep responses concise
    - Include my calendar link when scheduling
  ```

- **rewrite_preferences**: Your email tone and style
  ```yaml
  rewrite_preferences: |
    - Match the sender's tone
    - Use casual language with colleagues
    - Be more formal with clients
    - Avoid using emojis
  ```

### Triage Rules
- **triage_no**: Emails to ignore
  ```yaml
  triage_no: |
    - Spam and promotional emails
    - Automated notifications from services
    - Newsletter subscriptions
  ```

- **triage_notify**: Emails to notify you about (but not respond)
  ```yaml
  triage_notify: |
    - Documents shared with me
    - Meeting invitations
    - Important updates from team
  ```

- **triage_email**: Emails EAIA should draft responses to
  ```yaml
  triage_email: |
    - Direct questions from colleagues
    - Meeting scheduling requests
    - Client inquiries
    - Introduction requests
  ```

## Step 4: Test Your Setup

### Run Locally
```bash
# Install development server
pip install -U "langgraph-cli[inmem]"

# Start EAIA
poetry run langgraph dev
```

### Test Email Ingestion
In a new terminal:
```bash
# Ingest emails from the last 2 hours
poetry run python scripts/run_ingest.py --minutes-since 120 --rerun 1 --early 0
```

## Step 5: Access Agent Inbox

1. Go to [Agent Inbox](https://dev.agentinbox.ai/)
2. Click "Settings"
3. Add your LangSmith API key
4. Click "Add Inbox":
   - Assistant/Graph ID: `main`
   - Deployment URL: `http://127.0.0.1:2024`
   - Name: "Local EAIA"
5. Click "Submit"

You can now interact with EAIA through the Agent Inbox interface!

## Next Steps

- **Production Deployment**: See the README for instructions on deploying to LangGraph Cloud
- **Set Up Cron Jobs**: Automate email checking with `scripts/setup_cron.py`
- **Customize Behavior**: Modify the Python files in `eaia/main/` to customize EAIA's behavior

## Troubleshooting

### Poetry Installation Issues
- Make sure Python 3.11+ is installed
- Try using pipx: `pipx install poetry`

### Gmail Authentication Errors
- Ensure Gmail API is enabled in Google Cloud Console
- Check that your email is added as a test user (for External OAuth)
- Try deleting `eaia/.secrets/token.json` and re-running `setup_gmail.py`

### API Key Errors
- Verify all API keys in `.env` are correct
- Ensure you have sufficient credits/access for each service

### Configuration Issues
- Check YAML syntax in `config.yaml`
- Ensure all required fields are filled
- Use quotes for multi-line strings in YAML 