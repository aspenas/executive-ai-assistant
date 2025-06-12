"""Core agent responsible for drafting email."""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.store.base import BaseStore

from eaia.schemas import (
    State,
    NewEmailDraft,
    ResponseEmailDraft,
    Question,
    MeetingAssistant,
    SendCalendarInvite,
    Ignore,
    email_template,
)
from eaia.main.config import get_config
from eaia.main.audit_logger import audit_logger
from eaia.main.error_handler import llm_retry, error_handler

logger = logging.getLogger(__name__)

EMAIL_WRITING_INSTRUCTIONS = """You are {full_name}'s executive assistant. You are a top-notch executive assistant who cares about {name} performing as well as possible.

{background}

{name} gets lots of emails. This has been determined to be an email that is worth {name} responding to.

Your job is to help {name} respond. You can do this in a few ways.

# Using the `Question` tool

First, get all required information to respond. You can use the Question tool to ask {name} for information if you do not know it.

When drafting emails (either to response on thread or , if you do not have all the information needed to respond in the most appropriate way, call the `Question` tool until you have that information. Do not put placeholders for names or emails or information - get that directly from {name}!
You can get this information by calling `Question`. Again - do not, under any circumstances, draft an email with placeholders or you will get fired.

If people ask {name} if he can attend some event or meet with them, do not agree to do so unless he has explicitly okayed it!

Remember, if you don't have enough information to respond, you can ask {name} for more information. Use the `Question` tool for this.
Never just make things up! So if you do not know something, or don't know what {name} would prefer, don't hesitate to ask him.
Never use the Question tool to ask {name} when they are free - instead, just ask the MeetingAssistant

# Using the `ResponseEmailDraft` tool

Next, if you have enough information to respond, you can draft an email for {name}. Use the `ResponseEmailDraft` tool for this.

ALWAYS draft emails as if they are coming from {name}. Never draft them as "{name}'s assistant" or someone else.

When adding new recipients - only do that if {name} explicitly asks for it and you know their emails. If you don't know the right emails to add in, then ask {name}. You do NOT need to add in people who are already on the email! Do NOT make up emails.

{response_preferences}

# Using the `SendCalendarInvite` tool

Sometimes you will want to schedule a calendar event. You can do this with the `SendCalendarInvite` tool.
If you are sure that {name} would want to schedule a meeting, and you know that {name}'s calendar is free, you can schedule a meeting by calling the `SendCalendarInvite` tool. {name} trusts you to pick good times for meetings. You shouldn't ask {name} for what meeting times are preferred, but you should make sure he wants to meet. 

{schedule_preferences}

# Using the `NewEmailDraft` tool

Sometimes you will need to start a new email thread. If you have all the necessary information for this, use the `NewEmailDraft` tool for this.

If {name} asks someone if it's okay to introduce them, and they respond yes, you should draft a new email with that introduction.

# Using the `MeetingAssistant` tool

If the email is from a legitimate person and is working to schedule a meeting, call the MeetingAssistant to get a response from a specialist!
You should not ask {name} for meeting times (unless the Meeting Assistant is unable to find any).
If they ask for times from {name}, first ask the MeetingAssistant by calling the `MeetingAssistant` tool.
Note that you should only call this if working to schedule a meeting - if a meeting has already been scheduled, and they are referencing it, no need to call this.

# Background information: information you may find helpful when responding to emails or deciding what to do.

{random_preferences}"""
draft_prompt = """{instructions}

Remember to call a tool correctly! Use the specified names exactly - not add `functions::` to the start. Pass all required arguments.

Here is the email thread. Note that this is the full email thread. Pay special attention to the most recent email.

{email}"""


@llm_retry
async def draft_response(state: State, config: RunnableConfig, store: BaseStore):
    """Enhanced email drafting with error handling and audit logging."""
    email_id = state["email"].get("id", "unknown")
    
    try:
        logger.info(f"Starting draft response for email {email_id}")
        
        model = config["configurable"].get("model", "gpt-4o")
        llm = ChatOpenAI(
            model=model,
            temperature=0,
            parallel_tool_calls=False,
            tool_choice="required",
        )
        tools = [
            NewEmailDraft,
            ResponseEmailDraft,
            Question,
            MeetingAssistant,
            SendCalendarInvite,
        ]
        messages = state.get("messages") or []
        if len(messages) > 0:
            tools.append(Ignore)
        
        prompt_config = get_config(config)
        namespace = (config["configurable"].get("assistant_id", "default"),)
        
        preferences = await _load_preferences_safely(store, namespace, prompt_config)
        
        priority_info = await store.aget(namespace, f"email_priority_{email_id}")
        priority_context = ""
        if priority_info and "value" in priority_info.__dict__:
            priority_data = priority_info.value
            priority_context = f"\n\nPRIORITY CONTEXT: This email was scored {priority_data.get('priority_score', 0)}/100 ({priority_data.get('priority_category', 'unknown')} priority). Consider this when crafting your response."
        
        _prompt = EMAIL_WRITING_INSTRUCTIONS.format(
            schedule_preferences=preferences["schedule_preferences"],
            random_preferences=preferences["random_preferences"],
            response_preferences=preferences["response_preferences"],
            name=prompt_config["name"],
            full_name=prompt_config["full_name"],
            background=prompt_config["background"],
        ) + priority_context
        
        input_message = draft_prompt.format(
            instructions=_prompt,
            email=email_template.format(
                email_thread=state["email"]["page_content"],
                author=state["email"]["from_email"],
                subject=state["email"]["subject"],
                to=state["email"].get("to_email", ""),
            ),
        )

        model = llm.bind_tools(tools)
        messages = [{"role": "user", "content": input_message}] + messages
        
        response = await _invoke_with_retry(model, messages, email_id)
        
        if response and hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            draft_type = tool_call.get("name", "unknown")
            audit_logger.log_email_drafted(email_id, draft_type, 1)
            logger.info(f"Successfully drafted {draft_type} for email {email_id}")
        
        return {"draft": response, "messages": [response]}
        
    except Exception as e:
        logger.error(f"Error in draft_response for email {email_id}: {str(e)}", exc_info=True)
        audit_logger.log_error(email_id, "draft_error", str(e))
        
        fallback_response = await error_handler.handle_llm_error(e, {"function": "draft", "email_id": email_id})
        return {"draft": fallback_response, "messages": []}


async def _load_preferences_safely(store: BaseStore, namespace: tuple, prompt_config: Dict[str, Any]) -> Dict[str, str]:
    """Safely load user preferences with fallbacks."""
    preferences = {}
    
    preference_keys = {
        "schedule_preferences": "schedule_preferences",
        "random_preferences": "background_preferences", 
        "response_preferences": "response_preferences"
    }
    
    for key, config_key in preference_keys.items():
        try:
            result = await store.aget(namespace, key)
            if result and "data" in result.value:
                preferences[key] = result.value["data"]
            else:
                default_value = prompt_config.get(config_key, "")
                await store.aput(namespace, key, {"data": default_value})
                preferences[key] = default_value
        except Exception as e:
            logger.warning(f"Error loading preference {key}: {str(e)}")
            preferences[key] = prompt_config.get(config_key, "")
    
    return preferences


async def _invoke_with_retry(model, messages: list, email_id: str, max_attempts: int = 5):
    """Invoke model with enhanced retry logic."""
    for attempt in range(max_attempts):
        try:
            response = await model.ainvoke(messages)
            
            if not hasattr(response, 'tool_calls') or len(response.tool_calls) != 1:
                if attempt < max_attempts - 1:
                    logger.warning(f"Invalid tool call response for email {email_id}, attempt {attempt + 1}")
                    messages.append({"role": "user", "content": "Please call exactly one valid tool."})
                    continue
                else:
                    logger.error(f"Failed to get valid tool call after {max_attempts} attempts for email {email_id}")
                    audit_logger.log_error(email_id, "invalid_tool_call", f"No valid tool call after {max_attempts} attempts")
            
            return response
            
        except Exception as e:
            if attempt < max_attempts - 1:
                logger.warning(f"Model invocation failed for email {email_id}, attempt {attempt + 1}: {str(e)}")
                continue
            else:
                raise e
    
    return None
