import joblib
import pandas as pd
import copy

# ==============================
# STEP 1: Load Trained Model
# ==============================
model = joblib.load("Ecotrack_rf_model.pkl")
print(" Model loaded successfully")

# ==============================
# STEP 2: Sample User Input
# ==============================
user_input = {
    "body_type": "overweight",
    "sex": "male",
    "diet": "omnivore",
    "how_often_shower": "daily",
    "heating_energy_source": "coal",
    "transport": "private",
    "vehicle_type": "petrol",
    "social_activity": "often",
    "monthly_grocery_bill": 200,
    "frequency_of_traveling_by_air": "rarely",
    "vehicle_monthly_distance_km": 1200,
    "waste_bag_size": "medium",
    "waste_bag_weekly_count": 3,
    "how_long_tv_pc_daily_hour": 6,
    "how_many_new_clothes_monthly": 3,
    "how_long_internet_daily_hour": 6,
    "energy_efficiency": "No",

    # Recycling
    "recycle_metal": 1,
    "recycle_plastic": 0,
    "recycle_glass": 0,
    "recycle_paper": 0,

    # Cooking
    "cook_stove": 1,
    "cook_oven": 1,
    "cook_microwave": 0,
    "cook_grill": 0,
    "cook_airfryer": 0
}

user_df = pd.DataFrame([user_input])

# ==============================
# STEP 3: Predict Carbon Emission
# ==============================
predicted_emission = model.predict(user_df)[0]
print(f"\n Predicted Monthly Carbon Emission: {predicted_emission:.2f} kg CO₂")

# ==============================
# STEP 4: Ranked Optimization Logic
# ==============================
suggestions = []

def add_suggestion(title, new_prediction):
    savings = predicted_emission - new_prediction

    # Ignore negative or negligible improvements
    if savings <= 1:
        return

    percent = (savings / predicted_emission) * 100

    suggestions.append({
        "title": title,
        "savings": savings,
        "percent": percent
    })

# --- Transport Optimization ---
if user_input["transport"] == "private":
    modified = copy.deepcopy(user_input)
    modified["vehicle_monthly_distance_km"] *= 0.7
    modified["transport"] = "public"
    modified["vehicle_type"] = "none"

    new_pred = model.predict(pd.DataFrame([modified]))[0]
    add_suggestion(
        " Use public transport 2–3 days/week",
        new_pred
    )

# --- Energy Efficiency ---
if user_input["energy_efficiency"] == "No":
    modified = copy.deepcopy(user_input)
    modified["energy_efficiency"] = "Yes"

    new_pred = model.predict(pd.DataFrame([modified]))[0]
    add_suggestion(
        " Improve home energy efficiency",
        new_pred
    )

# --- Screen Time ---
if user_input["how_long_tv_pc_daily_hour"] > 5:
    modified = copy.deepcopy(user_input)
    modified["how_long_tv_pc_daily_hour"] -= 2

    new_pred = model.predict(pd.DataFrame([modified]))[0]
    add_suggestion(
        " Reduce screen time by 2 hours/day",
        new_pred
    )

# --- Diet Optimization ---
if user_input["diet"] == "omnivore":
    modified = copy.deepcopy(user_input)
    modified["diet"] = "vegetarian"

    new_pred = model.predict(pd.DataFrame([modified]))[0]
    add_suggestion(
        " Go vegetarian 3–4 days/week",
        new_pred
    )

# ==============================
# STEP 5: Rank & Display
# ==============================
suggestions = sorted(suggestions, key=lambda x: x["savings"], reverse=True)

print("\n Ranked Optimization Suggestions (by impact):")

if not suggestions:
    print("No significant optimizations found.")
else:
    for i, s in enumerate(suggestions, start=1):
        print(
            f"{i}. {s['title']} → "
            f"Save ~{s['savings']:.1f} kg CO₂/month "
            f"({s['percent']:.2f}% reduction)"
        )
