import os
import sys
import streamlit as st
import pandas as pd
import joblib
import copy
import base64
import sqlite3
import datetime
import streamlit.components.v1 as components
import plotly.graph_objects as go

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))
from pipeline import run_pipeline

st.set_page_config(page_title="EcoTrack — Know Your Impact", page_icon="🌿", layout="wide")

# ── MODEL (cached) ────────────────────────────────
@st.cache_resource
def load_model():
    return joblib.load("Ecotrack_rf_model.pkl")

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
    with open(f, "rb") as fp: enc = base64.b64encode(fp.read()).decode()
    st.markdown(f"""<style>.stApp{{background-color:#080808;background-image:linear-gradient(rgba(8,8,8,0.93),rgba(8,8,8,0.93)),url("data:image/jpeg;base64,{enc}");background-size:cover;background-attachment:fixed;}}</style>""", unsafe_allow_html=True)

set_background("frontend/background.jpeg")

# ── GLOBAL STYLES ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

* { -webkit-font-smoothing: antialiased; box-sizing: border-box; }
.stApp { background-color: #080808; font-family: 'Inter', sans-serif; color: #e0d8c8; }

section[data-testid="stSidebar"] {
    background: #0c0c0c !important;
    border-right: 1px solid rgba(201,168,76,0.15) !important;
}
section[data-testid="stSidebar"] * { color: #d8d0c0 !important; }
section[data-testid="stSidebar"] label {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #b0a890 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
section[data-testid="stSidebar"] p {
    font-size: 0.92rem !important;
    color: #c8c0b0 !important;
}

div[data-baseweb="select"] > div {
    background: linear-gradient(135deg, #141210, #1c1a10) !important;
    border: 1px solid rgba(201,168,76,0.25) !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] span {
    color: #e0d8c8 !important;
    font-size: 0.95rem !important;
    font-weight: 400 !important;
}
ul[role="listbox"] {
    background: #111008 !important;
    border: 1px solid rgba(201,168,76,0.2) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.8) !important;
}
ul[role="listbox"] li {
    color: #d0c8b8 !important;
    font-size: 0.95rem !important;
    padding: 11px 16px !important;
    border-bottom: 1px solid rgba(201,168,76,0.05) !important;
}
ul[role="listbox"] li:hover {
    background: linear-gradient(90deg, rgba(201,168,76,0.12), transparent) !important;
    color: #f0e8c8 !important;
}
ul[role="option"][aria-selected="true"] {
    background: linear-gradient(90deg, rgba(201,168,76,0.16), transparent) !important;
    color: #C9A84C !important;
    font-weight: 600 !important;
}

.stDataFrame { border: 1px solid rgba(201,168,76,0.12) !important; border-radius: 8px !important; overflow: hidden !important; }
.stDataFrame thead tr th {
    background: linear-gradient(135deg, #141210, #1c1a10) !important;
    color: #C9A84C !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    font-weight: 700 !important;
    border-bottom: 1px solid rgba(201,168,76,0.18) !important;
    padding: 12px 16px !important;
}
.stDataFrame tbody tr td {
    background: #0d0d0d !important;
    color: #d0c8b8 !important;
    font-size: 0.92rem !important;
    border-bottom: 1px solid rgba(201,168,76,0.06) !important;
    padding: 10px 16px !important;
}
.stDataFrame tbody tr:hover td { background: rgba(201,168,76,0.05) !important; }
[data-testid="stDataFrameResizable"] { background: #0d0d0d !important; }

.stSlider > div > div > div { background: rgba(201,168,76,0.2) !important; }
.stSlider > div > div > div > div { background: #C9A84C !important; }
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {
    color: #a09880 !important;
    font-size: 0.85rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, #C9A84C, #e8c870) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.06em !important;
    height: 3.4em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.35) !important;
}
.stButton > button p,
.stButton > button div,
.stButton > button span { color: #000000 !important; font-weight: 700 !important; }
.stButton > button:hover {
    background: linear-gradient(135deg, #f0d070, #C9A84C) !important;
    box-shadow: 0 8px 32px rgba(201,168,76,0.55) !important;
    transform: translateY(-2px) !important;
}

.stSpinner > div { border-top-color: #C9A84C !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #0a0a0a !important;
    border-bottom: 1px solid rgba(201,168,76,0.15) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #8a8070 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 16px 36px !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.2s !important;
}
.stTabs [aria-selected="true"] {
    color: #C9A84C !important;
    border-bottom: 2px solid #C9A84C !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 36px 0 !important;
}

.card {
    background: #0f0f0f;
    border: 1px solid rgba(201,168,76,0.14);
    border-radius: 12px;
    padding: 28px 30px;
    margin-bottom: 18px;
    transition: border-color 0.3s, box-shadow 0.3s;
    animation: fadeUp 0.5s ease both;
}
.card:hover {
    border-color: rgba(201,168,76,0.3);
    box-shadow: 0 12px 40px rgba(0,0,0,0.6);
}
.card-gold {
    background: linear-gradient(145deg, #0f0f0f, #130f04);
    border: 1px solid rgba(201,168,76,0.32);
    border-radius: 12px;
    padding: 28px 30px;
    margin-bottom: 18px;
    animation: fadeUp 0.5s ease both, glowGold 3.5s 1s ease infinite;
}
.card-green {
    background: linear-gradient(145deg, #070f08, #0b1709);
    border: 1px solid rgba(46,160,67,0.28);
    border-radius: 12px;
    padding: 28px 30px;
    margin-bottom: 18px;
    animation: fadeUp 0.5s ease both;
}
.card-red {
    background: linear-gradient(145deg, #0f0707, #170909);
    border: 1px solid rgba(210,60,60,0.25);
    border-radius: 12px;
    padding: 28px 30px;
    margin-bottom: 18px;
    animation: fadeUp 0.5s ease both;
}
.card-flat {
    background: #0f0f0f;
    border: 1px solid rgba(201,168,76,0.1);
    border-radius: 10px;
    padding: 22px 26px;
    margin-bottom: 14px;
}

[data-testid="stMetricValue"] {
    color: #C9A84C !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2.2rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    color: #a09880 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.85rem !important;
}

h1 { font-family: 'Cormorant Garamond', serif !important; font-size: 2.4rem !important; font-weight: 600 !important; color: #f0e8d8 !important; }
h2 { font-family: 'Cormorant Garamond', serif !important; font-size: 1.8rem !important; font-weight: 600 !important; color: #f0e8d8 !important; }
p  { color: #c8c0b0 !important; line-height: 1.8 !important; font-size: 0.98rem !important; }

.stSuccess { background: rgba(46,160,67,0.09) !important; border: 1px solid rgba(46,160,67,0.25) !important; border-radius: 8px !important; }
.stSuccess * { color: #6acf7a !important; font-size: 0.95rem !important; }
.stError { background: rgba(210,60,60,0.09) !important; border: 1px solid rgba(210,60,60,0.25) !important; border-radius: 8px !important; }
.stError * { color: #d86060 !important; font-size: 0.95rem !important; }

.block-container { padding-top: 2rem !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; max-width: 1240px; margin: auto; }
header[data-testid="stHeader"] { background: transparent !important; }
.streamlit-expanderHeader {
    background: #0f0f0f !important;
    border: 1px solid rgba(201,168,76,0.12) !important;
    border-radius: 8px !important;
    color: #b0a890 !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
}

@keyframes fadeUp   { from { opacity: 0; transform: translateY(18px) } to { opacity: 1; transform: translateY(0) } }
@keyframes fadeIn   { from { opacity: 0 } to { opacity: 1 } }
@keyframes lineGrow { from { width: 0 } to { width: 100% } }
@keyframes glowGold { 0%,100% { box-shadow: 0 0 0 rgba(201,168,76,0) } 50% { box-shadow: 0 0 30px rgba(201,168,76,0.12) } }
@keyframes shimmer  { 0%,100% { opacity: 0.25 } 50% { opacity: 0.8 } }

.a0 { animation: fadeUp 0.5s ease both; }
.a1 { animation: fadeUp 0.5s 0.1s ease both; }
.a2 { animation: fadeUp 0.5s 0.2s ease both; }
.a3 { animation: fadeUp 0.5s 0.3s ease both; }
.a4 { animation: fadeUp 0.5s 0.4s ease both; }
.af { animation: fadeIn 0.6s ease both; }

.pill { display: inline-block; padding: 5px 14px; border-radius: 100px; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; }
.pill-g { background: rgba(46,160,67,0.14); color: #5acf6a; border: 1px solid rgba(46,160,67,0.3); }
.pill-o { background: rgba(201,168,76,0.14); color: #d4aa50; border: 1px solid rgba(201,168,76,0.3); }
.pill-r { background: rgba(210,60,60,0.14); color: #d86060; border: 1px solid rgba(210,60,60,0.28); }

.sec-lbl {
    font-size: 0.85rem;
    font-weight: 700;
    color: #a09880;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    margin: 36px 0 20px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.sec-lbl::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(201,168,76,0.18), transparent);
}

.stat-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.2rem;
    font-weight: 600;
    line-height: 1;
    color: #f0e8d8;
}
.pbar-bg  { background: #1e1e1e; border-radius: 4px; height: 4px; margin-top: 12px; overflow: hidden; }
.pbar-fill { height: 100%; border-radius: 4px; animation: lineGrow 1.4s ease both; }
.card-lbl {
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.card-body {
    font-size: 0.96rem;
    color: #c0b8a8;
    line-height: 1.82;
}
.card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #C9A84C;
    margin-bottom: 10px;
}

/* ── AGENT PIPELINE VISUAL ── */
.agent-box {
    text-align: center;
    padding: 16px 20px;
    background: #141210;
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 8px;
    min-width: 130px;
    transition: border-color 0.3s;
}
.agent-box:hover { border-color: rgba(201,168,76,0.5); }
.agent-num {
    font-size: 0.78rem;
    color: #C9A84C;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.agent-name {
    font-size: 0.94rem;
    color: #e0d8c8;
    font-weight: 600;
    margin-bottom: 4px;
}
.agent-desc {
    font-size: 0.85rem;
    color: #7a7060;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION ───────────────────────────────────────
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

# ══════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════
if not st.session_state.show_dashboard:
    st.markdown("""<style>
        section[data-testid="stSidebar"] { display: none !important; }
        .block-container { max-width: 1000px !important; padding-top: 1rem !important; }
    </style>""", unsafe_allow_html=True)

    components.html("""<!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
    <style>
        @keyframes fadeUp  { from { opacity:0; transform:translateY(26px) } to { opacity:1; transform:translateY(0) } }
        @keyframes fadeIn  { from { opacity:0 } to { opacity:1 } }
        @keyframes shimmer { 0%,100% { opacity:0.25 } 50% { opacity:0.85 } }
        @keyframes floatUp { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-5px) } }

        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:transparent; font-family:'Inter',sans-serif; color:#e0d8c8; padding:36px 48px 28px; overflow:hidden; }

        canvas { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; }
        .content { position:relative; z-index:1; }

        .topbar {
            display:flex; justify-content:space-between; align-items:center;
            margin-bottom:60px; padding-bottom:18px;
            border-bottom:1px solid rgba(201,168,76,0.1);
            animation:fadeIn 0.5s ease both;
        }
        .logo { font-family:'Cormorant Garamond',serif; font-size:1.35rem; font-weight:600; color:#f0e8d8; letter-spacing:0.02em; }
        .logo em { color:#C9A84C; font-style:normal; }
        .topbar-r { font-size:0.8rem; color:#6a6050; letter-spacing:0.13em; text-transform:uppercase; }

        .hero { max-width:640px; margin:0 auto 56px; text-align:center; }
        .tag {
            display:inline-flex; align-items:center; gap:14px;
            font-size:0.8rem; color:#C9A84C; letter-spacing:0.15em;
            text-transform:uppercase; margin-bottom:28px;
            animation:fadeUp 0.6s ease both;
        }
        .tline { display:inline-block; height:1px; width:40px; background:#C9A84C; animation:shimmer 2.5s ease infinite; }
        .h1 {
            font-family:'Cormorant Garamond',serif; font-size:4.2rem; font-weight:600;
            line-height:1.04; color:#f0e8d8; letter-spacing:-0.02em;
            margin-bottom:14px; animation:fadeUp 0.6s 0.08s ease both;
        }
        .h1 em { color:#C9A84C; font-style:italic; }
        .sub {
            font-family:'Cormorant Garamond',serif; font-size:1.45rem;
            color:#8a8070; font-style:italic; margin-bottom:22px;
            animation:fadeUp 0.6s 0.16s ease both;
        }
        .desc {
            font-size:1rem; color:#9a9080; line-height:1.9;
            max-width:440px; margin:0 auto;
            animation:fadeUp 0.6s 0.24s ease both;
        }

        .vline {
            width:1px; height:48px;
            background:linear-gradient(180deg,transparent,rgba(201,168,76,0.35),transparent);
            margin:32px auto; animation:shimmer 3s ease infinite;
        }

        .grid {
            display:grid; grid-template-columns:repeat(3,1fr);
            gap:1px; background:rgba(201,168,76,0.08);
            border:1px solid rgba(201,168,76,0.08);
            border-radius:12px; overflow:hidden;
            margin-bottom:44px; animation:fadeUp 0.6s 0.32s ease both;
        }
        .cell { background:#090909; padding:28px 22px; transition:background 0.3s; }
        .cell:hover { background:#0e0c08; }
        .num { font-family:'Cormorant Garamond',serif; font-size:1.3rem; font-weight:600; color:rgba(201,168,76,0.25); margin-bottom:12px; }
        .ctitle { font-size:0.96rem; font-weight:600; color:#d8d0c0; margin-bottom:8px; }
        .cdesc { font-size:0.9rem; color:#7a7260; line-height:1.78; }

        .stats {
            display:grid; grid-template-columns:repeat(4,1fr);
            gap:1px; background:rgba(201,168,76,0.07);
            border:1px solid rgba(201,168,76,0.07);
            border-radius:12px; overflow:hidden;
            margin-bottom:36px; animation:fadeUp 0.6s 0.42s ease both;
        }
        .stat { background:#090909; padding:26px 18px; text-align:center; }
        .sv { font-family:'Cormorant Garamond',serif; font-size:2rem; font-weight:600; color:#C9A84C; letter-spacing:-0.02em; margin-bottom:8px; }
        .sl { font-size:0.8rem; color:#6a6050; letter-spacing:0.09em; text-transform:uppercase; }

        .foot { text-align:center; animation:fadeUp 0.6s 0.5s ease both; }
        .foot-txt { font-size:0.8rem; color:#4a4030; letter-spacing:0.13em; text-transform:uppercase; margin-bottom:14px; }
        .dots { display:flex; justify-content:center; gap:8px; }
        .dot { width:4px; height:4px; border-radius:50%; background:rgba(201,168,76,0.35); }
        .dot:nth-child(2) { animation:floatUp 2s 0.3s ease infinite; }
        .dot:nth-child(3) { animation:floatUp 2s 0.6s ease infinite; }
    </style></head>
    <body>
    <canvas id="c"></canvas>
    <div class="content">
        <div class="topbar">
            <div class="logo">Eco<em>Track</em></div>
            <div class="topbar-r">India &nbsp;·&nbsp; Personal Carbon Intelligence &nbsp;·&nbsp; 2026</div>
        </div>
        <div class="hero">
            <div class="tag"><span class="tline"></span>Personal Carbon Intelligence<span class="tline"></span></div>
            <div class="h1">Know Your <em>Impact</em><br>on the Planet</div>
            <div class="sub">Built for India. Built for you.</div>
            <div class="desc">Answer a few plain questions about your commute, food and home. We calculate your exact carbon output and show you the two or three changes that will make the biggest real-world difference.</div>
        </div>
        <div class="grid">
            <div class="cell">
                <div class="num">01</div>
                <div class="ctitle">Built for India</div>
                <div class="cdesc">Calibrated for Indian commute patterns, dietary habits, and energy consumption — not generic Western averages.</div>
            </div>
            <div class="cell">
                <div class="num">02</div>
                <div class="ctitle">Results in 2 Minutes</div>
                <div class="cdesc">No sign-up. No complicated forms. A few plain questions and your carbon result is instant and accurate.</div>
            </div>
            <div class="cell">
                <div class="num">03</div>
                <div class="ctitle">Personalised Actions</div>
                <div class="cdesc">We identify the specific changes that will reduce your footprint the most — ranked by impact, not guesswork.</div>
            </div>
            <div class="cell">
                <div class="num">04</div>
                <div class="ctitle">National Comparison</div>
                <div class="cdesc">See exactly where you stand against the Indian average and understand what your number means in real terms.</div>
            </div>
            <div class="cell">
                <div class="num">05</div>
                <div class="ctitle">AI Advisor</div>
                <div class="cdesc">Four AI agents analyse your profile, search the web, and generate a personalised 7-day reduction roadmap.</div>
            </div>
            <div class="cell">
                <div class="num">06</div>
                <div class="ctitle">Completely Private</div>
                <div class="cdesc">No account required. Nothing is collected or transmitted. Everything stays on your own device, always.</div>
            </div>
        </div>
        <div class="vline"></div>
        <div class="stats">
            <div class="stat"><div class="sv">1,500</div><div class="sl">kg · India monthly avg</div></div>
            <div class="stat"><div class="sv">4</div><div class="sl">AI agents working for you</div></div>
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
    for(let i=0;i<60;i++) pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.15,vy:(Math.random()-.5)*.15,r:Math.random()*1.2+.3,a:Math.random()*.3+.05,da:(Math.random()-.5)*.002});
    function draw(){
        ctx.clearRect(0,0,W,H);
        pts.forEach(p=>{
            p.x+=p.vx;p.y+=p.vy;p.a+=p.da;
            if(p.a>.4||p.a<.04)p.da*=-1;
            if(p.x<0||p.x>W)p.vx*=-1;
            if(p.y<0||p.y>H)p.vy*=-1;
            ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
            ctx.fillStyle=G+p.a+')';ctx.fill();
        });
        for(let i=0;i<pts.length;i++) for(let j=i+1;j<pts.length;j++){
            const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);
            if(d<110){ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.strokeStyle=G+(0.04*(1-d/110))+')';ctx.lineWidth=.5;ctx.stroke();}
        }
        requestAnimationFrame(draw);
    }
    draw();
    </script>
    </body></html>""", height=840, scrolling=False)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if st.button("Calculate My Carbon Footprint", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()

# ══════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════
else:
    INDIA_AVG = 1500
    model = load_model()

    # ── SIDEBAR ──────────────────────────────────
    st.sidebar.markdown("""
    <div style='padding:28px 16px 20px; border-bottom:1px solid rgba(201,168,76,0.1); margin-bottom:24px;'>
        <div style='font-family:Cormorant Garamond,serif; font-size:1.4rem; font-weight:600; color:#f0e8d8;'>EcoTrack</div>
        <div style='font-size:0.82rem; color:#8a7a60; margin-top:5px; letter-spacing:0.1em; text-transform:uppercase; font-weight:500;'>Personal Carbon Intelligence · India</div>
    </div>""", unsafe_allow_html=True)

    def sb_sec(label):
        st.sidebar.markdown(f"""
        <div style='font-size:0.82rem; color:#8a7a60; letter-spacing:0.11em; text-transform:uppercase;
        font-weight:700; margin:22px 0 12px; padding-bottom:7px;
        border-bottom:1px solid rgba(201,168,76,0.08);'>{label}</div>""", unsafe_allow_html=True)

    sb_sec("About You")
    body_type = st.sidebar.selectbox("Body Type", ["underweight", "normal", "overweight", "obese"])
    sex       = st.sidebar.selectbox("Gender", ["male", "female"])

    sb_sec("Your Food")
    diet   = st.sidebar.selectbox("What do you usually eat?", ["omnivore", "vegetarian", "pescatarian"],
                help="Omnivore = meat + veg  |  Vegetarian = no meat  |  Pescatarian = fish only")
    shower = st.sidebar.selectbox("How often do you shower?", ["daily", "twice a day", "more frequently", "less frequently"])

    sb_sec("Your Commute")
    transport    = st.sidebar.selectbox("Primary mode of travel", ["private", "public", "walk/bicycle"],
                    help="Private = own car/bike  |  Public = bus/metro/train  |  Walk/Bicycle = no engine")
    vehicle_type = st.sidebar.selectbox("Vehicle type", ["petrol", "diesel", "electric", "none"])
    distance     = st.sidebar.slider("Distance per month (km)", 0, 5000, 1200)
    high_traffic = st.sidebar.selectbox("Do you commute in a high-traffic city?", ["Yes", "No"],
                    help="E.g. Delhi, Mumbai, Bengaluru, Pune, Hyderabad")

    sb_sec("Your Home")
    energy_eff    = st.sidebar.selectbox("Do you use energy-saving appliances?", ["Yes", "No"])
    grocery       = st.sidebar.slider("Monthly grocery spend (₹)", 50, 500, 200)
    screen_time   = st.sidebar.slider("TV / computer hours per day", 0, 15, 6)
    internet_time = st.sidebar.slider("Internet hours per day", 0, 15, 6)
    clothes       = st.sidebar.slider("New clothes per month", 0, 10, 3)

    st.sidebar.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.sidebar.divider()
    if st.sidebar.button("← Back to Home", use_container_width=True):
        st.session_state.show_dashboard = False; st.rerun()
    predict_btn = st.sidebar.button("Calculate My Footprint", use_container_width=True)

    TRAFFIC_FACTOR = 1.15 if high_traffic == "Yes" and transport == "private" else 1.0

    # ── HEADER ───────────────────────────────────
    st.markdown("""
    <div class="af" style='padding-bottom:20px; border-bottom:1px solid rgba(201,168,76,0.1); margin-bottom:8px;'>
        <div style='font-size:0.82rem; color:#8a7a60; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:10px; font-weight:600;'>India · Personal Carbon Report</div>
        <div style='font-family:Cormorant Garamond,serif; font-size:2.2rem; font-weight:600; color:#f0e8d8; line-height:1.2;'>Your Carbon Footprint Dashboard</div>
        <div style='font-size:0.98rem; color:#9a9280; margin-top:8px;'>Fill in your details on the left and click <strong style='color:#C9A84C;'>Calculate My Footprint</strong> to get your personalised result.</div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["  My Results  ", "  My Progress  ", "  AI Advisor  ", "  About  "])

    user_input = {
        "body_type": body_type, "sex": sex, "diet": diet, "how_often_shower": shower,
        "heating_energy_source": "coal", "transport": transport,
        "vehicle_type": vehicle_type if transport == "private" else "none",
        "social_activity": "often", "monthly_grocery_bill": grocery,
        "frequency_of_traveling_by_air": "rarely",
        "vehicle_monthly_distance_km": distance, "waste_bag_size": "medium",
        "waste_bag_weekly_count": 3, "how_long_tv_pc_daily_hour": screen_time,
        "how_many_new_clothes_monthly": clothes, "how_long_internet_daily_hour": internet_time,
        "energy_efficiency": energy_eff, "recycle_metal": 1, "recycle_plastic": 0,
        "recycle_glass": 0, "recycle_paper": 0, "cook_stove": 1, "cook_oven": 1,
        "cook_microwave": 0, "cook_grill": 0, "cook_airfryer": 0
    }

    def get_persona():
        if transport == "private" and distance > 1000:
            return ("The Daily Driver",
                    "Your commute is the single biggest driver of your carbon footprint. Urban traffic in Indian cities means private vehicles emit significantly more than their open-road equivalent. Even switching to public transport two days a week produces a measurable monthly saving.")
        elif screen_time > 7:
            return ("The Digital Resident",
                    "You spend a significant portion of each day on screens and devices. This creates a steady electricity draw that compounds across the month — particularly relevant given that a large share of India's grid still relies on coal-based generation.")
        elif diet != "omnivore" and transport != "private":
            return ("The Conscious Commuter",
                    "You are already making strong, informed choices. Your diet and travel habits place you well ahead of the national average. Your next focus area should be home energy efficiency and reducing food waste.")
        return ("The Balanced Urbanite",
                "Your footprint is distributed fairly evenly across categories, with no single dominant driver. Consistent, targeted improvements in commute, diet and home energy will compound meaningfully over time.")

    # ══════════════════════════════════════════════
    # TAB 1 — RESULTS
    # ══════════════════════════════════════════════
    with tab1:
        if predict_btn:
            with st.spinner("Calculating your carbon footprint..."):
                try:
                    predicted = model.predict(pd.DataFrame([user_input]))[0]
                    predicted *= TRAFFIC_FACTOR
                except Exception as e:
                    st.error(f"Something went wrong during prediction: {str(e)}")
                    st.stop()

            if   predicted <= 1000: score, pill, pc, level = 90, "Excellent", "pill-g", "Well below the national average"
            elif predicted <= 1500: score, pill, pc, level = 72, "Good",      "pill-g", "Close to the national average"
            elif predicted <= 2200: score, pill, pc, level = 55, "Moderate",  "pill-o", "Room to improve"
            else:                   score, pill, pc, level = 35, "High",      "pill-r", "Significantly above average"

            diff       = ((predicted - INDIA_AVG) / INDIA_AVG) * 100
            ab         = "above" if diff > 0 else "below"
            diff_color = "#e06060" if diff > 0 else "#4ecf5e"
            dcard      = "card-red" if diff > 0 else "card-green"
            pname, pdesc = get_persona()

            transport_em = (distance * 0.21 * TRAFFIC_FACTOR) if transport == "private" else (distance * 0.05)
            diet_em      = {"omnivore": 400, "pescatarian": 250, "vegetarian": 150}.get(diet, 300)
            screen_em    = screen_time * 30 * 0.05
            internet_em  = internet_time * 30 * 0.03
            grocery_em   = grocery * 0.5
            other_em     = max(predicted - transport_em - diet_em - screen_em - internet_em - grocery_em, 30)

            st.session_state["advisor_data"] = {
                "transport"    : transport,
                "diet"         : diet,
                "distance"     : distance,
                "screen_time"  : screen_time,
                "internet_time": internet_time,
                "grocery"      : grocery,
                "energy_eff"   : energy_eff,
                "high_traffic" : high_traffic,
                "predicted"    : predicted,
                "score"        : score,
                "transport_em" : transport_em,
                "diet_em"      : diet_em,
                "screen_em"    : screen_em,
                "internet_em"  : internet_em,
                "grocery_em"   : grocery_em,
            }

            # ── 3 Summary Cards ──────────────────
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="card-green a0">
                    <div class="card-lbl" style='color:#4ecf5e;'>Monthly Carbon Output</div>
                    <div class="stat-num">{predicted:.0f}<span style='font-size:1.1rem; color:#3a7a3a; margin-left:8px;'>kg CO₂</span></div>
                    <div style='font-size:0.92rem; color:#5a9a5a; margin-top:10px;'>carbon equivalent per month</div>
                    <div class="pbar-bg"><div class="pbar-fill" style='width:{min(predicted/20,100):.0f}%; background:linear-gradient(90deg,#1a5a2a,#4ecf5e);'></div></div>
                    <div style='font-size:0.88rem; color:#4a7a4a; margin-top:10px;'>≈ driving {predicted/0.21:.0f} km in a petrol car</div>
                </div>""", unsafe_allow_html=True)

            with c2:
                circ   = 2 * 3.14159 * 40
                filled = circ * (1 - score / 100)
                ring_anim = f"ringFill{score}"
                st.markdown(f"""
                <style>@keyframes {ring_anim}{{from{{stroke-dashoffset:{circ:.1f}}}to{{stroke-dashoffset:{filled:.1f}}}}}</style>
                <div class="card-gold a1" style='text-align:center;'>
                    <div class="card-lbl" style='color:#C9A84C;'>Green Score</div>
                    <div style='position:relative; width:136px; height:136px; margin:0 auto 20px;'>
                        <svg width="136" height="136" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="40" fill="none" stroke="#1f1c08" stroke-width="8"/>
                            <circle cx="50" cy="50" r="40" fill="none" stroke="#C9A84C" stroke-width="8"
                                stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}"
                                stroke-linecap="round" transform="rotate(-90 50 50)"
                                style="animation:{ring_anim} 1.6s 0.4s ease forwards;"/>
                        </svg>
                        <div style='position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);'>
                            <div style='font-family:Cormorant Garamond,serif; font-size:2.5rem; font-weight:600; color:#f0e8d8; line-height:1;'>{score}</div>
                            <div style='font-size:0.78rem; color:#6a5a20; letter-spacing:0.05em; margin-top:2px;'>/ 100</div>
                        </div>
                    </div>
                    <div style='margin-bottom:12px;'><span class="pill {pc}">{pill}</span></div>
                    <div style='font-size:0.92rem; color:#a09060;'>{level}</div>
                </div>""", unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="{dcard} a2">
                    <div class="card-lbl" style='color:{diff_color};'>vs National Average</div>
                    <div class="stat-num" style='color:#f0e8d8;'>{abs(diff):.0f}<span style='font-size:1.1rem; color:#6a5050; margin-left:6px;'>%</span></div>
                    <div style='font-size:0.92rem; color:#a08080; margin-top:10px;'>{ab} the national average</div>
                    <div class="pbar-bg"><div class="pbar-fill" style='width:{min(abs(diff),100):.0f}%; background:{diff_color};'></div></div>
                    <div style='font-size:0.88rem; color:#7a6060; margin-top:10px;'>India average is approximately 1,500 kg per month</div>
                </div>""", unsafe_allow_html=True)

            # ── Persona ───────────────────────────
            st.markdown(f"""
            <div class="card a3" style='display:flex; align-items:flex-start; gap:22px;'>
                <div style='min-width:3px; height:56px; background:linear-gradient(180deg,#C9A84C,rgba(201,168,76,0)); border-radius:2px; margin-top:4px;'></div>
                <div>
                    <div style='font-size:0.82rem; color:#8a7a60; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:8px; font-weight:600;'>Your Carbon Personality</div>
                    <div class="card-title">{pname}</div>
                    <div class="card-body">{pdesc}</div>
                </div>
            </div>""", unsafe_allow_html=True)

            # ── Emission Breakdown ────────────────
            st.markdown("<div class='sec-lbl'>Emission Breakdown by Category</div>", unsafe_allow_html=True)

            col_pie, col_gauge = st.columns(2)
            with col_pie:
                fig_pie = go.Figure(go.Pie(
                    labels=["Commute & Travel", "Food & Diet", "TV & Devices", "Internet", "Groceries", "Other"],
                    values=[transport_em, diet_em, screen_em, internet_em, grocery_em, other_em],
                    hole=0.55,
                    marker=dict(
                        colors=["#C9A84C", "#9a7acd", "#5a9acd", "#4aaa6a", "#cd6a8a", "#5a5a5a"],
                        line=dict(color="#080808", width=2)
                    ),
                    textfont=dict(color="#e8e0d0", size=13, family="Inter"),
                    hovertemplate="<b>%{label}</b><br>%{value:.0f} kg CO₂<br>%{percent}<extra></extra>"
                ))
                fig_pie.update_layout(
                    title=dict(text="Where does your carbon come from?", font=dict(color="#c0b8a8", size=14, family="Inter")),
                    paper_bgcolor="#0f0f0f", plot_bgcolor="#0f0f0f",
                    legend=dict(font=dict(color="#c0b8a8", size=13, family="Inter"), bgcolor="rgba(0,0,0,0)"),
                    margin=dict(t=48, b=8, l=8, r=8), height=340
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_gauge:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={"text": "Green Score", "font": {"color": "#c0b8a8", "size": 15, "family": "Inter"}},
                    number={"suffix": " / 100", "font": {"color": "#C9A84C", "size": 42, "family": "Cormorant Garamond"}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#3a3a3a", "tickfont": {"color": "#7a7060", "size": 12}},
                        "bar": {"color": "#C9A84C", "thickness": 0.28},
                        "bgcolor": "#0f0f0f",
                        "bordercolor": "rgba(201,168,76,0.1)",
                        "steps": [
                            {"range": [0,  35],  "color": "#180b0b"},
                            {"range": [35, 60],  "color": "#181400"},
                            {"range": [60, 80],  "color": "#0c1a00"},
                            {"range": [80, 100], "color": "#091e00"},
                        ],
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="#0f0f0f", font_color="#c8bfb0",
                    margin=dict(t=48, b=24, l=44, r=44), height=340
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            # ── What's Driving It ─────────────────
            st.markdown("<div class='sec-lbl'>What Is Driving Your Footprint</div>", unsafe_allow_html=True)
            reasons = []
            if transport == "private" and distance > 1000:
                reasons.append(("Your Daily Commute",
                    "Private vehicle use is the single largest contributor for most urban Indians. Stop-and-go city traffic burns significantly more fuel than open-road driving, compounding emissions month after month."))
            if diet == "omnivore":
                reasons.append(("Your Diet",
                    "Meat and dairy production require substantially more land, water and energy than plant-based food. Reducing meat on three or four days a week creates a noticeable monthly reduction without requiring a complete lifestyle overhaul."))
            if screen_time > 6:
                reasons.append(("Screen & Device Usage",
                    "Extended daily use of televisions and computers creates a steady electricity load. Given that a significant portion of India's grid still relies on coal, this adds up to a meaningful share of your home energy footprint."))
            if not reasons:
                reasons.append(("Well-Balanced Lifestyle",
                    "Your habits are already relatively low-impact across all categories. Review the personalised actions below to identify targeted improvements."))

            for i, (title, exp) in enumerate(reasons):
                st.markdown(f"""
                <div class="card-flat" style='animation:fadeUp 0.5s {i*0.1:.1f}s ease both; display:flex; gap:20px; align-items:flex-start;'>
                    <div style='font-family:Cormorant Garamond,serif; font-size:1.1rem; color:rgba(201,168,76,0.3); font-weight:600; min-width:26px; padding-top:2px;'>{i+1:02d}</div>
                    <div>
                        <div style='font-size:0.96rem; font-weight:600; color:#e0d8c8; margin-bottom:8px;'>{title}</div>
                        <div class="card-body">{exp}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ── Suggestions ───────────────────────
            suggestions = []
            def add_s(title, plain, exp, new_pred):
                s = predicted - new_pred
                if s > 1: suggestions.append({"title": title, "plain": plain, "exp": exp, "saving": s, "pct": (s / predicted) * 100})

            if transport == "private":
                mod = copy.deepcopy(user_input)
                mod["transport"] = "public"; mod["vehicle_type"] = "none"; mod["vehicle_monthly_distance_km"] *= 0.6
                add_s("Switch to Public Transport", "Use bus, metro, or train",
                    "Replacing private vehicle trips with public transport significantly cuts your travel emissions. Even shifting two or three commute days per week produces a consistent and measurable monthly saving.",
                    model.predict(pd.DataFrame([mod]))[0])

            mod = copy.deepcopy(user_input); mod["vehicle_monthly_distance_km"] *= 0.8
            add_s("Work from Home One Day a Week", "Reduce commute frequency",
                "Eliminating one commute day per week cuts your monthly travel distance by 20 percent — a small structural change with a compounding weekly benefit that adds up significantly over the year.",
                model.predict(pd.DataFrame([mod]))[0])

            if diet == "omnivore":
                mod = copy.deepcopy(user_input); mod["diet"] = "vegetarian"
                add_s("Reduce Meat Consumption", "Eat meat-free three days a week",
                    "You do not need to eliminate meat entirely. Skipping it on three or four days a week noticeably reduces your diet's carbon cost while requiring minimal lifestyle adjustment.",
                    model.predict(pd.DataFrame([mod]))[0])

            suggestions.sort(key=lambda x: x["saving"], reverse=True)

            if suggestions:
                st.markdown("<div class='sec-lbl'>Your Top Actions — Ranked by Impact</div>", unsafe_allow_html=True)
                for i, s in enumerate(suggestions):
                    st.markdown(f"""
                    <div class="card" style='animation:fadeUp 0.5s {i*0.12:.2f}s ease both;'>
                        <div style='display:flex; gap:22px; align-items:flex-start;'>
                            <div style='font-family:Cormorant Garamond,serif; font-size:2.2rem; font-weight:600; color:rgba(201,168,76,0.2); min-width:36px; line-height:1;'>{i+1:02d}</div>
                            <div style='flex:1;'>
                                <div style='font-size:0.98rem; font-weight:600; color:#e0d8c8; margin-bottom:9px;'>{s['title']}</div>
                                <div class="card-body" style='margin-bottom:14px;'>{s['exp']}</div>
                                <div style='display:flex; align-items:center; gap:14px; flex-wrap:wrap;'>
                                    <span class="pill pill-g">Save {s['saving']:.0f} kg / month</span>
                                    <span style='font-size:0.88rem; color:#8a8060;'>{s['pct']:.0f}% reduction in your total footprint</span>
                                </div>
                                <div class="pbar-bg" style='margin-top:12px;'><div class="pbar-fill" style='width:{min(s["pct"],100):.0f}%; background:linear-gradient(90deg,#1a5a2a,#4ecf5e);'></div></div>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)

            # ── Annual View ───────────────────────
            st.markdown("<div class='sec-lbl'>Your Full Year Picture</div>", unsafe_allow_html=True)
            yearly      = predicted * 12 / 1000
            yearly_best = (predicted - suggestions[0]["saving"]) * 12 / 1000 if suggestions else yearly
            saving_yr   = yearly - yearly_best

            y1, y2 = st.columns(2)
            with y1:
                st.markdown(f"""
                <div class="card-red">
                    <div class="card-lbl" style='color:#c06060;'>Your Current Yearly Total</div>
                    <div class="stat-num">{yearly:.1f}<span style='font-size:1.1rem; color:#6a3a3a; margin-left:8px;'>tonnes CO₂</span></div>
                    <div class="card-body" style='margin-top:14px; color:#9a7070;'>
                        of carbon dioxide equivalent per year.<br>
                        Approximately {predicted*12/0.006:.0f} trees would be needed to absorb this annually.
                    </div>
                </div>""", unsafe_allow_html=True)
            with y2:
                st.markdown(f"""
                <div class="card-green">
                    <div class="card-lbl" style='color:#4ecf5e;'>With Your Top Action Applied</div>
                    <div class="stat-num">{yearly_best:.1f}<span style='font-size:1.1rem; color:#2a5a2a; margin-left:8px;'>tonnes CO₂</span></div>
                    <div class="card-body" style='margin-top:14px; color:#5a8a5a;'>
                        A saving of <strong style='color:#4ecf5e;'>{saving_yr:.1f} tonnes</strong> per year —<br>
                        equivalent to planting <strong style='color:#4ecf5e;'>{int(saving_yr/0.006):,} trees</strong>.
                    </div>
                </div>""", unsafe_allow_html=True)

            save_prediction(predicted, score, transport, diet, distance, screen_time)
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            st.success("✓ Result saved — open the My Progress tab to track your journey over time.")

        else:
            st.markdown("""
            <div class="af" style='text-align:center; padding:90px 48px; border:1px solid rgba(201,168,76,0.08); border-radius:12px; background:#0a0a0a; margin-top:10px;'>
                <div style='font-family:Cormorant Garamond,serif; font-size:1.6rem; color:#e0d8c8; margin-bottom:16px; font-weight:600;'>Fill in your details to get started</div>
                <div style='font-size:0.98rem; color:#8a8070; max-width:360px; margin:0 auto; line-height:1.9;'>
                    Use the panel on the left to describe your commute, food and home habits.<br>
                    Then click <strong style='color:#C9A84C;'>Calculate My Footprint</strong> to see your result.
                </div>
            </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # TAB 2 — PROGRESS
    # ══════════════════════════════════════════════
    with tab2:
        st.markdown("<div style='font-family:Cormorant Garamond,serif; font-size:1.7rem; color:#f0e8d8; font-weight:600; margin-bottom:8px;'>Your Progress Over Time</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.98rem; color:#9a9080; margin-bottom:28px;'>Every time you calculate your footprint, the result is saved here automatically. Return regularly to track whether your habits are improving.</div>", unsafe_allow_html=True)

        history_df = load_history()
        if history_df.empty:
            st.markdown("""
            <div class="af" style='text-align:center; padding:72px 48px; border:1px solid rgba(201,168,76,0.08); border-radius:12px; background:#0a0a0a;'>
                <div style='font-family:Cormorant Garamond,serif; font-size:1.4rem; color:#e0d8c8; margin-bottom:14px;'>No history yet</div>
                <div style='font-size:0.98rem; color:#8a8070; line-height:1.85;'>Go to <strong style='color:#C9A84C;'>My Results</strong>, fill in your details and click Calculate.<br>Your result will appear here automatically.</div>
            </div>""", unsafe_allow_html=True)
        else:
            m1, m2, m3, m4 = st.columns(4)
            delta_latest = f"{history_df.iloc[0]['predicted'] - history_df['predicted'].mean():.0f} kg vs avg"
            m1.metric("Times Calculated", len(history_df))
            m2.metric("Latest Reading",   f"{history_df.iloc[0]['predicted']:.0f} kg", delta=delta_latest)
            m3.metric("Best Score",       f"{history_df['score'].max()} / 100")
            m4.metric("Your Average",     f"{history_df['predicted'].mean():.0f} kg / mo")

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            history_df["date"] = pd.to_datetime(history_df["date"])
            hs = history_df.sort_values("date")

            fig_area = go.Figure()
            fig_area.add_trace(go.Scatter(
                x=hs["date"], y=hs["predicted"],
                mode="lines+markers",
                line=dict(color="#C9A84C", width=2.5, shape="spline", smoothing=0.8),
                marker=dict(color="#C9A84C", size=8, line=dict(color="#0a0a0a", width=2)),
                fill="tozeroy",
                fillgradient=dict(colorscale=[[0, "rgba(201,168,76,0)"], [1, "rgba(201,168,76,0.09)"]]),
                hovertemplate="<b>%{x|%d %b %Y}</b><br><b style='color:#C9A84C'>%{y:.0f} kg</b> CO₂ that month<extra></extra>"
            ))
            fig_area.add_hline(y=INDIA_AVG, line_dash="dot",
                line_color="rgba(200,80,80,0.5)", line_width=1.5,
                annotation_text="India Average (~1,500 kg)",
                annotation_font_color="rgba(220,110,110,0.9)",
                annotation_font_size=13)
            fig_area.update_layout(
                title=dict(text="Monthly carbon output — lower is better", font=dict(color="#c0b8a8", size=15, family="Inter")),
                paper_bgcolor="#0f0f0f", plot_bgcolor="#0f0f0f",
                xaxis=dict(tickfont=dict(color="#a09880", size=13), gridcolor="#181818",
                           title=dict(text="Date", font=dict(color="#8a8070", size=13))),
                yaxis=dict(tickfont=dict(color="#a09880", size=13), gridcolor="#181818",
                           title=dict(text="kg CO₂ per month", font=dict(color="#8a8070", size=13))),
                margin=dict(t=52, b=28, l=16, r=16), height=360, showlegend=False
            )
            st.plotly_chart(fig_area, use_container_width=True)

            colors_score = ["#4ecf5e" if s >= 70 else "#C9A84C" if s >= 50 else "#e06060" for s in hs["score"]]
            fig_score = go.Figure()
            fig_score.add_trace(go.Scatter(
                x=hs["date"], y=hs["score"],
                mode="lines+markers",
                line=dict(color="#C9A84C", width=2.2, shape="spline", smoothing=0.7),
                marker=dict(color=colors_score, size=10, line=dict(color="#0a0a0a", width=2)),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Score: <b>%{y}</b> / 100<extra></extra>"
            ))
            fig_score.add_hrect(y0=70, y1=100, fillcolor="rgba(46,160,67,0.05)", line_width=0,
                                annotation_text="Good zone (70+)", annotation_font_color="rgba(78,207,94,0.6)",
                                annotation_font_size=13)
            fig_score.update_layout(
                title=dict(text="Green score over time — higher is better", font=dict(color="#c0b8a8", size=15, family="Inter")),
                paper_bgcolor="#0f0f0f", plot_bgcolor="#0f0f0f",
                xaxis=dict(tickfont=dict(color="#a09880", size=13), gridcolor="#181818"),
                yaxis=dict(tickfont=dict(color="#a09880", size=13), gridcolor="#181818",
                           range=[0, 105], title=dict(text="Score / 100", font=dict(color="#8a8070", size=13))),
                margin=dict(t=52, b=28, l=16, r=16), height=300, showlegend=False
            )
            st.plotly_chart(fig_score, use_container_width=True)

            if len(hs) >= 2:
                first_val  = hs.iloc[0]["predicted"]
                last_val   = hs.iloc[-1]["predicted"]
                change     = last_val - first_val
                change_pct = (change / first_val) * 100 if first_val > 0 else 0
                trend_color = "#4ecf5e" if change < 0 else "#e06060"
                trend_word  = "improved" if change < 0 else "increased"
                st.markdown(f"""
                <div class="card" style='display:flex; gap:22px; align-items:center;'>
                    <div style='min-width:4px; height:48px; background:{trend_color}; border-radius:2px;'></div>
                    <div>
                        <div style='font-size:0.82rem; color:#8a7a60; letter-spacing:0.11em; text-transform:uppercase; margin-bottom:8px; font-weight:600;'>Your Trend</div>
                        <div style='font-size:0.98rem; color:#d0c8b8; line-height:1.75;'>
                            Since your first reading, your carbon footprint has <strong style='color:{trend_color};'>{trend_word} by {abs(change_pct):.0f}%</strong>.
                            Your latest reading is <strong style='color:#C9A84C;'>{last_val:.0f} kg</strong> CO₂ per month.
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            with st.expander("View full history table"):
                d = history_df[["date", "predicted", "score", "transport", "diet", "distance", "screen_time"]].copy()
                d.columns = ["Date", "Carbon (kg)", "Score", "Travel Mode", "Diet", "Distance (km)", "Screen (hrs/day)"]
                st.dataframe(d, use_container_width=True)

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            if st.button("Clear History"):
                conn = sqlite3.connect("ecotrack_history.db")
                conn.execute("DELETE FROM history"); conn.commit(); conn.close()
                st.rerun()

    # ══════════════════════════════════════════════
    # TAB 3 — AI ADVISOR
    # ══════════════════════════════════════════════
    with tab3:
        st.markdown("""
        <div style='font-family:Cormorant Garamond,serif; font-size:1.7rem; color:#f0e8d8; font-weight:600; margin-bottom:8px;'>AI Carbon Advisor</div>
        <div style='font-size:0.98rem; color:#9a9280; margin-bottom:28px;'>
            Four specialised AI agents analyse your carbon profile, search the web for green alternatives,
            and generate a personalised 7-day reduction roadmap — built specifically around your habits.
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class='card' style='margin-bottom:24px;'>
            <div style='font-size:0.82rem; color:#8a7a60; letter-spacing:0.11em; text-transform:uppercase; font-weight:700; margin-bottom:18px;'>How the Pipeline Works</div>
            <div style='display:flex; align-items:center; flex-wrap:wrap; gap:8px;'>
                <div class='agent-box'>
                    <div class='agent-num'>Agent 1</div>
                    <div class='agent-name'>Data Ingestion</div>
                    <div class='agent-desc'>Reads your profile</div>
                </div>
                <div style='font-size:1.4rem; color:rgba(201,168,76,0.35);'>→</div>
                <div class='agent-box'>
                    <div class='agent-num'>Agent 2</div>
                    <div class='agent-name'>LLM Reasoner</div>
                    <div class='agent-desc'>Finds top drivers</div>
                </div>
                <div style='font-size:1.4rem; color:rgba(201,168,76,0.35);'>→</div>
                <div class='agent-box'>
                    <div class='agent-num'>Agent 3</div>
                    <div class='agent-name'>Web Search</div>
                    <div class='agent-desc'>Finds live solutions</div>
                </div>
                <div style='font-size:1.4rem; color:rgba(201,168,76,0.35);'>→</div>
                <div class='agent-box'>
                    <div class='agent-num'>Agent 4</div>
                    <div class='agent-name'>Action Planner</div>
                    <div class='agent-desc'>Builds your roadmap</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        if "advisor_data" not in st.session_state:
            st.markdown("""
            <div class="af" style='text-align:center; padding:80px 48px; border:1px solid rgba(201,168,76,0.08); border-radius:12px; background:#0a0a0a;'>
                <div style='font-family:Cormorant Garamond,serif; font-size:1.5rem; color:#e0d8c8; margin-bottom:14px; font-weight:600;'>Run your carbon calculation first</div>
                <div style='font-size:0.98rem; color:#8a8070; max-width:380px; margin:0 auto; line-height:1.9;'>
                    Go to <strong style='color:#C9A84C;'>My Results</strong>, fill in your details and click
                    <strong style='color:#C9A84C;'>Calculate My Footprint</strong>.<br>
                    Then come back here to get your AI-powered roadmap.
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='font-size:0.98rem; color:#9a9280; margin-bottom:20px;'>
                Your carbon profile is ready. Click below to run all four agents and
                generate your personalised 7-day reduction roadmap.
            </div>""", unsafe_allow_html=True)

            col_btn, col_empty = st.columns([1, 2])
            with col_btn:
                run_advisor = st.button("Generate My AI Roadmap", use_container_width=True)

            if run_advisor:
                with st.spinner(""):
                    try:
                        st.markdown("""
                        <div class='card' style='text-align:center; padding:40px;'>
                            <div style='font-family:Cormorant Garamond,serif; font-size:1.5rem; color:#C9A84C; margin-bottom:16px;'>Running AI Agents</div>
                            <div style='font-size:0.98rem; color:#9a9280; line-height:2;'>
                                <strong style='color:#e0d8c8;'>Agent 1</strong> — Reading your carbon profile...<br>
                                <strong style='color:#e0d8c8;'>Agent 2</strong> — Analysing your top emission drivers...<br>
                                <strong style='color:#e0d8c8;'>Agent 3</strong> — Searching the web for green alternatives...<br>
                                <strong style='color:#e0d8c8;'>Agent 4</strong> — Building your 7-day roadmap...<br><br>
                                <span style='color:#6a6050;'>This takes about 15–20 seconds.</span>
                            </div>
                        </div>""", unsafe_allow_html=True)
                        result = run_pipeline(st.session_state["advisor_data"])
                        st.session_state["advisor_result"] = result
                        st.rerun()
                    except Exception as e:
                        st.error(f"Pipeline error: {str(e)}")
                        st.markdown("""
                        <div class='card-flat' style='margin-top:12px;'>
                            <div style='font-size:0.94rem; color:#9a7070;'>
                                Common fixes: check your <strong style='color:#C9A84C;'>GROQ_API_KEY</strong> in your .env file,
                                make sure you have an internet connection, and try again.
                            </div>
                        </div>""", unsafe_allow_html=True)

            if "advisor_result" in st.session_state:
                result      = st.session_state["advisor_result"]
                action_plan = result.get("action_plan", {})
                days        = action_plan.get("days", [])
                summary     = action_plan.get("summary", "")
                drivers     = result.get("reasoning_output", {}).get("drivers", [])
                search_res  = result.get("search_output", {}).get("search_results", [])

                if result.get("error"):
                    st.error(f"An agent encountered an error: {result['error']}")

                if drivers:
                    st.markdown("<div class='sec-lbl'>Your Top Emission Drivers</div>", unsafe_allow_html=True)
                    for i, driver in enumerate(drivers):
                        st.markdown(f"""
                        <div class="card-flat" style='animation:fadeUp 0.5s {i*0.1:.1f}s ease both; display:flex; gap:20px; align-items:flex-start;'>
                            <div style='font-family:Cormorant Garamond,serif; font-size:1.1rem; color:rgba(201,168,76,0.3); font-weight:600; min-width:26px; padding-top:2px;'>{i+1:02d}</div>
                            <div>
                                <div style='font-size:0.96rem; font-weight:600; color:#e0d8c8; margin-bottom:7px;'>{driver.get('name','')}</div>
                                <div class='card-body' style='margin-bottom:8px;'>{driver.get('why','')}</div>
                                <div style='font-size:0.92rem; color:#C9A84C; font-weight:500;'>→ {driver.get('action','')}</div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                if search_res:
                    st.markdown("<div class='sec-lbl'>Live Research — What the Web Says</div>", unsafe_allow_html=True)
                    for i, s in enumerate(search_res):
                        sources_html = ""
                        for src in s.get("raw_results", []):
                            if src.get("url"):
                                sources_html += f"""<a href='{src['url']}' target='_blank'
                                style='display:block; font-size:0.86rem; color:#6a7a8a;
                                margin-top:6px; text-decoration:none;'>↗ {src['title'][:65]}...</a>"""
                        st.markdown(f"""
                        <div class="card-flat" style='animation:fadeUp 0.5s {i*0.1:.1f}s ease both;'>
                            <div style='font-size:0.82rem; color:#C9A84C; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px;'>{s.get('driver','')}</div>
                            <div class='card-body' style='margin-bottom:10px;'>{s.get('summary','')}</div>
                            {sources_html}
                        </div>""", unsafe_allow_html=True)

                if days:
                    st.markdown("<div class='sec-lbl'>Your Personalised 7-Day Roadmap</div>", unsafe_allow_html=True)
                    day_colors = ["#C9A84C","#4ecf5e","#5a9acd","#9a7acd","#cd6a8a","#4aaa6a","#C9A84C"]
                    for i, day in enumerate(days[:7]):
                        color = day_colors[i % len(day_colors)]
                        st.markdown(f"""
                        <div class="card" style='animation:fadeUp 0.5s {i*0.1:.1f}s ease both;'>
                            <div style='display:flex; gap:22px; align-items:flex-start;'>
                                <div style='text-align:center; min-width:54px;'>
                                    <div style='font-family:Cormorant Garamond,serif; font-size:1.8rem; font-weight:600; color:{color}; line-height:1;'>{i+1}</div>
                                    <div style='font-size:0.74rem; color:#5a5040; text-transform:uppercase; letter-spacing:0.08em; margin-top:2px;'>Day</div>
                                </div>
                                <div style='flex:1; border-left:1px solid rgba(201,168,76,0.1); padding-left:22px;'>
                                    <div style='font-size:0.98rem; font-weight:600; color:#e0d8c8; margin-bottom:9px;'>{day.get('title','')}</div>
                                    <div class='card-body' style='margin-bottom:10px;'><strong style='color:#C9A84C;'>Task:</strong> {day.get('task','')}</div>
                                    <div style='font-size:0.92rem; color:#6a8a6a;'><strong style='color:#4ecf5e;'>Impact:</strong> {day.get('impact','')}</div>
                                </div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                if summary:
                    st.markdown(f"""
                    <div class="card-gold" style='margin-top:8px;'>
                        <div style='font-size:0.82rem; color:#C9A84C; letter-spacing:0.12em; text-transform:uppercase; font-weight:700; margin-bottom:12px;'>Your Week Ahead</div>
                        <div style='font-family:Cormorant Garamond,serif; font-size:1.25rem; color:#f0e8d8; line-height:1.75; font-style:italic;'>"{summary}"</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("Regenerate Roadmap"):
                    del st.session_state["advisor_result"]
                    st.rerun()

    # ══════════════════════════════════════════════
    # TAB 4 — ABOUT
    # ══════════════════════════════════════════════
    with tab4:
        st.markdown("<div style='font-family:Cormorant Garamond,serif; font-size:1.7rem; color:#f0e8d8; font-weight:600; margin-bottom:28px;'>About EcoTrack</div>", unsafe_allow_html=True)
        for i, (title, body) in enumerate([
            ("What is EcoTrack?",
             "EcoTrack is a free, open-source carbon footprint calculator built specifically for India. It takes your real daily habits — commute, diet, screen time — and tells you exactly how much CO₂ you produce each month, where it's coming from, and the specific changes that will make the biggest real-world difference."),
            ("Why is it built for India?",
             "Most carbon calculators are designed for Western contexts using assumptions about energy grids, diet patterns and transport infrastructure that simply do not apply here. EcoTrack is calibrated for Indian conditions — urban commute patterns, the coal-heavy electricity grid, local dietary norms and the national emissions average — so your results reflect actual daily reality, not a global approximation."),
            ("What is the AI Advisor?",
             "The AI Advisor is a four-agent pipeline built with LangGraph and powered by Groq. After your carbon calculation, Agent 1 reads your profile, Agent 2 uses an LLM to identify your top emission drivers, Agent 3 searches the web live for green alternatives relevant to your habits, and Agent 4 generates a personalised 7-day carbon reduction roadmap — all automatically."),
            ("Is my data private?",
             "Completely. Everything you enter is processed locally and stored only in a file on your own device. Nothing is transmitted, collected or shared with any third party. No account is ever required — not now, not in the future."),
            ("Open Source & Roadmap",
             "EcoTrack is fully open source under the MIT License. The complete codebase is on GitHub for anyone to inspect, fork or contribute to. Features planned include state-level carbon comparison, household multi-user support, and integration with public emissions datasets from MOEFCC and IEA India."),
        ]):
            st.markdown(f"""
            <div class="card" style='animation:fadeUp 0.5s {i*0.12:.2f}s ease both; display:flex; gap:22px; align-items:flex-start;'>
                <div style='font-family:Cormorant Garamond,serif; font-size:1rem; color:rgba(201,168,76,0.25); font-weight:600; min-width:28px; padding-top:3px;'>{i+1:02d}</div>
                <div>
                    <div style='font-size:0.98rem; font-weight:600; color:#e0d8c8; margin-bottom:10px;'>{title}</div>
                    <div class="card-body">{body}</div>
                </div>
            </div>""", unsafe_allow_html=True)