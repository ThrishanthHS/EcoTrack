import streamlit as st
import pandas as pd
import joblib
import copy
import base64
import sqlite3
import datetime
import streamlit.components.v1 as components

# ── Plotly ──────────────────────────────────────────────
import plotly.graph_objects as go
import plotly.express as px

import os

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="EcoTrack 🌱",
    page_icon="🌍",
    layout="wide"
)

# ==================================================
# SQLITE — History Tracker
# ==================================================
def init_db():
    conn = sqlite3.connect("ecotrack_history.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            predicted REAL,
            score INTEGER,
            transport TEXT,
            diet TEXT,
            distance REAL,
            screen_time INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_prediction(predicted, score, transport, diet, distance, screen_time):
    conn = sqlite3.connect("ecotrack_history.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (date, predicted, score, transport, diet, distance, screen_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), predicted, score, transport, diet, distance, screen_time))
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect("ecotrack_history.db")
    df = pd.read_sql_query("SELECT * FROM history ORDER BY date DESC LIMIT 30", conn)
    conn.close()
    return df

init_db()

# ==================================================
# BACKGROUND IMAGE
# ==================================================
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    page_bg = f"""
    <style>
    .stApp {{
        background-color: #0e1117;
        background-image:
            linear-gradient(rgba(10,15,20,0.85), rgba(10,15,20,0.85)),
            url("data:image/jpeg;base64,{encoded}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 950px;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

set_background("background.jpeg")

# ==================================================
# GLOBAL STYLES
# ==================================================
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #e6edf3; font-family: "Segoe UI", sans-serif; }
.stApp::before { content:""; position:fixed; inset:0; background:rgba(10,15,20,0.65); z-index:-1; }
h1, h2, h3, h4 { color: #ffffff !important; }

section[data-testid="stSidebar"] { background-color: #0b0f14; border-right: 1px solid #30363d; }
section[data-testid="stSidebar"] * { color: #e6edf3 !important; }
section[data-testid="stSidebar"] label { font-weight:500; color:#c9d1d9 !important; }
section[data-testid="stSidebar"] p { color:#9da7b3 !important; }

div[data-baseweb="select"] > div { background-color:#1e1b2e !important; color:#c084fc !important; border:1px solid #3b2a5c !important; }
div[data-baseweb="select"] span { color:#c084fc !important; font-weight:500 !important; }
ul[role="listbox"] { background-color:#161b22 !important; }
ul[role="listbox"] li { color:#c084fc !important; font-weight:500 !important; }
ul[role="listbox"] li:hover { background-color:#2a1f3d !important; color:#ffffff !important; }
ul[role="option"][aria-selected="true"] { background-color:#3b2a5c !important; color:#ffffff !important; }

.eco-card {
    background: rgba(22,27,34,0.85); backdrop-filter:blur(6px);
    border:1px solid #30363d; border-radius:14px; padding:20px;
    margin-bottom:18px; box-shadow:0 8px 30px rgba(0,0,0,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.eco-card:hover { transform:translateY(-4px); box-shadow:0 12px 35px rgba(0,0,0,0.5); }
.eco-success { background: linear-gradient(135deg,#1f6f43,#2ea043); color:white; }
.eco-warning { background:#3d2f00; color:#ffcc00; }
.eco-info { background:rgba(28,31,38,0.9); border-left:4px solid #2ea043; }

.stButton > button {
    background: linear-gradient(135deg,#2ea043,#3fb950);
    color:black; border-radius:12px; font-size:1.05rem; height:3em; border:none;
}
.stButton > button:hover { background: linear-gradient(135deg,#3fb950,#56d364); }
[data-testid="stMetricValue"] { color:#3fb950; }
p, span, li { color:#e6edf3 !important; }

.block-container { padding-top:1.5rem !important; max-width:1150px; margin:auto; }
header[data-testid="stHeader"] { background:transparent; }
h1 { margin-bottom:0.3em !important; }
h2 { margin-top:1.2em !important; margin-bottom:0.6em !important; }
.stMarkdown { margin-bottom:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False




# ==================================================
# LANDING PAGE
# ==================================================
if not st.session_state.show_dashboard:

    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { display: none !important; }
        .block-container { max-width: 1000px !important; padding-top: 1rem !important; }
        </style>
    """, unsafe_allow_html=True)

    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.4;transform:scale(1.5);} }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:transparent; font-family:'Segoe UI',sans-serif; color:#e6edf3; padding:20px; }

        .hero { display:flex; flex-direction:column; align-items:center; text-align:center; padding:40px 20px 30px; }
        .badge {
            display:inline-flex; align-items:center; gap:8px; padding:6px 18px;
            border:1px solid rgba(46,160,67,0.4); border-radius:100px;
            font-size:0.72rem; font-weight:600; color:#3fb950;
            background:rgba(46,160,67,0.08); letter-spacing:0.08em;
            text-transform:uppercase; margin-bottom:28px;
        }
        .dot { width:7px; height:7px; border-radius:50%; background:#3fb950; animation:pulse 2s infinite; display:inline-block; }
        .title { font-size:3.5rem; font-weight:900; line-height:1.05; letter-spacing:-0.03em; color:#fff; margin-bottom:20px; }
        .title .green { color:#3fb950; }
        .title .dim { color:#6b8f78; font-weight:600; font-size:3rem; display:block; }
        .desc { font-size:1rem; color:rgba(226,245,234,0.6); max-width:500px; margin:0 auto 40px; line-height:1.7; }

        .features { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; max-width:840px; margin:0 auto 36px; text-align:left; }
        .card { background:rgba(22,27,34,0.9); border:1px solid rgba(46,160,67,0.15); border-radius:12px; padding:20px; }
        .card-icon { font-size:1.4rem; margin-bottom:10px; }
        .card-title { font-size:0.88rem; font-weight:700; color:#e6edf3; margin-bottom:6px; }
        .card-desc { font-size:0.76rem; color:#6b8f78; line-height:1.6; }

        .divider { height:1px; background:linear-gradient(90deg,transparent,rgba(46,160,67,0.25),transparent); max-width:840px; margin:0 auto 28px; }
        .stats { display:flex; gap:48px; justify-content:center; flex-wrap:wrap; margin-bottom:28px; text-align:center; }
        .stat-val { font-size:1.9rem; font-weight:800; color:#3fb950; letter-spacing:-0.03em; }
        .stat-lbl { font-size:0.74rem; color:#6b8f78; margin-top:4px; }
    </style>
    </head>
    <body>
    <div class="hero">
        <div class="badge"><span class="dot"></span>&nbsp; Bengaluru-Aware Carbon Intelligence</div>
        <div class="title">
            Track Your <span class="green">Carbon</span>
            <span class="dim">Smarter Than Ever</span>
        </div>
        <div class="desc">
            EcoTrack combines machine learning and explainable AI to give you
            hyper-local carbon footprint insights built specifically for
            Bengaluru's lifestyle, traffic, and habits.
        </div>
    </div>

    <div class="features">
        <div class="card"><div class="card-icon">🤖</div><div class="card-title">ML-Powered Predictions</div><div class="card-desc">A trained Random Forest model predicts your monthly CO₂ based on your real lifestyle inputs.</div></div>
        <div class="card"><div class="card-icon">🗺️</div><div class="card-title">Bengaluru-Aware AI</div><div class="card-desc">Calibrated with Bengaluru's traffic factor, grid emissions, and city average benchmarks.</div></div>
        <div class="card"><div class="card-icon">📊</div><div class="card-title">Explainable Insights</div><div class="card-desc">Every score is broken down clearly — transport, diet, energy — with ranked reduction suggestions.</div></div>
        <div class="card"><div class="card-icon">📈</div><div class="card-title">History Tracker</div><div class="card-desc">Track your emissions over time with a SQLite-backed history and trend line chart.</div></div>
        <div class="card"><div class="card-icon">📄</div><div class="card-title">PDF Report</div><div class="card-desc">Download a full personalised carbon report as a PDF to share or save anytime.</div></div>
        <div class="card"><div class="card-icon">🌿</div><div class="card-title">Sustainability Persona</div><div class="card-desc">Discover if you're an Urban Commuter, Low-impact Minimalist, or Digital Heavy User.</div></div>
    </div>

    <div class="divider"></div>
    <div class="stats">
        <div><div class="stat-val">1300 kg</div><div class="stat-lbl">Bengaluru Monthly Avg CO₂</div></div>
        <div><div class="stat-val">22%</div><div class="stat-lbl">Avg Reduction Possible</div></div>
        <div><div class="stat-val">3 mins</div><div class="stat-lbl">To Get Your Score</div></div>
        <div><div class="stat-val">Free</div><div class="stat-lbl">Always & Forever</div></div>
    </div>
    <div class="divider"></div>
    </body>
    </html>
    """, height=780, scrolling=False)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='text-align:center; margin-bottom:12px; color:rgba(226,245,234,0.5); font-size:0.9rem;'>Ready to know your carbon footprint?</div>", unsafe_allow_html=True)
        if st.button("🌍 Open EcoTrack Dashboard →", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()
    st.markdown("<div style='text-align:center; margin-top:16px; color:#6b8f78; font-size:0.75rem;'>No sign-up required · 100% local to Bengaluru · Powered by ML</div>", unsafe_allow_html=True)


# ==================================================
# DASHBOARD
# ==================================================
else:
    BENGALURU_TRAFFIC_FACTOR = 1.15
    BENGALURU_AVG_EMISSION = 1300

    model = joblib.load("Ecotrack_rf_model.pkl")

    # ── SIDEBAR ──────────────────────────────────────
    st.sidebar.title("🌱 EcoTrack Controls")
    st.sidebar.caption("Bengaluru-aware carbon intelligence")

    body_type   = st.sidebar.selectbox("Body Type", ["underweight", "normal", "overweight", "obese"])
    sex         = st.sidebar.selectbox("Sex", ["male", "female"])
    diet        = st.sidebar.selectbox("Diet", ["omnivore", "vegetarian", "pescatarian"])
    shower      = st.sidebar.selectbox("Shower Frequency", ["daily", "twice a day", "more frequently", "less frequently"])
    transport   = st.sidebar.selectbox("Transport Mode", ["private", "public", "walk/bicycle"])
    vehicle_type= st.sidebar.selectbox("Vehicle Type", ["petrol", "diesel", "electric", "none"])
    energy_eff  = st.sidebar.selectbox("Energy Efficient Home?", ["Yes", "No"])

    st.sidebar.divider()

    distance    = st.sidebar.slider("Vehicle Distance / Month (km)", 0, 5000, 1200)
    grocery     = st.sidebar.slider("Monthly Grocery Bill (₹)", 50, 500, 200)
    screen_time = st.sidebar.slider("TV / PC Hours per Day", 0, 15, 6)
    internet_time = st.sidebar.slider("Internet Hours per Day", 0, 15, 6)
    clothes     = st.sidebar.slider("New Clothes / Month", 0, 10, 3)

    st.sidebar.divider()
    if st.sidebar.button("← Back to Home"):
        st.session_state.show_dashboard = False
        st.rerun()

    predict_btn = st.sidebar.button("🌍 Predict Carbon Footprint")

    # ── HEADER ───────────────────────────────────────
    st.title("🌍 EcoTrack Dashboard")
    st.subheader("City-aware carbon footprint intelligence for Bengaluru 🌆")
    st.info("This dashboard combines **machine learning**, **explainable AI**, and **human-centered design** to help reduce carbon emissions realistically.")

    # ── TABS ─────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📊 My Results", "📈 My History", "ℹ️ About"])

    # ── FEATURE DICT ─────────────────────────────────
    user_input = {
        "body_type": body_type, "sex": sex, "diet": diet,
        "how_often_shower": shower, "heating_energy_source": "coal",
        "transport": transport,
        "vehicle_type": vehicle_type if transport == "private" else "none",
        "social_activity": "often", "monthly_grocery_bill": grocery,
        "frequency_of_traveling_by_air": "rarely",
        "vehicle_monthly_distance_km": distance,
        "waste_bag_size": "medium", "waste_bag_weekly_count": 3,
        "how_long_tv_pc_daily_hour": screen_time,
        "how_many_new_clothes_monthly": clothes,
        "how_long_internet_daily_hour": internet_time,
        "energy_efficiency": energy_eff,
        "recycle_metal": 1, "recycle_plastic": 0,
        "recycle_glass": 0, "recycle_paper": 0,
        "cook_stove": 1, "cook_oven": 1, "cook_microwave": 0,
        "cook_grill": 0, "cook_airfryer": 0
    }

    def habit_difficulty(title):
        if "Work from home" in title: return "🟢 Easy"
        elif "Metro" in title: return "🟡 Medium"
        elif "vegetarian" in title: return "🔴 Hard"
        return "🟡 Medium"

    def sustainability_personality():
        if transport == "private" and distance > 1000: return "🚗 Urban Commuter"
        elif screen_time > 7: return "💻 Digital Heavy User"
        elif diet != "omnivore" and transport != "private": return "🌱 Low-impact Minimalist"
        return "⚖️ Balanced Urban Lifestyle"

    # ════════════════════════════════════════════════
    # TAB 1 — RESULTS
    # ════════════════════════════════════════════════
    with tab1:
        if predict_btn:
            df_input = pd.DataFrame([user_input])
            predicted = model.predict(df_input)[0]
            if transport == "private":
                predicted *= BENGALURU_TRAFFIC_FACTOR

            if predicted <= 1000:   score, level = 90, "🟢 Excellent"
            elif predicted <= 2000: score, level = 65, "🟡 Moderate"
            else:                   score, level = 40, "🔴 High Impact"

            diff = ((predicted - BENGALURU_AVG_EMISSION) / BENGALURU_AVG_EMISSION) * 100
            personality = sustainability_personality()

            # ── Score Cards ──────────────────────────
            colA, colB, colC = st.columns(3)
            with colA:
                st.markdown(f"""<div class="eco-card eco-success">
                🌍 <b>Monthly Emission</b><br>
                <span style="font-size:32px">{predicted:.1f} kg CO₂</span>
                </div>""", unsafe_allow_html=True)
            with colB:
                st.markdown(f"""<div class="eco-card">
                🌱 <b>Carbon Score</b><br>
                <span style="font-size:32px">{score}/100</span><br>{level}
                </div>""", unsafe_allow_html=True)
            with colC:
                st.markdown(f"""<div class="eco-card eco-warning">
                📊 {abs(diff):.1f}% {"above" if diff > 0 else "below"} Bengaluru average
                </div>""", unsafe_allow_html=True)

            # ── Explainability ───────────────────────
            st.markdown("""<div class="eco-card eco-info">🔍 <b>Why is your footprint at this level?</b></div>""", unsafe_allow_html=True)
            if transport == "private" and distance > 1000: st.write("• 🚗 High private vehicle usage in Bengaluru traffic")
            if diet == "omnivore":                          st.write("• 🥩 Omnivorous diet has higher carbon intensity")
            if screen_time > 6:                             st.write("• 📺 High screen time increases electricity usage")

            # ── Personality ──────────────────────────
            st.markdown(f"""<div class="eco-card">
            🧬 <b>Sustainability Personality</b><br>
            <span style="font-size:22px">{personality}</span>
            </div>""", unsafe_allow_html=True)

            # ── Suggestions ──────────────────────────
            st.header("🌱 Top Optimization Suggestions")
            suggestions = []

            def add_suggestion(title, new_pred):
                saving = predicted - new_pred
                if saving <= 1: return
                suggestions.append({"title": title, "saving": saving,
                                     "percent": (saving/predicted)*100,
                                     "difficulty": habit_difficulty(title)})

            if transport == "private":
                mod = copy.deepcopy(user_input)
                mod["transport"] = "public"; mod["vehicle_type"] = "none"
                mod["vehicle_monthly_distance_km"] *= 0.6
                add_suggestion("🚇 Use Namma Metro for office commute", model.predict(pd.DataFrame([mod]))[0])

            mod = copy.deepcopy(user_input)
            mod["vehicle_monthly_distance_km"] *= 0.8
            add_suggestion("🏠 Work from home 1 day/week", model.predict(pd.DataFrame([mod]))[0])

            if diet == "omnivore":
                mod = copy.deepcopy(user_input)
                mod["diet"] = "vegetarian"
                add_suggestion("🥗 Go vegetarian 3–4 days/week", model.predict(pd.DataFrame([mod]))[0])

            suggestions.sort(key=lambda x: x["saving"], reverse=True)

            for i, s in enumerate(suggestions, 1):
                st.markdown(f"""<div class="eco-card">
                <b>{i}. {s['title']}</b><br>
                Difficulty: {s['difficulty']}<br>
                Save ~<b>{s['saving']:.1f} kg CO₂/month</b> ({s['percent']:.2f}% reduction)
                </div>""", unsafe_allow_html=True)

            # ════════════════════════════════════════
            # 🆕 FEATURE 1 — PLOTLY CHARTS
            # ════════════════════════════════════════
            st.header("📊 Emission Breakdown")

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                # Estimate category breakdown
                transport_em = (distance * 0.21 * BENGALURU_TRAFFIC_FACTOR) if transport == "private" else (distance * 0.05)
                diet_em      = {"omnivore": 400, "pescatarian": 250, "vegetarian": 150}.get(diet, 300)
                screen_em    = screen_time * 30 * 0.05
                internet_em  = internet_time * 30 * 0.03
                grocery_em   = grocery * 0.5
                other_em     = max(predicted - transport_em - diet_em - screen_em - internet_em - grocery_em, 50)

                labels = ["🚗 Transport", "🥩 Diet", "📺 Screen Time", "🌐 Internet", "🛒 Grocery", "🏠 Other"]
                values = [transport_em, diet_em, screen_em, internet_em, grocery_em, other_em]
                colors = ["#2ea043", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899", "#6b7280"]

                fig_pie = go.Figure(go.Pie(
                    labels=labels, values=values,
                    hole=0.45,
                    marker=dict(colors=colors, line=dict(color="#0e1117", width=2)),
                    textfont=dict(color="white", size=12),
                    hovertemplate="<b>%{label}</b><br>%{value:.1f} kg CO₂<br>%{percent}<extra></extra>"
                ))
                fig_pie.update_layout(
                    title=dict(text="Monthly Emission by Category", font=dict(color="white", size=14)),
                    paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                    margin=dict(t=50, b=10, l=10, r=10), height=340
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_chart2:
                # Bar chart — current vs with suggestions
                if suggestions:
                    bar_labels  = ["Current"] + [s["title"].split(" ", 2)[-1][:22] + "…" if len(s["title"]) > 25 else s["title"] for s in suggestions]
                    bar_values  = [predicted] + [predicted - s["saving"] for s in suggestions]
                    bar_colors  = ["#ef4444"] + ["#2ea043"] * len(suggestions)

                    fig_bar = go.Figure(go.Bar(
                        x=bar_labels, y=bar_values,
                        marker_color=bar_colors,
                        text=[f"{v:.0f} kg" for v in bar_values],
                        textposition="outside",
                        textfont=dict(color="white"),
                        hovertemplate="<b>%{x}</b><br>%{y:.1f} kg CO₂<extra></extra>"
                    ))
                    fig_bar.update_layout(
                        title=dict(text="Current vs Optimised Emissions", font=dict(color="white", size=14)),
                        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                        xaxis=dict(tickfont=dict(color="white"), gridcolor="#30363d"),
                        yaxis=dict(tickfont=dict(color="white"), gridcolor="#30363d",
                                   title=dict(text="kg CO₂/month", font=dict(color="#9da7b3"))),
                        margin=dict(t=50, b=10, l=10, r=10), height=340,
                        showlegend=False
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

            # Score gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Your Carbon Score", "font": {"color": "white", "size": 16}},
                number={"suffix": "/100", "font": {"color": "#3fb950", "size": 36}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "white", "tickfont": {"color": "white"}},
                    "bar": {"color": "#2ea043"},
                    "bgcolor": "#161b22",
                    "bordercolor": "#30363d",
                    "steps": [
                        {"range": [0, 40],  "color": "#3d1515"},
                        {"range": [40, 70], "color": "#3d2f00"},
                        {"range": [70, 100],"color": "#0f3320"},
                    ],
                    "threshold": {"line": {"color": "#3fb950", "width": 3}, "value": score}
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#161b22", font_color="white",
                margin=dict(t=40, b=10, l=40, r=40), height=260
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Annual projection
            st.markdown("""<div class="eco-card eco-info">📅 <b>Annual Carbon Projection</b></div>""", unsafe_allow_html=True)
            st.write(f"🔴 Current lifestyle: **{predicted*12/1000:.2f} tons CO₂/year**")
            if suggestions:
                st.write(f"🟢 With top suggestion: **{(predicted - suggestions[0]['saving'])*12/1000:.2f} tons CO₂/year**")

            # ════════════════════════════════════════
            # SAVE TO HISTORY
            # ════════════════════════════════════════
            save_prediction(predicted, score, transport, diet, distance, screen_time)
            st.success("✅ This prediction has been saved to your history! Check the 📈 My History tab.")

        else:
            st.markdown("""
            <div class="eco-card eco-info" style="text-align:center; padding:40px;">
                <h3 style="color:#3fb950;">👈 Set your inputs in the sidebar</h3>
                <p style="color:#9da7b3; margin-top:10px;">Adjust your lifestyle details on the left, then click<br>
                <b>🌍 Predict Carbon Footprint</b> to see your results.</p>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════
    # TAB 2 — HISTORY TRACKER
    # ════════════════════════════════════════════════
    with tab2:
        st.header("📈 Your Emission History")
        history_df = load_history()

        if history_df.empty:
            st.markdown("""<div class="eco-card eco-info" style="text-align:center; padding:40px;">
                <h3 style="color:#3fb950;">No history yet!</h3>
                <p style="color:#9da7b3; margin-top:10px;">Run your first prediction in the 📊 My Results tab to start tracking.</p>
            </div>""", unsafe_allow_html=True)
        else:
            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Predictions", len(history_df))
            m2.metric("Latest Emission", f"{history_df.iloc[0]['predicted']:.0f} kg")
            m3.metric("Best Score", f"{history_df['score'].max()}/100")
            m4.metric("Avg Emission", f"{history_df['predicted'].mean():.0f} kg")

            # Line chart — emission over time
            history_df["date"] = pd.to_datetime(history_df["date"])
            history_sorted = history_df.sort_values("date")

            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=history_sorted["date"],
                y=history_sorted["predicted"],
                mode="lines+markers",
                name="Your Emissions",
                line=dict(color="#2ea043", width=2.5),
                marker=dict(color="#3fb950", size=8, line=dict(color="#0e1117", width=2)),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:.1f} kg CO₂<extra></extra>"
            ))
            # Bengaluru average reference line
            fig_line.add_hline(
                y=BENGALURU_AVG_EMISSION, line_dash="dash",
                line_color="#f59e0b", line_width=1.5,
                annotation_text="Bengaluru Avg (1300 kg)",
                annotation_font_color="#f59e0b"
            )
            fig_line.update_layout(
                title=dict(text="Monthly CO₂ Emissions Over Time", font=dict(color="white", size=15)),
                paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                xaxis=dict(tickfont=dict(color="white"), gridcolor="#30363d", title=dict(text="Date", font=dict(color="#9da7b3"))),
                yaxis=dict(tickfont=dict(color="white"), gridcolor="#30363d", title=dict(text="kg CO₂/month", font=dict(color="#9da7b3"))),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=50, b=30, l=10, r=10), height=380
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Score trend
            fig_score = go.Figure()
            fig_score.add_trace(go.Bar(
                x=history_sorted["date"],
                y=history_sorted["score"],
                marker_color=["#2ea043" if s >= 70 else "#f59e0b" if s >= 50 else "#ef4444" for s in history_sorted["score"]],
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Score: %{y}/100<extra></extra>"
            ))
            fig_score.update_layout(
                title=dict(text="Carbon Score Over Time (higher = better)", font=dict(color="white", size=15)),
                paper_bgcolor="#161b22", plot_bgcolor="#161b22",
                xaxis=dict(tickfont=dict(color="white"), gridcolor="#30363d"),
                yaxis=dict(tickfont=dict(color="white"), gridcolor="#30363d", range=[0, 105],
                           title=dict(text="Score /100", font=dict(color="#9da7b3"))),
                margin=dict(t=50, b=30, l=10, r=10), height=300, showlegend=False
            )
            st.plotly_chart(fig_score, use_container_width=True)

            # Raw table
            with st.expander("📋 View Raw History Table"):
                display_df = history_df[["date","predicted","score","transport","diet","distance","screen_time"]].copy()
                display_df.columns = ["Date","Emission (kg)","Score","Transport","Diet","Distance (km)","Screen Time (h)"]
                st.dataframe(display_df, use_container_width=True)

            # Clear history button
            if st.button("🗑️ Clear All History"):
                conn = sqlite3.connect("ecotrack_history.db")
                conn.execute("DELETE FROM history")
                conn.commit()
                conn.close()
                st.success("History cleared!")
                st.rerun()

    # ════════════════════════════════════════════════
    # TAB 3 — ABOUT
    # ════════════════════════════════════════════════
    with tab3:
        st.header("ℹ️ About EcoTrack")
        st.markdown("""
        <div class="eco-card">
        <b>🌍 What is EcoTrack?</b><br><br>
        EcoTrack is a Bengaluru-aware carbon footprint intelligence tool that combines a trained
        <b>Random Forest ML model</b> with explainable AI to give hyper-local emission insights.
        </div>

        <div class="eco-card">
        <b>🤖 How does the ML model work?</b><br><br>
        The model was trained on the <b>Carbon Emissions dataset</b> and predicts monthly CO₂ output
        based on 25 lifestyle features. Bengaluru-specific factors like the city's traffic multiplier
        (1.15x) and average emission baseline (1300 kg/month) are applied post-prediction.
        </div>

        <div class="eco-card eco-info">
        <b>🐙 Open Source</b><br><br>
        EcoTrack is open source! Contributions welcome on GitHub.<br>
        Features roadmap: multi-city support · community leaderboard · BESCOM energy integration
        </div>
        """, unsafe_allow_html=True)