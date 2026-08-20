"""Nirnaya LangGraph Orchestrator.

Defines the state graph for the fraud analysis pipeline:
Understand -> Gather Evidence -> Score -> Explain
"""

import logging
from typing import TypedDict, Dict, Any, List

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from app.services.llm_router import get_llm
from app.services.agent_tools import run_evidence_gathering, calculate_final_risk

logger = logging.getLogger(__name__)


# 1. Define the State
class AgentState(TypedDict):
    text: str
    rule_signals: Dict[str, bool]
    ml_score: float
    semantic_matches: List[Dict]
    rag_context: str
    final_risk_score: float
    policy_action: str
    explanation: str


# 2. Define the Nodes
def gather_evidence_node(state: AgentState) -> AgentState:
    """Executes deterministic rules, ML models, and RAG retrieval."""
    logger.info("Executing Gather Evidence Node")
    text = state["text"]
    
    evidence = run_evidence_gathering(text)
    return evidence  # langgraph merges this dict into the state


def score_risk_node(state: AgentState) -> AgentState:
    """Fuses evidence into a final risk score and policy action."""
    logger.info("Executing Score Risk Node")
    
    risk_data = calculate_final_risk(
        state.get("rule_signals", {}),
        state.get("ml_score", 0.0),
        state.get("semantic_matches", [])
    )
    return risk_data


def generate_explanation_node(state: AgentState) -> AgentState:
    """Uses the LLM to explain the final verdict based ONly on the evidence."""
    logger.info("Executing Explanation Node")
    
    llm = get_llm(temperature=0.2)
    
    # Format the evidence for the LLM
    ml_score = state.get("ml_score", 0.0)
    risk_score = state.get("final_risk_score", 0.0)
    action = state.get("policy_action", "UNKNOWN")
    signals = [k for k, v in state.get("rule_signals", {}).items() if v]
    rag = state.get("rag_context", "None")
    
    system_prompt = f"""You are Nirnaya, an AI financial safety assistant. 
Your job is to explain why a message was flagged as risky or safe, based strictly on the provided evidence.

EVIDENCE:
- Final Risk Score: {risk_score:.2f} (0=Safe, 1=High Risk)
- Policy Action: {action}
- AI Classifier Score: {ml_score:.2f}
- Detected Red Flags: {', '.join(signals) if signals else 'None'}

REFERENCE KNOWLEDGE:
{rag}

INSTRUCTIONS:
1. Write a 2-3 sentence explanation directed at the user.
2. Be empathetic but firm if the risk is high.
3. If reference knowledge is provided (e.g. RBI guidelines), cite it briefly to ground your explanation.
4. Do NOT invent new evidence.
5. If the risk is low, reassure the user.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Message to analyze: '{state['text']}'")
    ]
    
    try:
        response = llm.invoke(messages)
        explanation = response.content.strip()
    except Exception as e:
        logger.error(f"Failed to generate explanation: {e}")
        explanation = "We detected suspicious patterns in this message. Please exercise caution."
        
    return {"explanation": explanation}


# 3. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("gather_evidence", gather_evidence_node)
workflow.add_node("score_risk", score_risk_node)
workflow.add_node("explain", generate_explanation_node)

workflow.add_edge(START, "gather_evidence")
workflow.add_edge("gather_evidence", "score_risk")
workflow.add_edge("score_risk", "explain")
workflow.add_edge("explain", END)

# Compile it
fraud_agent = workflow.compile()

def analyze_fraud_with_agent(text: str) -> Dict[str, Any]:
    """Entry point for the API to invoke the LangGraph agent."""
    initial_state = {
        "text": text,
        "rule_signals": {},
        "ml_score": 0.0,
        "semantic_matches": [],
        "rag_context": "",
        "final_risk_score": 0.0,
        "policy_action": "ALLOW",
        "explanation": ""
    }
    
    result = fraud_agent.invoke(initial_state)
    
    # Return a structured dict suitable for the Pydantic API response
    return {
        "risk_score": result["final_risk_score"],
        "action": result["policy_action"],
        "explanation": result["explanation"],
        "signals": [{"type": k, "confidence": 1.0, "evidence": k} for k, v in result["rule_signals"].items() if v],
        "raw_scores": {
            "ml_score": result.get("ml_score"),
            "semantic_score": result.get("semantic_matches")[0]["similarity"] if result.get("semantic_matches") else 0.0
        }
    }
