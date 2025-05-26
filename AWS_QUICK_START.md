# EAIA AWS Secrets Manager - Quick Start

## ✅ Setup Complete
Your Gmail credentials are stored in AWS Secrets Manager (`us-west-2` region).

## 🚀 Quick Commands

### Test AWS Integration
```bash
USE_AWS_SECRETS=true AWS_REGION=us-west-2 poetry run python scripts/test_aws_gmail_integration.py
```

### Fetch Recent Emails
```bash
# Last 24 hours
poetry run python scripts/fetch_emails_simple.py --minutes-since 1440

# Last week
poetry run python scripts/fetch_emails_simple.py --minutes-since 10080
```

### Run Full EAIA (requires LangGraph server)
```bash
# Terminal 1: Start LangGraph
poetry run langgraph dev

# Terminal 2: Run ingest
USE_AWS_SECRETS=true AWS_REGION=us-west-2 poetry run python scripts/run_ingest.py --minutes-since 120
```

## 📝 Key Files
- `eaia/aws_secrets.py` - AWS integration module
- `scripts/fetch_emails_simple.py` - Simple email viewer
- `scripts/test_aws_gmail_integration.py` - Test script
- `AWS_USAGE_GUIDE.md` - Full documentation

## 🔑 Environment Variables
```bash
export USE_AWS_SECRETS=true
export AWS_REGION=us-west-2
```

Your email: `patrick@highline.work` ✅ 