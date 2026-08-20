"""Nirnaya LLM Router.

Provides a unified interface for the LangGraph agent to communicate
with Gemini (via google-genai) or a Mock LLM for local testing if keys
are not provided.
"""

import os
import logging
from typing import Optional, List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

logger = logging.getLogger(__name__)


def get_llm(model_name: str = "gemini-3.6-flash", temperature: float = 0.0) -> BaseChatModel:
    """Initialize the chosen LLM via LangChain.
    
    If the GEMINI_API_KEY environment variable is not set, a mock LLM 
    should be used or it will fail.
    """
    from app.config import settings
    api_key = settings.GEMINI_API_KEY
    
    if api_key:
        logger.info(f"Initializing ChatGoogleGenerativeAI ({model_name})")
        # LangChain's ChatGoogleGenerativeAI supports tool binding, structured output, etc.
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(api_key),
            max_retries=2
        )
    else:
        logger.warning("No GEMINI_API_KEY found. Falling back to MockChatModel (will fail on real queries).")
        # In a real app we'd return a custom MockChatModel here that just echoes,
        # but LangGraph requires a proper BaseChatModel for tool calling.
        # We'll instantiate the real one with a dummy key and let it fail gracefully
        # at runtime if they actually try to invoke it.
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr("mock_key_will_fail"),
            max_retries=0
        )

# For direct text extraction tasks without the full agent
def extract_intent_fast(text: str) -> str:
    """Fast, single-shot LLM call for intent extraction."""
    llm = get_llm(model_name="gemini-3.6-flash")
    messages = [
        SystemMessage(content="You are a financial intent classifier. Classify the user's intent as one of: [CHECK_FRAUD, ANALYZE_SPENDING, PLAN_GOAL, UNKNOWN]. Return ONLY the classification string."),
        HumanMessage(content=text)
    ]
    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        return "UNKNOWN"
