# ── Agent 1: Data Ingestion ───────────────────────────────────────────────
# Reads the user's carbon profile from session state and structures it
# into a clean dictionary that the downstream agents can reason over.

def run_ingestion_agent(session_data: dict) -> dict:
    """
    Takes raw session state values from the Streamlit app and returns
    a structured carbon profile ready for LLM reasoning.

    Args:
        session_data: dict containing user inputs and prediction results

    Returns:
        structured_profile: clean dict with all relevant carbon data
    """

    transport       = session_data.get("transport", "unknown")
    diet            = session_data.get("diet", "unknown")
    distance        = session_data.get("distance", 0)
    screen_time     = session_data.get("screen_time", 0)
    internet_time   = session_data.get("internet_time", 0)
    grocery         = session_data.get("grocery", 0)
    energy_eff      = session_data.get("energy_eff", "No")
    high_traffic    = session_data.get("high_traffic", "No")
    predicted       = session_data.get("predicted", 0)
    score           = session_data.get("score", 0)
    transport_em    = session_data.get("transport_em", 0)
    diet_em         = session_data.get("diet_em", 0)
    screen_em       = session_data.get("screen_em", 0)
    internet_em     = session_data.get("internet_em", 0)
    grocery_em      = session_data.get("grocery_em", 0)

    INDIA_AVG = 1500
    diff_pct  = round(((predicted - INDIA_AVG) / INDIA_AVG) * 100, 1)
    status    = "above" if diff_pct > 0 else "below"

    # Identify top emission category
    categories = {
        "Commute & Travel" : transport_em,
        "Food & Diet"      : diet_em,
        "Screen & Devices" : screen_em,
        "Internet Usage"   : internet_em,
        "Groceries"        : grocery_em,
    }
    top_category = max(categories, key=categories.get)

    structured_profile = {
        # ── User Inputs ──────────────────────────
        "transport"         : transport,
        "diet"              : diet,
        "monthly_distance_km": distance,
        "screen_hours_day"  : screen_time,
        "internet_hours_day": internet_time,
        "monthly_grocery_inr": grocery,
        "energy_efficient"  : energy_eff,
        "high_traffic_city" : high_traffic,

        # ── Prediction Results ───────────────────
        "predicted_kg"      : round(predicted, 1),
        "green_score"       : score,
        "vs_india_avg_pct"  : diff_pct,
        "vs_india_avg_status": status,

        # ── Emission Breakdown ───────────────────
        "emission_breakdown": {
            "commute"   : round(transport_em, 1),
            "diet"      : round(diet_em, 1),
            "screens"   : round(screen_em, 1),
            "internet"  : round(internet_em, 1),
            "groceries" : round(grocery_em, 1),
        },

        # ── Derived Insights ─────────────────────
        "top_emission_category": top_category,
        "yearly_kg"            : round(predicted * 12, 1),
        "yearly_tonnes"        : round(predicted * 12 / 1000, 2),
    }

    return structured_profile


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

    profile = run_ingestion_agent(sample)

    print("\n── Structured Carbon Profile ──────────────────")
    for k, v in profile.items():
        print(f"  {k}: {v}")