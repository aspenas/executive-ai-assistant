# How to Send Messages to Your Executive AI Assistant

## Step 1: Open LangGraph Studio
Click this link: https://smith.langchain.com/studio/thread?baseUrl=https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app

## Step 2: Find the Message Box
Look for the chat interface at the bottom of the screen. It will have:
- A text input box where you type your message
- A "Send" button (or press Enter)

## Step 3: Type Your Message
In the message box, type any of these examples:
- "What emails do I have from today?"
- "Help me find a meeting time with John"
- "Summarize my unread emails"

## Step 4: Send and Wait
- Click Send or press Enter
- The assistant will process your request (may take 5-30 seconds)
- You'll see the response appear in the chat

## Visual Guide:
```
┌─────────────────────────────────────────┐
│         LangGraph Studio                │
│                                         │
│  [Previous messages appear here]        │
│                                         │
│  Assistant: How can I help you today?   │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Type your message here...           │ │ ← Type here!
│ └─────────────────────────────────────┘ │
│                            [Send]       │ ← Click to send
└─────────────────────────────────────────┘
```

## Alternative: Using the API
If you prefer command line, you can also send messages via curl:

```bash
# First, create a thread
curl -X POST https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app/threads \
  -H "Content-Type: application/json"

# Then send a message (replace <thread_id> with the ID from above)
curl -X POST https://eaia-18a3cdfcc5c1502794a566a108ec4a60.us.langgraph.app/threads/<thread_id>/runs \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "main",
    "input": {
      "messages": [{
        "role": "user",
        "content": "What emails do I have today?"
      }]
    }
  }'
```

But the Studio interface is much easier to use!