# Executive AI Assistant Usage Guide

## Overview
The Executive AI Assistant is a powerful tool that helps manage your email, schedule meetings, and provide intelligent assistance for various tasks.

## Access Methods

### 1. LangGraph Studio (Recommended)
Visit: https://smith.langchain.com/studio/thread?baseUrl=https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app

### 2. API Access
Base URL: `https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app`

## Features & Example Messages

### 📧 Email Management
- **Check emails**: "What emails do I have from today?"
- **Search emails**: "Find all emails from John about the project"
- **Draft replies**: "Draft a reply to the latest email from Sarah"
- **Summarize threads**: "Summarize my conversation with the marketing team"

### 📅 Calendar & Scheduling
- **Find meeting times**: "Find a 30-minute slot this week for a meeting with Alex"
- **Check availability**: "What's my schedule for tomorrow?"
- **Schedule meetings**: "Schedule a meeting with the team for Friday at 2pm"

### 🤖 General Assistance
- **Research**: "Research the latest trends in AI development"
- **Analysis**: "Analyze the key points from my last board meeting"
- **Writing**: "Help me write an executive summary for the Q3 report"

## Quick Start Examples

### First Message
Try these to test the assistant:
```
"Hello, can you check my recent emails?"
"What's on my calendar today?"
"Help me draft an email to my team about tomorrow's meeting"
```

### Email Triage
```
"Check my unread emails and categorize them by priority"
"Which emails need immediate attention?"
"Summarize emails from my direct reports"
```

### Meeting Coordination
```
"Find a time for a 1-hour meeting with John and Sarah next week"
"What meetings do I have this afternoon?"
"Reschedule my 3pm meeting to tomorrow"
```

## Advanced Features

### Multi-Step Tasks
The assistant can handle complex, multi-step requests:
```
"Check my emails from the product team, summarize the main issues, 
and draft responses for each one"
```

### Context-Aware Responses
The assistant remembers context within a conversation:
```
You: "What emails do I have from John?"
Assistant: [Shows emails]
You: "Draft a reply to the second one"
```

### Reflection & Analysis
For complex tasks, the assistant can use reflection graphs:
```
"Analyze my meeting patterns over the last month and suggest 
improvements to my schedule"
```

## API Usage (for developers)

### Basic Request
```bash
curl -X POST https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app/threads/<thread_id>/runs \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d '{
    "assistant_id": "main",
    "input": {
      "messages": [{
        "role": "user",
        "content": "Check my recent emails"
      }]
    }
  }'
```

### Available Graphs
- `main`: Primary assistant for general tasks
- `cron`: Scheduled tasks and automation
- `general_reflection_graph`: For analytical tasks
- `multi_reflection_graph`: For complex multi-aspect analysis

## Tips for Best Results

1. **Be Specific**: "Find emails from John about the Q3 budget" works better than "Find John's emails"

2. **Use Natural Language**: The assistant understands conversational requests

3. **Leverage Context**: You can refer to previous messages in the conversation

4. **Request Summaries**: For long email threads or multiple items, ask for summaries

5. **Iterate**: If the first response isn't quite right, provide clarification

## Troubleshooting

### If the assistant isn't responding:
1. Check deployment status: Run `python3 check_deployment_quick.py`
2. Verify you're using the correct URL
3. Ensure your API keys are properly configured

### If email access isn't working:
1. The Gmail OAuth may need reauthorization
2. Check that GMAIL_OAUTH_CREDENTIALS is properly set

### If responses seem slow:
1. Complex requests may take 10-30 seconds
2. Email searches with many results take longer
3. The reflection graphs are slower but more thorough

## Privacy & Security
- All data is processed securely
- Email access is via OAuth (no password storage)
- API keys are encrypted in AWS Secrets Manager
- No persistent storage of email content

## Getting Help
- Check deployment logs for technical issues
- Review the README.md for setup information
- Contact support for API key or access issues