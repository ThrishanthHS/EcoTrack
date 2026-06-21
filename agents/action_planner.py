# ── Agent 4: Action Planner ───────────────────────────────────────────────
# Takes everything from Agents 1, 2, and 3 and generates a personalised
# 7-day carbon reduction roadmap the user can follow immediately.

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

def run_action_planner_agent(search_output: dict) -> dict:
    """
    Takes the full pipeline output and generates a personalised
    7-day carbon reduction roadmap using Groq LLM.

    Args:
        search_output: dict from Agent 3 (web_search)

    Returns:
        action_plan: dict with 7-day roadmap and summary
    """

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
    )

    profile = search_output["profile"]
    drivers = search_output["reasoning"]["drivers"]
    search_results = search_output["search_results"]

    # ── Build context for the planner ────────────────────────────────────
    drivers_context = ""
    for i, (driver, search) in enumerate(zip(drivers, search_results), 1):
        drivers_context += f"""
Driver {i}: {driver['name']}
  Why it matters : {driver['why']}
  Recommended action : {driver['action']}
  Research insight   : {search['summary']}
"""

    system_prompt = """You are a personal carbon reduction coach specialising in 
Indian urban lifestyles. Your job is to create a practical, realistic 7-day action 
plan that helps someone genuinely reduce their carbon footprint. 

Rules:
- Each day should have ONE clear, specific task — not vague advice
- Tasks must be realistic for a working person in an Indian city
- Alternate between different emission categories across the week
- Use simple, friendly language — like texting a friend, not writing a report
- Day 1 should be the easiest task to build momentum
- Day 7 should be a reflection and planning task"""

    user_prompt = f"""Create a personalised 7-day carbon reduction plan for this user:

Their Profile:
- Monthly carbon output : {profile['predicted_kg']} kg CO₂
- Green score           : {profile['green_score']} / 100
- vs India average      : {abs(profile['vs_india_avg_pct'])}% {profile['vs_india_avg_status']}
- Transport             : {profile['transport']} ({profile['monthly_distance_km']} km/month)
- Diet                  : {profile['diet']}
- Screen time           : {profile['screen_hours_day']} hours/day
- High traffic city     : {profile['high_traffic_city']}

Their Top Emission Drivers and Research:
{drivers_context}

Generate a 7-day plan using EXACTLY this format:

DAY 1: [title]
TASK: [specific action]
IMPACT: [one sentence on why this helps]

DAY 2: [title]
TASK: [specific action]
IMPACT: [one sentence on why this helps]

DAY 3: [title]
TASK: [specific action]
IMPACT: [one sentence on why this helps]

DAY 4: [title]
TASK: [specific action]
IMPACT: [one sentence on why this helps]

DAY 5: [title]
TASK: [specific action]
IMPACT: [one sentence on why this helps]

DAY 6: [title]
TASK: [specific action]
IMPACT: [one sentence on why this helps]

DAY 7: [title]
TASK: [specific action]
IMPACT: [one sentence on why this helps]

SUMMARY: [2 sentence motivational summary of the week ahead]"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    raw_text = response.content.strip()

    # ── Parse the 7-day plan ─────────────────────────────────────────────
    days    = []
    summary = ""
    blocks  = raw_text.split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        day   = {}
        for line in lines:
            if line.startswith("DAY"):
                parts = line.split(":", 1)
                day["day"]   = parts[0].strip()
                day["title"] = parts[1].strip() if len(parts) > 1 else ""
            elif line.startswith("TASK"):
                day["task"] = line.split(":", 1)[-1].strip()
            elif line.startswith("IMPACT"):
                day["impact"] = line.split(":", 1)[-1].strip()
            elif line.startswith("SUMMARY"):
                summary = line.split(":", 1)[-1].strip()
        if "day" in day and "task" in day:
            days.append(day)

    action_plan = {
        "days"    : days,
        "summary" : summary,
        "raw_text": raw_text,
        "profile" : profile,
    }

    return action_plan


# ── Quick test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from ingestion   import run_ingestion_agent
    from reasoner    import run_reasoner_agent
    from web_search  import run_web_search_agent

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

    profile          = run_ingestion_agent(sample)
    reasoning_output = run_reasoner_agent(profile)
    search_output    = run_web_search_agent(reasoning_output)
    action_plan      = run_action_planner_agent(search_output)

    print("\n── 7-Day Carbon Reduction Roadmap ─────────────")
    for day in action_plan["days"]:
        print(f"\n{day['day']}: {day.get('title', '')}")
        print(f"  Task   : {day['task']}")
        print(f"  Impact : {day.get('impact', '')}")

    print(f"\nSummary: {action_plan['summary']}")