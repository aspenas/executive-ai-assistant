# EAIA Implementation Plan

## Current Status
✅ **Gmail Authentication Complete**
- Both Gmail accounts configured in AWS Secrets Manager:
  - patrick@highline.work (5,876 messages)
  - patrick.smith@gmail.com (285,856 messages)
- Credentials stored securely with no local files needed

## Immediate Next Steps

### 1. Update Credentials System (Priority: HIGH)
The current codebase expects credentials in local files, but we're using AWS Secrets Manager.

**Actions needed:**
- Modify `eaia/gmail.py` to properly handle AWS Secrets Manager credentials (already partially done)
- Update the credential flow in `scripts/setup_gmail.py` to support AWS
- Test the integration with the main application

### 2. Configuration Setup (Priority: HIGH)
Create and configure `eaia/main/config.yaml` with your personal settings:

```yaml
email: patrick@highline.work  # Or patrick.smith@gmail.com
full_name: Patrick Smith
name: Patrick
background: [Add your professional background]
timezone: [Your timezone, e.g., America/Denver]
schedule_preferences: |
  - Default meeting length: 30 minutes
  - Prefer mornings for meetings
  - No meetings on Fridays
background_preferences: |
  - Key coworkers: [List important contacts]
  - Company context: [Your company/role info]
response_preferences: |
  - Include calendar links when scheduling
  - Professional but friendly tone
rewrite_preferences: |
  - Concise and clear
  - Action-oriented
triage_no: |
  - Marketing emails
  - Newsletters (unless specifically requested)
  - Automated notifications
triage_notify: |
  - Emails from VIP contacts
  - Urgent requests
  - Financial/legal matters
triage_email: |
  - Meeting requests
  - Direct questions
  - Action items
```

### 3. Multi-Account Strategy (Priority: MEDIUM)
Since you have two Gmail accounts, decide on the approach:

**Option A: Single Assistant, Multiple Accounts**
- Modify the codebase to monitor both accounts
- Add account selection logic in email processing
- Update configuration to handle multiple accounts

**Option B: Two Separate Instances**
- Deploy two instances of EAIA
- One for patrick@highline.work (professional)
- One for patrick.smith@gmail.com (personal)
- Different configuration files for each

**Recommendation:** Start with Option B (simpler), then migrate to Option A if needed.

### 4. Local Testing Setup (Priority: HIGH)
Before deploying to production:

1. **Install development dependencies:**
   ```bash
   pip install -U "langgraph-cli[inmem]"
   ```

2. **Test email ingestion:**
   ```bash
   python scripts/run_ingest.py --minutes-since 60 --rerun 0 --early 1
   ```

3. **Verify triage logic works with your emails**

### 5. AWS Integration Enhancements (Priority: MEDIUM)
Since you're already using AWS:

- Consider using AWS Lambda for the cron job instead of LangGraph Cloud
- Use AWS SES for sending emails (better deliverability)
- Store conversation history in DynamoDB
- Use AWS Bedrock for additional AI models

### 6. Security & Monitoring (Priority: MEDIUM)
- Set up CloudWatch monitoring for email processing
- Add error notifications via SNS
- Implement rate limiting for API calls
- Add logging for all email actions

## Recommended Implementation Order

1. **Week 1: Core Setup**
   - [ ] Update credential system for AWS
   - [ ] Create config.yaml with your preferences
   - [ ] Test local email ingestion
   - [ ] Verify triage logic with sample emails

2. **Week 2: Production Deployment**
   - [ ] Choose deployment strategy (LangGraph Cloud vs AWS Lambda)
   - [ ] Set up monitoring and logging
   - [ ] Deploy first instance (patrick@highline.work)
   - [ ] Test with low-risk emails first

3. **Week 3: Multi-Account & Optimization**
   - [ ] Deploy second instance if using Option B
   - [ ] Or implement multi-account support if using Option A
   - [ ] Fine-tune triage rules based on real usage
   - [ ] Add custom email templates

4. **Week 4: Advanced Features**
   - [ ] Integrate calendar management
   - [ ] Add custom workflows for specific email types
   - [ ] Implement learning from feedback
   - [ ] Set up backup and recovery procedures

## Important Considerations

1. **Email Volume**: With 285k+ emails in one account, consider:
   - Implementing pagination for initial sync
   - Setting reasonable lookback windows
   - Caching processed email IDs

2. **API Limits**: Monitor Gmail API quotas:
   - 250 quota units per user per second
   - 1 billion quota units per day

3. **Testing Strategy**:
   - Start with a test Gmail account
   - Use email filters to process only specific labels initially
   - Gradually expand scope as confidence grows

4. **Compliance**:
   - Ensure GDPR/privacy compliance if handling others' emails
   - Implement audit logging for all actions
   - Consider data retention policies

## Quick Start Commands

```bash
# Set up environment
export USE_AWS_SECRETS=true
export AWS_REGION=us-west-2

# Test Gmail connection
poetry run python scripts/test_both_gmail_accounts.py

# Run local development server
langgraph dev

# Test email ingestion (last 2 hours)
python scripts/run_ingest.py --minutes-since 120 --rerun 0 --early 1

# Monitor logs
tail -f logs/eaia.log
```

## Next Immediate Action
Start by creating your `config.yaml` file and testing local email ingestion with a small time window to ensure everything works correctly.