"""Agent responsible for triaging the email, can either ignore it, try to respond, or notify user."""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.messages import RemoveMessage
from langgraph.store.base import BaseStore

from eaia.schemas import (
    State,
    RespondTo,
)
from eaia.main.fewshot import get_few_shot_examples
from eaia.main.config import get_config
from eaia.main.priority_scorer import EmailPriorityScorer

logger = logging.getLogger(__name__)


triage_prompt = """You are {full_name}'s executive assistant. You are a top-notch executive assistant who cares about {name} performing as well as possible.

{background}. 

{name} gets lots of emails. Your job is to categorize the below email to see whether is it worth responding to.

PRIORITY ANALYSIS:
This email has been automatically scored with a priority of {priority_score}/100 ({priority_category}).
Priority breakdown: {priority_breakdown}

Consider this priority assessment when making your decision, but use your judgment as the final arbiter.

Emails that are not worth responding to:
{triage_no}

Emails that are worth responding to:
{triage_email}

There are also other things that {name} should know about, but don't require an email response. For these, you should notify {name} (using the `notify` response). Examples of this include:
{triage_notify}

For emails not worth responding to, respond `no`. For something where {name} should respond over email, respond `email`. If it's important to notify {name}, but no email is required, respond `notify`. \

If unsure, opt to `notify` {name} - you will learn from this in the future.

{fewshotexamples}

Please determine how to handle the below email thread:

From: {author}
To: {to}
Subject: {subject}

{email_thread}"""


async def triage_input(state: State, config: RunnableConfig, store: BaseStore):
    """Enhanced triage function with priority scoring and audit logging."""
    try:
        model = config.get("configurable", {}).get("model") or "gpt-4o"
        llm = ChatOpenAI(model=model, temperature=0)
        examples = await get_few_shot_examples(state["email"], store, config)
        prompt_config = get_config(config)
        
        priority_scorer = EmailPriorityScorer(prompt_config)
        priority_score, priority_breakdown = priority_scorer.score_email(state["email"])
        priority_category = priority_scorer.get_priority_category(priority_score)
        
        email_id = state["email"].get("id", "unknown")
        logger.info(f"Triaging email {email_id} from {state['email'].get('from_email', 'unknown')} "
                   f"with priority {priority_score}/100 ({priority_category})")
        
        namespace = (config["configurable"].get("assistant_id", "default"),)
        await store.aput(namespace, f"email_priority_{email_id}", {
            "priority_score": priority_score,
            "priority_category": priority_category,
            "priority_breakdown": priority_breakdown,
            "timestamp": state["email"].get("timestamp", "")
        })
        
        input_message = triage_prompt.format(
            email_thread=state["email"]["page_content"],
            author=state["email"]["from_email"],
            to=state["email"].get("to_email", ""),
            subject=state["email"]["subject"],
            fewshotexamples=examples,
            name=prompt_config["name"],
            full_name=prompt_config["full_name"],
            background=prompt_config["background"],
            triage_no=prompt_config["triage_no"],
            triage_email=prompt_config["triage_email"],
            triage_notify=prompt_config["triage_notify"],
            priority_score=priority_score,
            priority_category=priority_category,
            priority_breakdown=_format_priority_breakdown(priority_breakdown),
        )
        
        model = llm.with_structured_output(RespondTo).bind(
            tool_choice={"type": "function", "function": {"name": "RespondTo"}}
        )
        response = await model.ainvoke(input_message)
        
        logger.info(f"Triage decision for email {email_id}: {response.response}")
        
        await store.aput(namespace, f"triage_decision_{email_id}", {
            "decision": response.response,
            "priority_score": priority_score,
            "timestamp": state["email"].get("timestamp", "")
        })
        
        if len(state["messages"]) > 0:
            delete_messages = [RemoveMessage(id=m.id) for m in state["messages"]]
            return {"triage": response, "messages": delete_messages}
        else:
            return {"triage": response}
            
    except Exception as e:
        logger.error(f"Error in triage_input: {str(e)}", exc_info=True)
        fallback_response = RespondTo(response="notify")
        return {"triage": fallback_response}


def _format_priority_breakdown(breakdown: Dict[str, int]) -> str:
    """Format priority breakdown for display in prompt."""
    formatted_items = []
    for category, score in breakdown.items():
        if score > 0:
            formatted_items.append(f"{category.replace('_', ' ').title()}: +{score}")
    return ", ".join(formatted_items) if formatted_items else "No specific priority indicators"
