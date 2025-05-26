# LangGraph Cloud Deployment Checklist

## Pre-Deployment Checklist

### ✅ Completed Items
- [x] Gmail credentials for both accounts stored in AWS
- [x] Configuration file customized with your preferences
- [x] Multi-account support added
- [x] Git repository initialized
- [x] AWS credentials available

### ⏳ Required for Deployment

#### 1. Get LangSmith API Key
- Go to [smith.langchain.com](https://smith.langchain.com)
- Sign up for LangSmith Plus account (required for LangGraph Cloud)
- Navigate to Settings → API Keys
- Create new API key (starts with `ls__`)

#### 2. Fork the Repository
Since you need your own GitHub repo for deployment:

```bash
# Option A: Push to your GitHub
git remote add origin https://github.com/YOUR_USERNAME/executive-ai-assistant.git
git commit -m "Initial setup with personalized configuration"
git push -u origin main

# Option B: Use the original repo and deploy from a branch
git checkout -b patrick-deployment
git commit -m "Personalized configuration for Patrick"
git push origin patrick-deployment
```

## Quick Deployment Steps

### Step 1: Prepare All Credentials

Run this to generate your deployment configuration:
```bash
# First, export your LangSmith API key
export LANGSMITH_API_KEY='ls__your_key_here'

# Then generate deployment config
poetry run python scripts/setup_langgraph_cloud_env.py
```

### Step 2: Deploy to LangGraph Cloud

1. Go to [smith.langchain.com/deployments](https://smith.langchain.com/deployments)
2. Click "New Deployment"
3. Select "LangGraph Cloud"
4. Configure:
   - **Name**: `eaia-patrick`
   - **Repository**: Your forked repo
   - **Branch**: `main` (or `patrick-deployment`)
   - **Root Directory**: (leave empty)

5. Add Environment Variables from `~/.eaia_deployment_env.txt`:
   ```
   OPENAI_API_KEY=...
   ANTHROPIC_API_KEY=...
   LANGSMITH_API_KEY=...
   GMAIL_SECRET=<entire JSON>
   GMAIL_TOKEN=<entire JSON>
   USE_AWS_SECRETS=false
   AWS_REGION=us-west-2
   ```

### Step 3: Initial Testing

Once deployed, test with recent emails:
```bash
# Get your deployment URL from LangGraph Cloud
export DEPLOYMENT_URL="https://your-deployment.api.langchain.com"

# Test ingestion (last 1 hour)
poetry run python scripts/run_ingest.py \
  --minutes-since 60 \
  --rerun 0 \
  --early 1 \
  --url $DEPLOYMENT_URL
```

### Step 4: Monitor Results

1. Check [smith.langchain.com](https://smith.langchain.com) for traces
2. Look for:
   - Email ingestion runs
   - Triage decisions
   - Any errors

### Step 5: Connect Agent Inbox

1. Go to [dev.agentinbox.ai](https://dev.agentinbox.ai)
2. Settings → Add Inbox:
   - **Graph ID**: `main`
   - **URL**: Your deployment URL
   - **Name**: `EAIA Production`

## Alternative: Local Testing First

If you want to test locally before deploying:

```bash
# Install dev server
poetry add --group dev "langgraph-cli[inmem]"

# Set environment variables
export USE_AWS_SECRETS=true
export AWS_REGION=us-west-2
export OPENAI_API_KEY='...'
export ANTHROPIC_API_KEY='...'
export LANGSMITH_API_KEY='...'

# Run local server
langgraph dev

# In another terminal, test ingestion
poetry run python scripts/run_ingest.py \
  --minutes-since 60 \
  --rerun 0 \
  --early 1
```

## Production Considerations

### Email Volume Management
- Start with `--minutes-since 60` (last hour)
- Gradually increase as you verify behavior
- Your patrick.smith@gmail.com has 285k+ emails - don't try to process all!

### Monitoring
- Set up LangSmith alerts for errors
- Check daily for the first week
- Review triage decisions regularly

### Cost Management
- Monitor API usage in OpenAI/Anthropic dashboards
- LangGraph Cloud pricing based on invocations
- Consider setting spending limits

## Troubleshooting

### Common Issues

1. **"Gmail API has not been used in project"**
   - Both projects have Gmail API enabled ✅

2. **Authentication errors**
   - Credentials are fresh and working ✅
   - Token refresh is handled automatically

3. **No emails processing**
   - Check time window in ingestion command
   - Verify email matches config.yaml
   - Look at triage rules

### Support Resources
- LangGraph docs: https://python.langchain.com/docs/langgraph
- LangSmith support: support@langchain.com
- Community: https://discord.gg/langchain

## Next Actions

1. **Get LangSmith Plus account** (if you don't have one)
2. **Fork/push repository to GitHub**
3. **Run deployment setup script** with LANGSMITH_API_KEY
4. **Deploy to LangGraph Cloud**
5. **Test with recent emails**
6. **Monitor and adjust**