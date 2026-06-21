# ── Agent 3: Web Search Agent ─────────────────────────────────────────────
# Takes the emission drivers from Agent 2 and searches the web live
# for real, practical green alternatives relevant to the user's habits.

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from ddgs import DDGS
from reasoner import run_reasoner_agent

load_dotenv()

def search_green_alternatives(query: str, max_results: int = 3) -> list:
    """
    Searches DuckDuckGo for green alternatives and returns
    a clean list of results.

    Args:
        query     : search query string
        max_results: number of results to fetch

    Returns:
        list of dicts with title, url, snippet
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title"  : r.get("title", ""),
                    "url"    : r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
    except Exception as e:
        results.append({
            "title"  : "Search unavailable",
            "url"    : "",
            "snippet": str(e),
        })
    return results


def run_web_search_agent(reasoning_output: dict) -> dict:
    """
    Takes reasoning output from Agent 2, builds targeted search queries
    for each emission driver, fetches live results, and uses Groq to
    summarise the findings into actionable green alternatives.

    Args:
        reasoning_output: dict from Agent 2 (reasoner)

    Returns:
        search_output: dict with live green alternatives per driver
    """

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.5,
    )

    profile = reasoning_output["profile"]
    drivers = reasoning_output["drivers"]

    # ── Build search queries per driver ──────────────────────────────────
    search_results = []

    for driver in drivers:
        driver_name = driver["name"]

        # Build a targeted India-specific query
        query = f"how to reduce {driver_name} carbon emissions India 2024 practical tips"

        raw_results = search_green_alternatives(query, max_results=3)

        # Use Groq to summarise the search results into one clean insight
        snippets = "\n".join([
            f"- {r['title']}: {r['snippet']}" for r in raw_results if r['snippet']
        ])

        if snippets:
            summary_prompt = f"""Based on these search results about reducing {driver_name} 
carbon emissions in India:

{snippets}

Write ONE clear, practical tip in 2 sentences maximum that an Indian user can 
act on immediately. Be specific. No jargon. No bullet points."""

            summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
            summary = summary_response.content.strip()
        else:
            summary = driver["action"]

        search_results.append({
            "driver"     : driver_name,
            "query"      : query,
            "raw_results": raw_results,
            "summary"    : summary,
        })

    search_output = {
        "search_results": search_results,
        "reasoning"     : reasoning_output,
        "profile"       : profile,
    }

    return search_output


# ── Quick test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from ingestion import run_ingestion_agent
    from reasoner   import run_reasoner_agent

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

    print("\n── Web Search Results ─────────────────────────")
    for r in search_output["search_results"]:
        print(f"\nDriver  : {r['driver']}")
        print(f"Query   : {r['query']}")
        print(f"Summary : {r['summary']}")
        print(f"Sources :")
        for s in r["raw_results"]:
            print(f"  · {s['title']}")
            print(f"    {s['url']}")