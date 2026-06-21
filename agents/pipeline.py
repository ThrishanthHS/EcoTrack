# ── LangGraph Pipeline ────────────────────────────────────────────────────
# Wires all 4 agents into a single LangGraph pipeline.
# Flow: Ingestion → Reasoner → Web Search → Action Planner

import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from ingestion     import run_ingestion_agent
from reasoner      import run_reasoner_agent
from web_search    import run_web_search_agent
from action_planner import run_action_planner_agent

load_dotenv()

# ── Pipeline State ────────────────────────────────────────────────────────
# This is the shared state object that gets passed between all agents.
# Each agent reads from it and writes its output back into it.

class EcoTrackState(TypedDict):
    session_data     : dict   # raw input from Streamlit session
    profile          : dict   # Agent 1 output — structured carbon profile
    reasoning_output : dict   # Agent 2 output — LLM emission reasoning
    search_output    : dict   # Agent 3 output — live web search results
    action_plan      : dict   # Agent 4 output — 7-day roadmap
    error            : str    # captures any error that occurs mid-pipeline


# ── Agent Node Functions ──────────────────────────────────────────────────
# Each function receives the full state, runs its agent, and returns
# only the keys it wants to update in the state.

def node_ingestion(state: EcoTrackState) -> dict:
    print("  [Agent 1] Running Data Ingestion...")
    try:
        profile = run_ingestion_agent(state["session_data"])
        return {"profile": profile, "error": ""}
    except Exception as e:
        return {"error": f"Ingestion failed: {str(e)}"}


def node_reasoner(state: EcoTrackState) -> dict:
    print("  [Agent 2] Running LLM Reasoner...")
    try:
        reasoning_output = run_reasoner_agent(state["profile"])
        return {"reasoning_output": reasoning_output, "error": ""}
    except Exception as e:
        return {"error": f"Reasoner failed: {str(e)}"}


def node_web_search(state: EcoTrackState) -> dict:
    print("  [Agent 3] Running Web Search...")
    try:
        search_output = run_web_search_agent(state["reasoning_output"])
        return {"search_output": search_output, "error": ""}
    except Exception as e:
        return {"error": f"Web search failed: {str(e)}"}


def node_action_planner(state: EcoTrackState) -> dict:
    print("  [Agent 4] Running Action Planner...")
    try:
        action_plan = run_action_planner_agent(state["search_output"])
        return {"action_plan": action_plan, "error": ""}
    except Exception as e:
        return {"error": f"Action planner failed: {str(e)}"}


# ── Error Check ───────────────────────────────────────────────────────────
# After each agent, check if an error occurred.
# If yes, route to END. If no, continue to next agent.

def check_error(state: EcoTrackState) -> str:
    if state.get("error", ""):
        print(f"  [Pipeline] Error detected — stopping: {state['error']}")
        return "end"
    return "continue"


# ── Build the Graph ───────────────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    graph = StateGraph(EcoTrackState)

    # Add all 4 agent nodes
    graph.add_node("ingestion",      node_ingestion)
    graph.add_node("reasoner",       node_reasoner)
    graph.add_node("web_search",     node_web_search)
    graph.add_node("action_planner", node_action_planner)

    # Set entry point
    graph.set_entry_point("ingestion")

    # Connect nodes with error checking between each step
    graph.add_conditional_edges(
        "ingestion",
        check_error,
        {"continue": "reasoner", "end": END}
    )
    graph.add_conditional_edges(
        "reasoner",
        check_error,
        {"continue": "web_search", "end": END}
    )
    graph.add_conditional_edges(
        "web_search",
        check_error,
        {"continue": "action_planner", "end": END}
    )
    graph.add_edge("action_planner", END)

    return graph.compile()


# ── Main entry point ──────────────────────────────────────────────────────

def run_pipeline(session_data: dict) -> dict:
    """
    Main function called by the Streamlit app.
    Takes session data and returns the complete action plan.

    Args:
        session_data: dict of user inputs + prediction results

    Returns:
        final state dict containing action_plan and all intermediate outputs
    """
    pipeline = build_pipeline()

    initial_state = EcoTrackState(
        session_data     = session_data,
        profile          = {},
        reasoning_output = {},
        search_output    = {},
        action_plan      = {},
        error            = "",
    )

    print("\n── EcoTrack Agentic Pipeline Starting ─────────")
    final_state = pipeline.invoke(initial_state)
    print("── Pipeline Complete ───────────────────────────\n")

    return final_state


# ── Quick test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "transport"    : "private",
        "diet"         : "omnivore",
        "distance"     : 1200,
        "screen_time"  : 7,
        "internet_time": 5,
        "grocery"      : 200,
        "energy_eff"   : "No",
        "high_traffic" : "Yes",
        "predicted"    : 1850.0,
        "score"        : 55,
        "transport_em" : 289.8,
        "diet_em"      : 400.0,
        "screen_em"    : 10.5,
        "internet_em"  : 4.5,
        "grocery_em"   : 100.0,
    }

    result = run_pipeline(sample)

    print("── Final Action Plan ───────────────────────────")
    for day in result["action_plan"]["days"]:
        print(f"\n{day['day']}: {day.get('title', '')}")
        print(f"  Task   : {day['task']}")
        print(f"  Impact : {day.get('impact', '')}")

    print(f"\nSummary: {result['action_plan']['summary']}")
    if result["error"]:
        print(f"\nError: {result['error']}")