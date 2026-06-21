# ── Agent 2: LLM Reasoner ─────────────────────────────────────────────────
# Takes the structured carbon profile from Agent 1 and uses Groq LLM
# to identify the top emission leverage points with clear explanations.

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

def run_reasoner_agent(profile: dict) -> dict:
    """
    Takes the structured carbon profile and returns LLM-generated
    reasoning about the top emission drivers and what to do about them.

    Args:
        profile: structured dict from Agent 1 (ingestion)

    Returns:
        reasoning_output: dict with identified drivers and explanations
    """

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
    )

    system_prompt = """You are an expert carbon footprint analyst specialising in 
Indian urban lifestyles. Your job is to look at a person's carbon emission profile 
and identify their top 3 emission drivers — the specific habits causing the most 
carbon output — and explain each one in simple, direct language that anyone can 
understand. Be honest, practical, and avoid jargon. Keep each explanation under 
3 sentences. Do not use bullet points in your response — use plain numbered format."""

    user_prompt = f"""Here is the carbon profile of an Indian user:

Monthly Carbon Output : {profile['predicted_kg']} kg CO₂
Green Score           : {profile['green_score']} / 100
vs India Average      : {abs(profile['vs_india_avg_pct'])}% {profile['vs_india_avg_status']} national average

Emission Breakdown:
  - Commute & Travel  : {profile['emission_breakdown']['commute']} kg
  - Food & Diet       : {profile['emission_breakdown']['diet']} kg
  - Screens & Devices : {profile['emission_breakdown']['screens']} kg
  - Internet Usage    : {profile['emission_breakdown']['internet']} kg
  - Groceries         : {profile['emission_breakdown']['groceries']} kg

User Habits:
  - Transport mode    : {profile['transport']}
  - Monthly distance  : {profile['monthly_distance_km']} km
  - Diet type         : {profile['diet']}
  - Screen time       : {profile['screen_hours_day']} hours/day
  - High traffic city : {profile['high_traffic_city']}
  - Energy efficient  : {profile['energy_efficient']}

Top emission category: {profile['top_emission_category']}
Yearly total          : {profile['yearly_tonnes']} tonnes CO₂

Identify the top 3 emission drivers for this person. For each one:
1. Name the driver clearly
2. Explain why it is causing high emissions in simple words
3. Give one specific thing this person can do to reduce it

Format your response exactly like this:
DRIVER 1: [name]
WHY: [explanation]
ACTION: [specific action]

DRIVER 2: [name]
WHY: [explanation]
ACTION: [specific action]

DRIVER 3: [name]
WHY: [explanation]
ACTION: [specific action]"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    raw_text = response.content

    # ── Parse the structured response ────────────────────────────────────
    drivers = []
    blocks  = raw_text.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        driver = {}
        for line in lines:
            if line.startswith("DRIVER"):
                driver["name"] = line.split(":", 1)[-1].strip()
            elif line.startswith("WHY"):
                driver["why"] = line.split(":", 1)[-1].strip()
            elif line.startswith("ACTION"):
                driver["action"] = line.split(":", 1)[-1].strip()
        if len(driver) == 3:
            drivers.append(driver)

    reasoning_output = {
        "drivers"  : drivers,
        "raw_text" : raw_text,
        "profile"  : profile,
    }

    return reasoning_output


# ── Quick test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from ingestion import run_ingestion_agent

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

    profile = run_ingestion_agent(sample)
    result  = run_reasoner_agent(profile)

    print("\n── LLM Reasoning Output ───────────────────────")
    for i, d in enumerate(result["drivers"], 1):
        print(f"\nDriver {i}: {d['name']}")
        print(f"  Why   : {d['why']}")
        print(f"  Action: {d['action']}")