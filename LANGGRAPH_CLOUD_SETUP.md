# LangGraph Cloud Deployment Guide for EAIA

## Prerequisites
✅ Gmail credentials stored in AWS Secrets Manager
✅ Configuration file updated with your preferences
✅ LangSmith Plus account (required for LangGraph Cloud)

## Step 1: Prepare Environment Variables

You'll need to extract your credentials from AWS to set them as environment variables in LangGraph Cloud.

### Get Your Credentials

```bash
# Run this script to extract your credentials
cd "/Users/patricksmith/1. Highline Development/0l0/executive-ai-assistant-latest"
poetry run python scripts/export_credentials_for_langgraph.py
```

This will output the values you need for:
- `GMAIL_SECRET`
- `GMAIL_TOKEN`

## Step 2: Deploy to LangGraph Cloud

1. **Go to LangSmith**
   - Navigate to [smith.langchain.com](https://smith.langchain.com)
   - Click on "Deployments" in the left sidebar

2. **Create New Deployment**
   - Click "New Deployment"
   - Select "LangGraph Cloud"

3. **Configure Deployment**
   - **Name**: `executive-ai-assistant-patrick`
   - **GitHub Repository**: Your forked repo URL
   - **Branch**: `main`
   - **Root Directory**: Leave empty (uses root)

4. **Set Environment Variables**
   Add these environment variables:
   ```
   OPENAI_API_KEY=<your-openai-key>
   ANTHROPIC_API_KEY=<your-anthropic-key>
   GMAIL_SECRET=<output-from-script>
   GMAIL_TOKEN=<output-from-script>
   USE_AWS_SECRETS=false
   AWS_REGION=us-west-2
   AWS_ACCESS_KEY_ID=<your-aws-access-key>
   AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
   LANGSMITH_API_KEY=<your-langsmith-key>
   ```

5. **Deploy**
   - Click "Submit"
   - Wait for deployment (usually 2-5 minutes)

## Step 3: Set Up Email Ingestion

Once deployed, you'll get a deployment URL like:
`https://your-deployment-id.api.langchain.com`

### Test Manual Ingestion

```bash
# Test with emails from last 2 hours
python scripts/run_ingest.py \
  --minutes-since 120 \
  --rerun 0 \
  --early 1 \
  --url YOUR_DEPLOYMENT_URL
```

### Set Up Automatic Cron Job

```bash
# Configure automatic email checking every 10 minutes
python scripts/setup_cron.py --url YOUR_DEPLOYMENT_URL
```

## Step 4: Connect Agent Inbox

1. Go to [dev.agentinbox.ai](https://dev.agentinbox.ai)
2. Click "Settings"
3. Add your LangSmith API key
4. Click "Add Inbox":
   - **Assistant/Graph ID**: `main`
   - **Deployment URL**: Your deployment URL
   - **Name**: `EAIA Production`
5. Click "Submit"

## Step 5: Monitor and Test

### Initial Testing Checklist
- [ ] Send a test email to yourself
- [ ] Wait for ingestion (or run manually)
- [ ] Check Agent Inbox for the email
- [ ] Review the triage decision
- [ ] Test draft response generation

### Monitoring Commands

```bash
# Check recent email processing
python scripts/check_processing_status.py --url YOUR_DEPLOYMENT_URL

# View logs in LangSmith
# Go to Projects > Your Project > Runs
```

## Alternative: AWS Lambda Deployment

Since you're already using AWS, you might prefer Lambda:

### Benefits:
- No additional costs (use existing AWS account)
- Better integration with AWS Secrets Manager
- More control over scaling and monitoring

### Setup Guide:
1. Package the application
2. Create Lambda function
3. Set up EventBridge for scheduling
4. Configure API Gateway for webhook access

Would you like me to create the AWS Lambda deployment guide instead?

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify GMAIL_SECRET and GMAIL_TOKEN are correctly set
   - Check that values aren't truncated or escaped

2. **No Emails Processing**
   - Verify cron job is running
   - Check email filters in config.yaml
   - Look at LangSmith traces for errors

3. **Wrong Account**
   - Ensure config.yaml has correct email address
   - Verify credentials match the configured account

## Next Steps

1. Start with conservative triage rules
2. Monitor for a few days
3. Adjust config.yaml based on results
4. Gradually enable more automation

## Security Notes

- Credentials in environment variables are encrypted at rest
- Use read-only AWS credentials if possible
- Regularly rotate API keys
- Monitor LangSmith usage for anomalies