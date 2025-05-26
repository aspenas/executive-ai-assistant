# Using EAIA with AWS Secrets Manager

Now that your Gmail credentials are stored in AWS Secrets Manager, here's how to use them with various EAIA scripts.

## Environment Setup

Always set these environment variables before running scripts:

```bash
export USE_AWS_SECRETS=true
export AWS_REGION=us-west-2
```

Or prefix each command with them:

```bash
USE_AWS_SECRETS=true AWS_REGION=us-west-2 poetry run python scripts/...
```

## Available Scripts

### 1. Test AWS Integration
Verify that AWS Secrets Manager is working correctly:

```bash
USE_AWS_SECRETS=true AWS_REGION=us-west-2 poetry run python scripts/test_aws_gmail_integration.py
```

### 2. Fetch Emails (Simple)
View emails without processing them through LangGraph:

```bash
# Last 2 hours (default)
poetry run python scripts/fetch_emails_simple.py

# Last 24 hours
poetry run python scripts/fetch_emails_simple.py --minutes-since 1440

# Last week
poetry run python scripts/fetch_emails_simple.py --minutes-since 10080
```

### 3. Run Email Ingest (Requires LangGraph)
Process emails through the EAIA LangGraph application:

```bash
# First, start the LangGraph server locally:
poetry run langgraph dev

# Then in another terminal, run ingest:
USE_AWS_SECRETS=true AWS_REGION=us-west-2 poetry run python scripts/run_ingest.py --minutes-since 120

# Or with a remote LangGraph URL:
USE_AWS_SECRETS=true AWS_REGION=us-west-2 poetry run python scripts/run_ingest.py --url https://your-langgraph-url --minutes-since 120
```

### 4. Calendar Operations
The Gmail credentials also include Google Calendar access:

```python
from eaia.gmail import get_events_for_days, send_calendar_invite

# Set environment first
os.environ["USE_AWS_SECRETS"] = "true"
os.environ["AWS_REGION"] = "us-west-2"

# Get calendar events
events = get_events_for_days(["26-05-2025", "27-05-2025"])

# Send calendar invite
send_calendar_invite(
    emails=["attendee@example.com"],
    title="Meeting",
    start_time="2025-05-26T10:00:00",
    end_time="2025-05-26T11:00:00",
    email_address="patrick@highline.work",
    timezone="PST"
)
```

## Deployment Notes

### For LangGraph Cloud
When deploying to LangGraph Cloud, add these environment variables:
- `USE_AWS_SECRETS=true`
- `AWS_ACCESS_KEY_ID=your-key`
- `AWS_SECRET_ACCESS_KEY=your-secret`
- `AWS_REGION=us-west-2`

You no longer need `GMAIL_SECRET` and `GMAIL_TOKEN` environment variables.

### For Local Development
Make sure AWS CLI is configured:
```bash
aws configure list
```

Or set AWS credentials via environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-west-2
```

## Troubleshooting

### Region Issues
If you see "Could not connect to the endpoint URL", check your AWS region:
```bash
# List secrets in the correct region
aws secretsmanager list-secrets --region us-west-2
```

### Permission Issues
Ensure your AWS IAM user/role has these permissions:
- `secretsmanager:GetSecretValue` for "eaia/gmail-credentials"

### Testing Connection
```bash
# Test AWS CLI access to the secret
aws secretsmanager get-secret-value --secret-id eaia/gmail-credentials --region us-west-2 --query SecretString --output text | jq .
```

## Security Best Practices

1. **Never commit AWS credentials** to version control
2. **Use IAM roles** when running on AWS infrastructure
3. **Rotate AWS access keys** regularly
4. **Use least privilege** - only grant necessary permissions
5. **Monitor access** - use AWS CloudTrail to audit secret access 