# AWS Secrets Manager Integration for EAIA

This guide explains how to use AWS Secrets Manager to store and retrieve Gmail credentials for the Executive AI Assistant (EAIA) project.

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws --version  # Should show version 2.x.x or higher
   aws configure  # Set up your AWS credentials
   ```

2. **boto3 installed** (already added to your project)
   ```bash
   poetry show boto3  # Should show boto3 package
   ```

3. **AWS IAM permissions** for Secrets Manager:
   - `secretsmanager:CreateSecret`
   - `secretsmanager:GetSecretValue`
   - `secretsmanager:UpdateSecret`
   - `secretsmanager:ListSecrets`

## Setup Steps

### 1. Test AWS Secrets Manager Connection

First, verify that AWS Secrets Manager is working correctly:

```bash
poetry run python scripts/test_aws_secrets.py
```

This will:
- Verify AWS credentials are configured
- List existing secrets
- Create a test secret
- Retrieve the test secret

### 2. Migrate Gmail Credentials to AWS

If you have existing Gmail credentials in local files, migrate them to AWS:

```bash
poetry run python scripts/migrate_secrets_to_aws.py
```

This script will:
- Read credentials from `eaia/.secrets/secrets.json` and `eaia/.secrets/token.json`
- Upload them to AWS Secrets Manager as `eaia/gmail-credentials`
- Verify the upload was successful

### 3. Configure EAIA to Use AWS Secrets

Set the environment variable to enable AWS Secrets Manager:

```bash
export USE_AWS_SECRETS=true
```

### 4. Test the Integration

Run your EAIA application to verify it can retrieve credentials from AWS:

```bash
poetry run python scripts/run_ingest.py --minutes-since 120
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `USE_AWS_SECRETS` | Set to `true` to use AWS Secrets Manager | Yes |
| `AWS_REGION` | AWS region for Secrets Manager (default: us-east-1) | No |
| `AWS_ACCESS_KEY_ID` | AWS access key (if not using AWS CLI) | Conditional |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (if not using AWS CLI) | Conditional |

## Deployment to LangGraph Cloud

When deploying to LangGraph Cloud with AWS Secrets Manager:

1. **Remove** these environment variables (no longer needed):
   - `GMAIL_SECRET`
   - `GMAIL_TOKEN`

2. **Add** these environment variables:
   - `USE_AWS_SECRETS=true`
   - `AWS_ACCESS_KEY_ID=your-key`
   - `AWS_SECRET_ACCESS_KEY=your-secret`
   - `AWS_REGION=us-west-2` (or your preferred region)

## Troubleshooting

### "No module named 'boto3'"
- Run `poetry install` to ensure all dependencies are installed
- Use `poetry run` prefix for all Python commands

### "Secret not found"
- Ensure the secret name is correct: `eaia/gmail-credentials`
- Check your AWS region matches where the secret was created
- Verify IAM permissions

### "Invalid credentials"
- Run `aws configure list` to check AWS configuration
- Ensure AWS credentials have not expired
- Check IAM permissions for Secrets Manager

### Fallback to Environment Variables
If AWS Secrets Manager fails, the system will automatically fall back to using:
- `GMAIL_SECRET` environment variable
- `GMAIL_TOKEN` environment variable

## Security Best Practices

1. **Never commit AWS credentials** to version control
2. **Use IAM roles** when running on AWS infrastructure
3. **Rotate credentials regularly** using AWS Secrets Manager rotation
4. **Limit IAM permissions** to only what's needed
5. **Use different AWS accounts** for development and production

## Additional AWS Secrets

You can store other secrets in AWS Secrets Manager:

```python
from eaia.aws_secrets import get_secret, get_secrets_manager

# Get a secret
api_key = get_secret("eaia/openai-api-key")

# Create/update a secret
sm = get_secrets_manager()
sm.create_or_update_secret(
    "eaia/my-secret",
    {"key": "value"},
    description="My secret description"
)
``` 