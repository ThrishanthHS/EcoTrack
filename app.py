import streamlit as st
import pandas as pd
import joblib
import copy
import base64
import sqlite3
import datetime
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(page_title="EcoTrack — Know Your Impact", page_icon="", layout="wide")

# ── DB ────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("ecotrack_history.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, predicted REAL, score INTEGER,
        transport TEXT, diet TEXT, distance REAL, screen_time INTEGER)""")
    conn.commit(); conn.close()

def save_prediction(predicted, score, transport, diet, distance, screen_time):
    conn = sqlite3.connect("ecotrack_history.db")
    conn.execute("INSERT INTO history (date,predicted,score,transport,diet,distance,screen_time) VALUES (?,?,?,?,?,?,?)",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), predicted, score, transport, diet, distance, screen_time))
    conn.commit(); conn.close()

def load_history():
    conn = sqlite3.connect("ecotrack_history.db")
    df = pd.read_sql_query("SELECT * FROM history ORDER BY date DESC LIMIT 30", conn)
    conn.close(); return df

init_db()

# ── BACKGROUND ───────────────────────────────────
def set_background(f):
    with open(f,"rb") as fp: enc = base64.b64encode(fp.read()).decode()
    st.markdown(f"""<style>.stApp{{background-color:#080808;background-image:linear-gradient(rgba(8,8,8,0.91),rgba(8,8,8,0.91)),url("data:image/jpeg;base64,{enc}");background-size:cover;background-attachment:fixed;}}</style>""", unsafe_allow_html=True)

set_background("background.jpeg")

# ── GLOBAL STYLES ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

*{-webkit-font-smoothing:antialiased;}
.stApp{background-color:#080808;font-family:'Inter',sans-serif;color:#d8d0c0;}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"]{background:#0a0a0a !important;border-right:1px solid rgba(201,168,76,0.12) !important;}
section[data-testid="stSidebar"] *{color:#c8bfb0 !important;}
section[data-testid="stSidebar"] label{font-size:0.73rem !important;font-weight:600 !important;color:#8a8070 !important;letter-spacing:0.07em !important;text-transform:uppercase !important;}

/* ── INPUTS ── */
div[data-baseweb="select"]>div{background:#121212 !important;border:1px solid rgba(201,168,76,0.2) !important;border-radius:6px !important;}
div[data-baseweb="select"] span{color:#d8d0c0 !important;font-size:0.85rem !important;}
ul[role="listbox"]{background:#121212 !important;border:1px solid rgba(201,168,76,0.15) !important;}
ul[role="listbox"] li{color:#c8bfb0 !important;font-size:0.85rem !important;}
ul[role="listbox"] li:hover{background:rgba(201,168,76,0.08) !important;color:#C9A84C !important;}
ul[role="option"][aria-selected="true"]{background:rgba(201,168,76,0.12) !important;color:#C9A84C !important;}
.stSlider>div>div>div{background:rgba(201,168,76,0.18) !important;}
.stSlider>div>div>div>div{background:#C9A84C !important;}
[data-testid="stTickBarMin"],[data-testid="stTickBarMax"]{color:#8a8070 !important;font-size:0.72rem !important;}

/* ── BUTTON ── */
.stButton>button{
    background:linear-gradient(135deg,#C9A84C,#e8c870) !important;
    color:#000000 !important;border:none !important;border-radius:7px !important;
    font-family:'Inter',sans-serif !important;font-weight:800 !important;
    font-size:0.88rem !important;letter-spacing:0.07em !important;
    height:3.2em !important;text-transform:uppercase !important;
    transition:all 0.2s ease !important;
    box-shadow:0 4px 20px rgba(201,168,76,0.35) !important;
}
.stButton>button p,
.stButton>button div,
.stButton>button span{
    color:#000000 !important;font-weight:800 !important;
}
.stButton>button:hover{
    background:linear-gradient(135deg,#f0d070,#C9A84C) !important;
    box-shadow:0 8px 32px rgba(201,168,76,0.5) !important;
    transform:translateY(-2px) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{background:#0a0a0a !important;border-bottom:1px solid rgba(201,168,76,0.12) !important;gap:0 !important;padding:0 !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;color:#6a6050 !important;font-family:'Inter',sans-serif !important;font-size:0.78rem !important;font-weight:600 !important;letter-spacing:0.09em !important;text-transform:uppercase !important;padding:16px 32px !important;border-bottom:2px solid transparent !important;}
.stTabs [aria-selected="true"]{color:#C9A84C !important;border-bottom:2px solid #C9A84C !important;}
.stTabs [data-baseweb="tab-panel"]{background:transparent !important;padding:32px 0 !important;}

/* ── CARDS ── */
.card{background:#0f0f0f;border:1px solid rgba(201,168,76,0.12);border-radius:10px;padding:26px 28px;margin-bottom:16px;transition:border-color 0.35s,box-shadow 0.35s;animation:fadeUp 0.5s ease both;}
.card:hover{border-color:rgba(201,168,76,0.25);box-shadow:0 12px 40px rgba(0,0,0,0.6);}
.card-gold{background:linear-gradient(145deg,#0f0f0f,#110f04);border:1px solid rgba(201,168,76,0.3);border-radius:10px;padding:26px 28px;margin-bottom:16px;animation:fadeUp 0.5s ease both,glowGold 3.5s 1s ease infinite;}
.card-green{background:linear-gradient(145deg,#070f08,#0a1509);border:1px solid rgba(46,160,67,0.25);border-radius:10px;padding:26px 28px;margin-bottom:16px;animation:fadeUp 0.5s ease both;}
.card-red{background:linear-gradient(145deg,#0f0707,#150909);border:1px solid rgba(210,60,60,0.2);border-radius:10px;padding:26px 28px;margin-bottom:16px;animation:fadeUp 0.5s ease both;}
.card-flat{background:#0f0f0f;border:1px solid rgba(201,168,76,0.08);border-radius:8px;padding:20px 24px;margin-bottom:12px;}

/* ── METRICS ── */
[data-testid="stMetricValue"]{color:#C9A84C !important;font-family:'Cormorant Garamond',serif !important;font-size:2rem !important;font-weight:600 !important;}
[data-testid="stMetricLabel"]{color:#8a8070 !important;font-size:0.72rem !important;text-transform:uppercase !important;letter-spacing:0.08em !important;}

/* ── TYPOGRAPHY ── */
h1{font-family:'Cormorant Garamond',serif !important;font-size:2.1rem !important;font-weight:600 !important;color:#f0e8d8 !important;}
h2{font-family:'Cormorant Garamond',serif !important;font-size:1.6rem !important;font-weight:600 !important;color:#f0e8d8 !important;}
p{color:#a09880 !important;line-height:1.75 !important;}

/* ── ALERTS ── */
.stSuccess{background:rgba(46,160,67,0.07) !important;border:1px solid rgba(46,160,67,0.2) !important;border-radius:8px !important;}
.stSuccess *{color:#5abf6a !important;}

/* ── LAYOUT ── */
.block-container{padding-top:2rem !important;padding-left:2.5rem !important;padding-right:2.5rem !important;max-width:1220px;margin:auto;}
header[data-testid="stHeader"]{background:transparent !important;}
.streamlit-expanderHeader{background:#0f0f0f !important;border:1px solid rgba(201,168,76,0.1) !important;border-radius:6px !important;color:#9a9080 !important;font-size:0.78rem !important;}

/* ── ANIMATIONS ── */
@keyframes fadeUp  {from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn  {from{opacity:0}to{opacity:1}}
@keyframes lineGrow{from{width:0}to{width:100%}}
@keyframes glowGold{0%,100%{box-shadow:0 0 0 rgba(201,168,76,0)}50%{box-shadow:0 0 30px rgba(201,168,76,0.1)}}
@keyframes shimmer {0%,100%{opacity:0.2}50%{opacity:0.7}}
@keyframes spin    {from{stroke-dashoffset:var(--dash-start)}to{stroke-dashoffset:var(--dash-end)}}

.a0{animation:fadeUp 0.5s ease both;}
.a1{animation:fadeUp 0.5s 0.1s ease both;}
.a2{animation:fadeUp 0.5s 0.2s ease both;}
.a3{animation:fadeUp 0.5s 0.3s ease both;}
.a4{animation:fadeUp 0.5s 0.4s ease both;}
.af{animation:fadeIn 0.6s ease both;}

/* ── LABELS ── */
.pill{display:inline-block;padding:4px 13px;border-radius:100px;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;}
.pill-g{background:rgba(46,160,67,0.12);color:#4ecf5e;border:1px solid rgba(46,160,67,0.25);}
.pill-o{background:rgba(201,168,76,0.12);color:#d4aa50;border:1px solid rgba(201,168,76,0.25);}
.pill-r{background:rgba(210,60,60,0.12);color:#d86060;border:1px solid rgba(210,60,60,0.22);}

/* ── SECTION LABELS ── */
.sec-lbl{font-size:0.68rem;font-weight:700;color:#8a8070;letter-spacing:0.14em;text-transform:uppercase;margin:32px 0 18px;display:flex;align-items:center;gap:14px;}
.sec-lbl::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(201,168,76,0.15),transparent);}

/* ── STAT ── */
.stat-num{font-family:'Cormorant Garamond',serif;font-size:3rem;font-weight:600;line-height:1;color:#f0e8d8;}

/* ── PROGRESS ── */
.pbar-bg{background:#1a1a1a;border-radius:3px;height:3px;margin-top:10px;overflow:hidden;}
.pbar-fill{height:100%;border-radius:3px;animation:lineGrow 1.4s ease both;}
</style>
""", unsafe_allow_html=True)

# ── SESSION ───────────────────────────────────────
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

# ══════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════
if not st.session_state.show_dashboard:
    st.markdown("""<style>section[data-testid="stSidebar"]{display:none !important;}
    .block-container{max-width:980px !important;padding-top:1rem !important;}</style>""", unsafe_allow_html=True)

    components.html("""<!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet"/>
    <style>
        @keyframes fadeUp  {from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:translateY(0)}}
        @keyframes fadeIn  {from{opacity:0}to{opacity:1}}
        @keyframes shimmer {0%,100%{opacity:0.2}50%{opacity:0.8}}
        @keyframes floatUp {0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
        @keyframes particle{0%{transform:translateY(0) translateX(0);opacity:0}10%{opacity:1}90%{opacity:0.3}100%{transform:translateY(-120px) translateX(var(--dx));opacity:0}}

        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:transparent;font-family:'Inter',sans-serif;color:#d8d0c0;padding:32px 44px 24px;overflow:hidden;}

        canvas{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;}
        .content{position:relative;z-index:1;}

        .topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:64px;padding-bottom:18px;border-bottom:1px solid rgba(201,168,76,0.08);animation:fadeIn 0.5s ease both;}
        .logo{font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-weight:600;color:#f0e8d8;letter-spacing:0.02em;}
        .logo em{color:#C9A84C;font-style:normal;}
        .topbar-r{font-size:0.63rem;color:#3a3530;letter-spacing:0.14em;text-transform:uppercase;}

        .hero{max-width:620px;margin:0 auto 60px;text-align:center;}
        .tag{display:inline-flex;align-items:center;gap:12px;font-size:0.65rem;color:#C9A84C;letter-spacing:0.16em;text-transform:uppercase;margin-bottom:26px;animation:fadeUp 0.6s ease both;}
        .tline{display:inline-block;height:1px;width:36px;background:#C9A84C;animation:shimmer 2.5s ease infinite;}
        .h1{font-family:'Cormorant Garamond',serif;font-size:4rem;font-weight:600;line-height:1.04;color:#f0e8d8;letter-spacing:-0.02em;margin-bottom:12px;animation:fadeUp 0.6s 0.08s ease both;}
        .h1 em{color:#C9A84C;font-style:italic;}
        .sub{font-family:'Cormorant Garamond',serif;font-size:1.4rem;color:#6a6050;font-style:italic;margin-bottom:24px;animation:fadeUp 0.6s 0.16s ease both;}
        .desc{font-size:0.88rem;color:#7a7060;line-height:1.85;max-width:420px;margin:0 auto;animation:fadeUp 0.6s 0.24s ease both;}

        .vline{width:1px;height:44px;background:linear-gradient(180deg,transparent,rgba(201,168,76,0.3),transparent);margin:36px auto;animation:shimmer 3s ease infinite;}

        .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(201,168,76,0.07);border:1px solid rgba(201,168,76,0.07);border-radius:10px;overflow:hidden;margin-bottom:48px;animation:fadeUp 0.6s 0.32s ease both;}
        .cell{background:#090909;padding:26px 20px;transition:background 0.3s;}
        .cell:hover{background:#0d0c08;}
        .num{font-family:'Cormorant Garamond',serif;font-size:1.25rem;font-weight:600;color:rgba(201,168,76,0.22);margin-bottom:12px;}
        .ctitle{font-size:0.82rem;font-weight:600;color:#c0b8a8;margin-bottom:7px;}
        .cdesc{font-size:0.74rem;color:#4a4540;line-height:1.72;}

        .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.06);border-radius:10px;overflow:hidden;margin-bottom:36px;animation:fadeUp 0.6s 0.42s ease both;}
        .stat{background:#090909;padding:24px 16px;text-align:center;}
        .sv{font-family:'Cormorant Garamond',serif;font-size:1.85rem;font-weight:600;color:#C9A84C;letter-spacing:-0.02em;margin-bottom:6px;}
        .sl{font-size:0.63rem;color:#3a3530;letter-spacing:0.1em;text-transform:uppercase;}

        .foot{text-align:center;animation:fadeUp 0.6s 0.5s ease both;}
        .foot-txt{font-size:0.62rem;color:#2a2520;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:12px;}
        .dots{display:flex;justify-content:center;gap:7px;}
        .dot{width:3px;height:3px;border-radius:50%;background:rgba(201,168,76,0.3);}
        .dot:nth-child(2){animation:floatUp 2s 0.3s ease infinite;}
        .dot:nth-child(3){animation:floatUp 2s 0.6s ease infinite;}
    </style></head>
    <body>
    <canvas id="c"></canvas>
    <div class="content">
        <div class="topbar">
            <div class="logo">Eco<em>Track</em></div>
            <div class="topbar-r">Bengaluru &nbsp;·&nbsp; Carbon Intelligence &nbsp;·&nbsp; 2026</div>
        </div>
        <div class="hero">
            <div class="tag"><span class="tline"></span>Personal Carbon Intelligence<span class="tline"></span></div>
            <div class="h1">Know Your <em>Impact</em><br>on the Planet</div>
            <div class="sub">Built for Bengaluru. Built for you.</div>
            <div class="desc">Answer a few plain questions about your commute, food and home. We tell you exactly how much carbon you produce — and the two or three changes that will make the biggest difference.</div>
        </div>
        <div class="grid">
            <div class="cell"><div class="num">01</div><div class="ctitle">Built for Bengaluru</div><div class="cdesc">Uses real local traffic, transport and energy data — not global averages that do not apply here.</div></div>
            <div class="cell"><div class="num">02</div><div class="ctitle">Results in 2 Minutes</div><div class="cdesc">No sign-up. No complicated forms. A few plain questions and your result is instant.</div></div>
            <div class="cell"><div class="num">03</div><div class="ctitle">Personalised Actions</div><div class="cdesc">We tell you the two or three specific changes that will reduce your footprint the most.</div></div>
            <div class="cell"><div class="num">04</div><div class="ctitle">City Comparison</div><div class="cdesc">See exactly where you stand against the Bengaluru average — and what it means.</div></div>
            <div class="cell"><div class="num">05</div><div class="ctitle">Progress Tracking</div><div class="cdesc">Your history is saved automatically. Return regularly to see if things improve.</div></div>
            <div class="cell"><div class="num">06</div><div class="ctitle">Completely Private</div><div class="cdesc">No account required. Nothing collected. Everything stays on your device.</div></div>
        </div>
        <div class="vline"></div>
        <div class="stats">
            <div class="stat"><div class="sv">1,300</div><div class="sl">kg · Bengaluru monthly avg</div></div>
            <div class="stat"><div class="sv">22%</div><div class="sl">Average reduction possible</div></div>
            <div class="stat"><div class="sv">2 min</div><div class="sl">Time to your result</div></div>
            <div class="stat"><div class="sv">Free</div><div class="sl">Always, no exceptions</div></div>
        </div>
        <div class="foot">
            <div class="foot-txt">No sign-up &nbsp;·&nbsp; No data collected &nbsp;·&nbsp; Open source</div>
            <div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
    </div>

    <script>
    const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
    let W,H,pts=[];
    function resize(){W=canvas.width=window.innerWidth;H=canvas.height=window.innerHeight;}
    window.addEventListener('resize',resize);resize();
    const G='rgba(201,168,76,';
    for(let i=0;i<60;i++) pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.15,vy:(Math.random()-.5)*.15,r:Math.random()*1.1+.2,a:Math.random()*.3+.04,da:(Math.random()-.5)*.002});
    function draw(){
        ctx.clearRect(0,0,W,H);
        pts.forEach(p=>{
            p.x+=p.vx;p.y+=p.vy;p.a+=p.da;
            if(p.a>.38||p.a<.03)p.da*=-1;
            if(p.x<0||p.x>W)p.vx*=-1;
            if(p.y<0||p.y>H)p.vy*=-1;
            ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
            ctx.fillStyle=G+p.a+')';ctx.fill();
        });
        for(let i=0;i<pts.length;i++) for(let j=i+1;j<pts.length;j++){
            const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);
            if(d<105){ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.strokeStyle=G+(0.035*(1-d/105))+')';ctx.lineWidth=.4;ctx.stroke();}
        }
        requestAnimationFrame(draw);
    }
    draw();
    </script>
    </body></html>""", height=830, scrolling=False)

    c1,c2,c3 = st.columns([1,1.2,1])
    with c2:
        if st.button("Calculate My Carbon Footprint", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()

# ══════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════
else:
    BENGALURU_AVG = 1300
    TRAFFIC_FACTOR = 1.15
    model = joblib.load("Ecotrack_rf_model.pkl")

    # ── SIDEBAR ──────────────────────────────────
    st.sidebar.markdown("""<div style='padding:26px 14px 18px;border-bottom:1px solid rgba(201,168,76,0.08);margin-bottom:20px;'>
        <div style='font-family:Cormorant Garamond,serif;font-size:1.25rem;font-weight:600;color:#f0e8d8;'>EcoTrack</div>
        <div style='font-size:0.65rem;color:#5a5040;margin-top:4px;letter-spacing:0.12em;text-transform:uppercase;'>Carbon Calculator · Bengaluru</div>
    </div>""", unsafe_allow_html=True)

    def sb_sec(label):
        st.sidebar.markdown(f"<div style='font-size:0.64rem;color:#5a5040;letter-spacing:0.13em;text-transform:uppercase;margin:18px 0 10px;padding-bottom:6px;border-bottom:1px solid rgba(201,168,76,0.06);'>{label}</div>", unsafe_allow_html=True)

    sb_sec("About You")
    body_type = st.sidebar.selectbox("Body type", ["underweight","normal","overweight","obese"])
    sex       = st.sidebar.selectbox("Gender", ["male","female"])

    sb_sec("Your Food")
    diet   = st.sidebar.selectbox("What do you usually eat?", ["omnivore","vegetarian","pescatarian"],
                help="Omnivore = meat + veg  |  Vegetarian = no meat  |  Pescatarian = fish only")
    shower = st.sidebar.selectbox("How often do you shower?", ["daily","twice a day","more frequently","less frequently"])

    sb_sec("Your Commute")
    transport    = st.sidebar.selectbox("How do you travel?", ["private","public","walk/bicycle"],
                    help="Private = own car/bike  |  Public = bus/metro  |  Walk/Bicycle = no engine")
    vehicle_type = st.sidebar.selectbox("Vehicle type", ["petrol","diesel","electric","none"])
    distance     = st.sidebar.slider("Distance per month (km)", 0, 5000, 1200)

    sb_sec("Your Home")
    energy_eff    = st.sidebar.selectbox("Energy-saving appliances?", ["Yes","No"])
    grocery       = st.sidebar.slider("Monthly grocery spend (Rs)", 50, 500, 200)
    screen_time   = st.sidebar.slider("TV / computer hours per day", 0, 15, 6)
    internet_time = st.sidebar.slider("Internet hours per day", 0, 15, 6)
    clothes       = st.sidebar.slider("New clothes per month", 0, 10, 3)

    st.sidebar.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.sidebar.divider()
    if st.sidebar.button("Back to Home", use_container_width=True):
        st.session_state.show_dashboard = False; st.rerun()
    predict_btn = st.sidebar.button("Calculate My Footprint", use_container_width=True)

    # ── HEADER ───────────────────────────────────
    st.markdown("""<div class="af" style='padding-bottom:18px;border-bottom:1px solid rgba(201,168,76,0.08);margin-bottom:4px;'>
        <div style='font-size:0.65rem;color:#6a6050;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;'>Bengaluru · Personal Carbon Report</div>
        <div style='font-family:Cormorant Garamond,serif;font-size:2rem;font-weight:600;color:#f0e8d8;'>Your Carbon Footprint Dashboard</div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["My Results", "My Progress", "About"])

    user_input = {
        "body_type":body_type,"sex":sex,"diet":diet,"how_often_shower":shower,
        "heating_energy_source":"coal","transport":transport,
        "vehicle_type":vehicle_type if transport=="private" else "none",
        "social_activity":"often","monthly_grocery_bill":grocery,
        "frequency_of_traveling_by_air":"rarely",
        "vehicle_monthly_distance_km":distance,"waste_bag_size":"medium",
        "waste_bag_weekly_count":3,"how_long_tv_pc_daily_hour":screen_time,
        "how_many_new_clothes_monthly":clothes,"how_long_internet_daily_hour":internet_time,
        "energy_efficiency":energy_eff,"recycle_metal":1,"recycle_plastic":0,
        "recycle_glass":0,"recycle_paper":0,"cook_stove":1,"cook_oven":1,
        "cook_microwave":0,"cook_grill":0,"cook_airfryer":0
    }

    def get_persona():
        if transport=="private" and distance>1000:
            return "The Daily Driver","Your commute is by far the biggest factor in your footprint. Bengaluru traffic makes private vehicles significantly more polluting than open-road driving. Switching to the metro even two days a week would produce a meaningful monthly saving."
        elif screen_time>7:
            return "The Digital Resident","You spend a significant number of hours on screens and devices every day. This creates a steady electricity draw that adds up substantially across a full month."
        elif diet!="omnivore" and transport!="private":
            return "The Conscious Commuter","You are already making strong choices. Your diet and travel habits put you well ahead of most Bengalureans. Focus on energy use at home for further improvement."
        return "The Balanced Urbanite","Your footprint is spread fairly evenly across categories. Consistent small improvements in your commute, diet and home energy will compound over time."

    # ══════════════════════════════════════════════
    # TAB 1 — RESULTS
    # ══════════════════════════════════════════════
    with tab1:
        if predict_btn:
            predicted = model.predict(pd.DataFrame([user_input]))[0]
            if transport=="private": predicted *= TRAFFIC_FACTOR

            if   predicted<=1000: score,pill,pc,level = 90,"Excellent","pill-g","Well below the city average"
            elif predicted<=1300: score,pill,pc,level = 72,"Good","pill-g","Close to the city average"
            elif predicted<=2000: score,pill,pc,level = 55,"Moderate","pill-o","Room to improve"
            else:                 score,pill,pc,level = 35,"High","pill-r","Significantly above average"

            diff       = ((predicted-BENGALURU_AVG)/BENGALURU_AVG)*100
            ab         = "above" if diff>0 else "below"
            diff_color = "#e06060" if diff>0 else "#4ecf5e"
            dcard      = "card-red" if diff>0 else "card-green"
            pname, pdesc = get_persona()

            # ── 3 Summary Cards ──────────────────
            c1,c2,c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="card-green a0">
                    <div style='font-size:0.63rem;color:#4ecf5e;letter-spacing:0.13em;text-transform:uppercase;margin-bottom:14px;'>Monthly Carbon Output</div>
                    <div class="stat-num">{predicted:.0f}<span style='font-size:1rem;color:#2a5a2a;margin-left:6px;'>kg</span></div>
                    <div style='font-size:0.8rem;color:#4a8a4a;margin-top:9px;'>carbon per month</div>
                    <div class="pbar-bg"><div class="pbar-fill" style='width:{min(predicted/20,100):.0f}%;background:linear-gradient(90deg,#1a5a2a,#4ecf5e);'></div></div>
                    <div style='font-size:0.72rem;color:#2a5a2a;margin-top:9px;'>Equivalent to driving {predicted/0.21:.0f} km in a petrol car</div>
                </div>""", unsafe_allow_html=True)

            with c2:
                circ   = 2 * 3.14159 * 40
                filled = circ * (1 - score / 100)
                ring_anim = f"ringFill{score}"
                st.markdown(f"""
                <style>@keyframes {ring_anim}{{from{{stroke-dashoffset:{circ:.1f}}}to{{stroke-dashoffset:{filled:.1f}}}}}</style>
                <div class="card-gold a1" style='text-align:center;'>
                    <div style='font-size:0.63rem;color:#C9A84C;letter-spacing:0.13em;text-transform:uppercase;margin-bottom:18px;'>Green Score</div>
                    <div style='position:relative;width:130px;height:130px;margin:0 auto 18px;'>
                        <svg width="130" height="130" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="40" fill="none" stroke="#1f1c08" stroke-width="9"/>
                            <circle cx="50" cy="50" r="40" fill="none" stroke="#C9A84C" stroke-width="9"
                                stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}"
                                stroke-linecap="round" transform="rotate(-90 50 50)"
                                style="animation:{ring_anim} 1.6s 0.4s ease forwards;"/>
                        </svg>
                        <div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);'>
                            <div style='font-family:Cormorant Garamond,serif;font-size:2.3rem;font-weight:600;color:#f0e8d8;line-height:1;'>{score}</div>
                            <div style='font-size:0.62rem;color:#5a4a18;letter-spacing:0.04em;margin-top:1px;'>/ 100</div>
                        </div>
                    </div>
                    <div style='margin-bottom:10px;'><span class="pill {pc}" style='font-size:0.73rem;padding:5px 16px;'>{pill}</span></div>
                    <div style='font-size:0.78rem;color:#8a8060;'>{level}</div>
                </div>""", unsafe_allow_html=True)

            with c3:
                st.markdown(f"""<div class="{dcard} a2">
                    <div style='font-size:0.63rem;color:{diff_color};letter-spacing:0.13em;text-transform:uppercase;margin-bottom:14px;'>vs Bengaluru Average</div>
                    <div class="stat-num" style='color:#f0e8d8;'>{abs(diff):.0f}<span style='font-size:1rem;color:#4a3a3a;margin-left:4px;'>%</span></div>
                    <div style='font-size:0.8rem;color:#8a6060;margin-top:9px;'>{ab} the city average</div>
                    <div class="pbar-bg"><div class="pbar-fill" style='width:{min(abs(diff),100):.0f}%;background:{diff_color};'></div></div>
                    <div style='font-size:0.72rem;color:#5a4040;margin-top:9px;'>City average is 1,300 kg per month</div>
                </div>""", unsafe_allow_html=True)

            # ── Persona ───────────────────────────
            st.markdown(f"""<div class="card a3" style='display:flex;align-items:flex-start;gap:20px;'>
                <div style='min-width:3px;height:50px;background:linear-gradient(180deg,#C9A84C,rgba(201,168,76,0));border-radius:2px;margin-top:4px;'></div>
                <div>
                    <div style='font-size:0.63rem;color:#6a6050;letter-spacing:0.13em;text-transform:uppercase;margin-bottom:8px;'>Your Carbon Personality</div>
                    <div style='font-family:Cormorant Garamond,serif;font-size:1.35rem;font-weight:600;color:#C9A84C;margin-bottom:10px;'>{pname}</div>
                    <div style='font-size:0.85rem;color:#9a9080;line-height:1.8;'>{pdesc}</div>
                </div>
            </div>""", unsafe_allow_html=True)

            # ── Emission Breakdown — Horizontal Bars ─
            st.markdown("<div class='sec-lbl'>Where your carbon comes from</div>", unsafe_allow_html=True)

            transport_em = (distance*0.21*TRAFFIC_FACTOR) if transport=="private" else (distance*0.05)
            diet_em      = {"omnivore":400,"pescatarian":250,"vegetarian":150}.get(diet,300)
            screen_em    = screen_time*30*0.05
            internet_em  = internet_time*30*0.03
            grocery_em   = grocery*0.5
            other_em     = max(predicted - transport_em - diet_em - screen_em - internet_em - grocery_em, 30)
            total_check  = transport_em + diet_em + screen_em + internet_em + grocery_em + other_em

            categories = [
                ("Commute & Travel", transport_em, "#C9A84C"),
                ("Food & Diet",      diet_em,      "#9a7acd"),
                ("TV & Devices",     screen_em,    "#5a9acd"),
                ("Internet",         internet_em,  "#4aaa6a"),
                ("Groceries",        grocery_em,   "#cd6a8a"),
                ("Other",            other_em,     "#5a5a5a"),
            ]

            st.markdown("<div class='card a4' style='padding:24px 28px;'>", unsafe_allow_html=True)
            bar_html = "<div style='display:flex;flex-direction:column;gap:14px;'>"
            for name, val, color in categories:
                pct = (val / total_check * 100) if total_check > 0 else 0
                bar_html += f"""
                <div>
                    <div style='display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;'>
                        <div style='font-size:0.82rem;font-weight:500;color:#c0b8a8;'>{name}</div>
                        <div style='font-size:0.8rem;color:{color};font-weight:600;'>{val:.0f} kg &nbsp;<span style='color:#4a4540;font-weight:400;font-size:0.72rem;'>({pct:.0f}%)</span></div>
                    </div>
                    <div style='background:#1a1a1a;border-radius:4px;height:6px;overflow:hidden;'>
                        <div style='height:100%;width:{pct:.1f}%;background:{color};border-radius:4px;animation:lineGrow 1.2s ease both;'></div>
                    </div>
                </div>"""
            bar_html += "</div>"
            st.markdown(bar_html + "</div>", unsafe_allow_html=True)

            # ── What's Driving It ─────────────────
            st.markdown("<div class='sec-lbl'>What is driving your footprint</div>", unsafe_allow_html=True)
            reasons = []
            if transport=="private" and distance>1000:
                reasons.append(("Your daily commute","Driving through Bengaluru traffic is the largest single contributor for most residents. Stop-and-go conditions burn significantly more fuel than open road driving."))
            if diet=="omnivore":
                reasons.append(("Your diet","Meat production requires more land, water and energy than plant-based food. Cutting meat three or four days a week makes a noticeable difference without major lifestyle change."))
            if screen_time>6:
                reasons.append(("Screen and device usage","Extended use of televisions and computers draws a steady electricity load. Over a full month this adds up to a meaningful share of your home energy footprint."))
            if not reasons:
                reasons.append(("Well-balanced lifestyle","Your habits are relatively low-impact across all areas. Look at the suggestions below for small further improvements."))

            for i,(title,exp) in enumerate(reasons):
                st.markdown(f"""<div class="card-flat" style='animation:fadeUp 0.5s {i*0.1:.1f}s ease both;display:flex;gap:18px;align-items:flex-start;'>
                    <div style='font-family:Cormorant Garamond,serif;font-size:1rem;color:rgba(201,168,76,0.25);font-weight:600;min-width:22px;padding-top:1px;'>{i+1:02d}</div>
                    <div>
                        <div style='font-size:0.86rem;font-weight:600;color:#d0c8b8;margin-bottom:6px;'>{title}</div>
                        <div style='font-size:0.81rem;color:#7a7060;line-height:1.8;'>{exp}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ── Suggestions ───────────────────────
            suggestions = []
            def add_s(title, plain, exp, new_pred):
                s = predicted - new_pred
                if s>1: suggestions.append({"title":title,"plain":plain,"exp":exp,"saving":s,"pct":(s/predicted)*100})

            if transport=="private":
                mod = copy.deepcopy(user_input)
                mod["transport"]="public"; mod["vehicle_type"]="none"; mod["vehicle_monthly_distance_km"]*=0.6
                add_s("Switch to Namma Metro","Take the metro",
                    "Using Bengaluru's metro instead of driving significantly reduces travel emissions. Even two or three days a week produces a meaningful monthly saving.",
                    model.predict(pd.DataFrame([mod]))[0])

            mod = copy.deepcopy(user_input); mod["vehicle_monthly_distance_km"]*=0.8
            add_s("Work from Home One Day a Week","Work from home",
                "Removing one commute day per week cuts your travel by 20 percent. A small structural change with a consistent weekly benefit.",
                model.predict(pd.DataFrame([mod]))[0])

            if diet=="omnivore":
                mod = copy.deepcopy(user_input); mod["diet"]="vegetarian"
                add_s("Eat Meat-Free Three Days a Week","Reduce meat intake",
                    "You do not need to give up meat entirely. Skipping it three or four days a week noticeably reduces your diet's carbon cost.",
                    model.predict(pd.DataFrame([mod]))[0])

            suggestions.sort(key=lambda x: x["saving"], reverse=True)

            if suggestions:
                st.markdown("<div class='sec-lbl'>Your top actions to reduce your footprint</div>", unsafe_allow_html=True)
                for i,s in enumerate(suggestions):
                    st.markdown(f"""<div class="card" style='animation:fadeUp 0.5s {i*0.12:.2f}s ease both;'>
                        <div style='display:flex;gap:20px;align-items:flex-start;'>
                            <div style='font-family:Cormorant Garamond,serif;font-size:2rem;font-weight:600;color:rgba(201,168,76,0.18);min-width:32px;line-height:1;'>{i+1:02d}</div>
                            <div style='flex:1;'>
                                <div style='font-size:0.9rem;font-weight:600;color:#d0c8b8;margin-bottom:7px;'>{s['title']}</div>
                                <div style='font-size:0.81rem;color:#7a7060;line-height:1.8;margin-bottom:13px;'>{s['exp']}</div>
                                <div style='display:flex;align-items:center;gap:12px;flex-wrap:wrap;'>
                                    <span class="pill pill-g">Save {s['saving']:.0f} kg / month</span>
                                    <span style='font-size:0.72rem;color:#5a5040;'>{s['pct']:.0f}% reduction in your total</span>
                                </div>
                                <div class="pbar-bg" style='margin-top:9px;'><div class="pbar-fill" style='width:{min(s["pct"],100):.0f}%;background:linear-gradient(90deg,#1a5a2a,#4ecf5e);'></div></div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)

            # ── Annual View ───────────────────────
            st.markdown("<div class='sec-lbl'>Your full year picture</div>", unsafe_allow_html=True)
            yearly      = predicted*12/1000
            yearly_best = (predicted-suggestions[0]["saving"])*12/1000 if suggestions else yearly
            saving_yr   = yearly-yearly_best

            y1,y2 = st.columns(2)
            with y1:
                st.markdown(f"""<div class="card-red">
                    <div style='font-size:0.63rem;color:#c06060;letter-spacing:0.13em;text-transform:uppercase;margin-bottom:14px;'>Your Current Yearly Total</div>
                    <div class="stat-num">{yearly:.1f}<span style='font-size:1rem;color:#5a3030;margin-left:6px;'>tonnes</span></div>
                    <div style='font-size:0.78rem;color:#7a5050;margin-top:12px;line-height:1.8;'>
                        of carbon dioxide per year.<br>
                        About {yearly/0.006:.0f} trees would be needed to absorb this.
                    </div>
                </div>""", unsafe_allow_html=True)
            with y2:
                st.markdown(f"""<div class="card-green">
                    <div style='font-size:0.63rem;color:#4ecf5e;letter-spacing:0.13em;text-transform:uppercase;margin-bottom:14px;'>With Your Top Action</div>
                    <div class="stat-num">{yearly_best:.1f}<span style='font-size:1rem;color:#2a5a2a;margin-left:6px;'>tonnes</span></div>
                    <div style='font-size:0.78rem;color:#4a7a4a;margin-top:12px;line-height:1.8;'>
                        A saving of <b style='color:#4ecf5e;'>{saving_yr:.1f} tonnes</b> per year —<br>
                        the equivalent of planting {int(saving_yr/0.006):,} trees.
                    </div>
                </div>""", unsafe_allow_html=True)

            save_prediction(predicted, score, transport, diet, distance, screen_time)
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            st.success("Result saved — open My Progress tab to track your journey over time.")

        else:
            st.markdown("""<div class="af" style='text-align:center;padding:80px 40px;border:1px solid rgba(201,168,76,0.07);border-radius:10px;background:#0a0a0a;margin-top:8px;'>
                <div style='font-family:Cormorant Garamond,serif;font-size:1.4rem;color:#c0b8a8;margin-bottom:14px;font-weight:600;'>Fill in your details to get started</div>
                <div style='font-size:0.84rem;color:#5a5040;max-width:320px;margin:0 auto;line-height:1.85;'>
                    Use the panel on the left to describe your commute, food and home.<br>
                    Then click <b style='color:#C9A84C;'>Calculate My Footprint</b>.
                </div>
            </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # TAB 2 — PROGRESS
    # ══════════════════════════════════════════════
    with tab2:
        st.markdown("<div style='font-family:Cormorant Garamond,serif;font-size:1.45rem;color:#f0e8d8;font-weight:600;margin-bottom:6px;'>Your Progress Over Time</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.78rem;color:#6a6050;margin-bottom:26px;'>Every time you calculate your footprint, the result is saved here automatically.</div>", unsafe_allow_html=True)

        history_df = load_history()
        if history_df.empty:
            st.markdown("""<div class="af" style='text-align:center;padding:64px 40px;border:1px solid rgba(201,168,76,0.07);border-radius:10px;background:#0a0a0a;'>
                <div style='font-family:Cormorant Garamond,serif;font-size:1.25rem;color:#c0b8a8;margin-bottom:12px;'>No history yet</div>
                <div style='font-size:0.82rem;color:#5a5040;line-height:1.8;'>Go to <b style='color:#C9A84C;'>My Results</b>, fill in your details and click Calculate.<br>Your result will appear here automatically.</div>
            </div>""", unsafe_allow_html=True)
        else:
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Times Calculated", len(history_df))
            m2.metric("Latest Reading",   f"{history_df.iloc[0]['predicted']:.0f} kg")
            m3.metric("Best Score",       f"{history_df['score'].max()} / 100")
            m4.metric("Your Average",     f"{history_df['predicted'].mean():.0f} kg / mo")

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            history_df["date"] = pd.to_datetime(history_df["date"])
            hs = history_df.sort_values("date")

            # ── Area Chart — emissions over time ──
            fig_area = go.Figure()
            fig_area.add_trace(go.Scatter(
                x=hs["date"], y=hs["predicted"],
                mode="lines+markers",
                name="Your Carbon",
                line=dict(color="#C9A84C", width=2.5, shape="spline", smoothing=0.8),
                marker=dict(color="#C9A84C", size=7, line=dict(color="#0a0a0a", width=2)),
                fill="tozeroy",
                fillgradient=dict(colorscale=[[0,"rgba(201,168,76,0)"], [1,"rgba(201,168,76,0.08)"]]),
                hovertemplate="<b>%{x|%d %b %Y}</b><br><b style='color:#C9A84C'>%{y:.0f} kg</b> carbon that month<extra></extra>"
            ))
            fig_area.add_hline(y=BENGALURU_AVG, line_dash="dot",
                line_color="rgba(200,80,80,0.45)", line_width=1.5,
                annotation_text="Bengaluru Average (1,300 kg)",
                annotation_font_color="rgba(210,100,100,0.8)",
                annotation_font_size=11)
            fig_area.update_layout(
                title=dict(text="Your monthly carbon — lower means better", font=dict(color="#a09880",size=13,family="Inter")),
                paper_bgcolor="#0f0f0f", plot_bgcolor="#0f0f0f",
                xaxis=dict(tickfont=dict(color="#8a8070",size=11), gridcolor="#181818",
                           title=dict(text="Date", font=dict(color="#6a6050",size=11))),
                yaxis=dict(tickfont=dict(color="#8a8070",size=11), gridcolor="#181818",
                           title=dict(text="kg carbon per month", font=dict(color="#6a6050",size=11))),
                margin=dict(t=48,b=24,l=12,r=12), height=340, showlegend=False
            )
            st.plotly_chart(fig_area, use_container_width=True)

            # ── Score Timeline ─────────────────────
            colors_score = ["#4ecf5e" if s>=70 else "#C9A84C" if s>=50 else "#e06060" for s in hs["score"]]
            fig_score = go.Figure()
            fig_score.add_trace(go.Scatter(
                x=hs["date"], y=hs["score"],
                mode="lines+markers",
                line=dict(color="#C9A84C", width=2, shape="spline", smoothing=0.7),
                marker=dict(color=colors_score, size=10, line=dict(color="#0a0a0a", width=2)),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Score: <b>%{y}</b> / 100<extra></extra>"
            ))
            fig_score.add_hrect(y0=70, y1=100, fillcolor="rgba(46,160,67,0.04)", line_width=0,
                                annotation_text="Good zone", annotation_font_color="rgba(78,207,94,0.5)",
                                annotation_font_size=10)
            fig_score.update_layout(
                title=dict(text="Your green score over time — higher is better", font=dict(color="#a09880",size=13,family="Inter")),
                paper_bgcolor="#0f0f0f", plot_bgcolor="#0f0f0f",
                xaxis=dict(tickfont=dict(color="#8a8070",size=11), gridcolor="#181818"),
                yaxis=dict(tickfont=dict(color="#8a8070",size=11), gridcolor="#181818",
                           range=[0,105], title=dict(text="Score out of 100", font=dict(color="#6a6050",size=11))),
                margin=dict(t=48,b=24,l=12,r=12), height=280, showlegend=False
            )
            st.plotly_chart(fig_score, use_container_width=True)

            # ── Trend summary ─────────────────────
            if len(hs) >= 2:
                first_val = hs.iloc[0]["predicted"]
                last_val  = hs.iloc[-1]["predicted"]
                change    = last_val - first_val
                change_pct= (change/first_val)*100 if first_val>0 else 0
                trend_color = "#4ecf5e" if change<0 else "#e06060"
                trend_word  = "improved" if change<0 else "increased"
                st.markdown(f"""<div class="card" style='display:flex;gap:20px;align-items:center;'>
                    <div style='min-width:3px;height:40px;background:{trend_color};border-radius:2px;'></div>
                    <div>
                        <div style='font-size:0.63rem;color:#6a6050;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;'>Your Trend</div>
                        <div style='font-size:0.88rem;color:#c0b8a8;line-height:1.7;'>
                            Since your first reading, your carbon footprint has <b style='color:{trend_color};'>{trend_word} by {abs(change_pct):.0f}%</b>.
                            Your latest reading is <b style='color:#C9A84C;'>{last_val:.0f} kg</b> per month.
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            with st.expander("View full history table"):
                d = history_df[["date","predicted","score","transport","diet","distance","screen_time"]].copy()
                d.columns = ["Date","Carbon (kg)","Score","Travel","Diet","Distance (km)","Screen (hrs)"]
                st.dataframe(d, use_container_width=True)

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("Clear History"):
                conn = sqlite3.connect("ecotrack_history.db")
                conn.execute("DELETE FROM history"); conn.commit(); conn.close()
                st.rerun()

    # ══════════════════════════════════════════════
    # TAB 3 — ABOUT
    # ══════════════════════════════════════════════
    with tab3:
        st.markdown("<div style='font-family:Cormorant Garamond,serif;font-size:1.45rem;color:#f0e8d8;font-weight:600;margin-bottom:26px;'>About EcoTrack</div>", unsafe_allow_html=True)
        for i,(title,body) in enumerate([
            ("What is EcoTrack?","EcoTrack is a free tool that helps everyday people in Bengaluru understand their personal carbon footprint — the amount of carbon pollution their lifestyle creates each month. Reducing emissions starts with honest, clear awareness."),
            ("Why is it specific to Bengaluru?","Most carbon calculators are built for Western cities using global averages that do not reflect life here. EcoTrack uses local data — Bengaluru traffic patterns, electricity grid characteristics, and city-level averages — so the results reflect your actual daily reality."),
            ("Is my data private?","Yes. Everything you enter stays on your own computer. Nothing is collected, transmitted or sold. Your history is stored only in a local file on your device."),
            ("Open Source","EcoTrack is fully open source. The complete code is on GitHub for anyone to inspect, improve or build upon. Features on the roadmap include multi-city support, neighbourhood comparisons, and BESCOM electricity data integration."),
        ]):
            st.markdown(f"""<div class="card" style='animation:fadeUp 0.5s {i*0.12:.2f}s ease both;display:flex;gap:20px;align-items:flex-start;'>
                <div style='font-family:Cormorant Garamond,serif;font-size:0.95rem;color:rgba(201,168,76,0.22);font-weight:600;min-width:24px;padding-top:2px;'>{i+1:02d}</div>
                <div>
                    <div style='font-size:0.88rem;font-weight:600;color:#d0c8b8;margin-bottom:9px;'>{title}</div>
                    <div style='font-size:0.82rem;color:#7a7060;line-height:1.85;'>{body}</div>
                </div>
            </div>""", unsafe_allow_html=True)