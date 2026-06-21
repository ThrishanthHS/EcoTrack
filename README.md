# EcoTrack — Personal Carbon Intelligence Platform
[![Live App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://thrishanthhs-ecotrack.streamlit.app)
> Know your impact. Change your habits. Track your progress.

EcoTrack is a free, open-source carbon footprint calculator built specifically 
for India. It takes your real daily habits — how you commute, what you eat, how 
much time you spend on screens — and tells you exactly how much CO₂ you produce 
each month, where it is coming from, and the specific changes that will make the 
biggest real-world difference.

No sign-up. No data collection. Everything runs locally on your device.

---

## Why EcoTrack Exists

Most carbon calculators online are built for Western users. They assume energy 
grids, transport infrastructure, and dietary patterns that simply do not reflect 
life in India. EcoTrack is calibrated for Indian conditions — urban commute 
patterns, the coal-heavy electricity grid, local dietary norms, and a national 
average of approximately 1,500 kg CO₂ per person per month.

The result is a tool that gives you accurate, relevant, and actionable output — 
not a generic approximation that does not apply to your life.

---

## What It Does

### Carbon Prediction
Predicts your monthly carbon footprint using a Random Forest model trained on 
7,000+ real-world records. You input your commute mode and distance, diet type, 
screen time, grocery spend, and home energy habits — and get your result in under 
two minutes.

### Emission Breakdown
See exactly where your carbon comes from across six categories — commute and 
travel, food and diet, TV and devices, internet usage, groceries, and other home 
emissions — visualised as an interactive pie chart with hover details.

### Green Score
A 0–100 score that benchmarks your footprint against the Indian national average. 
Excellent, Good, Moderate, or High — with a clear animated gauge and a plain 
explanation of what your number means in practice.

### Carbon Personality
Based on your habits, EcoTrack assigns you a carbon personality — The Daily 
Driver, The Digital Resident, The Conscious Commuter, or The Balanced Urbanite — 
with a personalised explanation of your biggest impact areas.

### Top Actions — Ranked by Impact
EcoTrack calculates exactly how much carbon you would save by switching to public 
transport, working from home one day a week, or reducing meat consumption — and 
ranks them by real monthly savings, not guesswork.

### AI Advisor — Four-Agent Pipeline
After your prediction, the AI Advisor tab runs a four-agent system powered by 
LangGraph and Groq that goes further than static suggestions:

- **Agent 1 — Data Ingestion:** Reads your carbon breakdown directly from the 
  app session. No re-entry required.
- **Agent 2 — LLM Reasoner:** Uses Groq (llama-3.3-70b-versatile) to analyse 
  your emission profile and identify the top three leverage points where a 
  change will have the highest impact.
- **Agent 3 — Web Search Agent:** Searches the web live using DuckDuckGo for 
  green alternatives relevant to your specific habits and location — public 
  transport options, energy-saving schemes, dietary swap guides.
- **Agent 4 — Action Planner:** Generates a personalised 7-day carbon reduction 
  roadmap with specific, actionable daily tasks based on your full profile and 
  the live research findings.

### Progress Tracking
Every result is saved automatically to a local SQLite database. Return over time 
to see whether your habits are genuinely improving — with an area chart of monthly 
emissions and a colour-coded green score timeline.

---

## How the Agentic Pipeline Works

Your Carbon Profile

│

▼

┌─────────────────┐

│   Agent 1       │  Reads session data → structures your carbon profile

│   Data Ingestion│  into a clean dictionary for downstream agents

└────────┬────────┘

│

▼

┌─────────────────┐

│   Agent 2       │  Sends profile to Groq LLM → identifies your top 3

│   LLM Reasoner  │  emission drivers with plain explanations and actions

└────────┬────────┘

│

▼

┌─────────────────┐

│   Agent 3       │  Builds targeted search queries per driver → fetches

│   Web Search    │  live results via DuckDuckGo → Groq summarises findings

└────────┬────────┘

│

▼

┌─────────────────┐

│   Agent 4       │  Takes everything above → generates a personalised

│   Action Planner│  7-day roadmap with daily tasks and impact explanations

└────────┬────────┘

│

▼

Your 7-Day Carbon

Reduction Roadmap


All four agents are orchestrated using **LangGraph** with conditional error 
checking between each step. If any agent fails, the pipeline stops cleanly and 
surfaces the error rather than producing broken output.

---

## Tech Stack

| Layer                | Technology                          |
|----------------------|-------------------------------------|
| Frontend             | Streamlit                           |
| ML Model             | Random Forest (scikit-learn, joblib)|
| Agent Orchestration  | LangGraph                           |
| LLM                  | Groq — llama-3.3-70b-versatile      |
| Web Search           | DuckDuckGo Search (ddgs)            |
| Visualisation        | Plotly                              |
| Database             | SQLite                              |
| Language             | Python 3.10+                        |

---

## Project Structure

```
EcoTrack/
│
├── app.py                    # Main Streamlit application — all 4 tabs
│
├── agents/
│   ├── ingestion.py          # Agent 1 — Data Ingestion
│   ├── reasoner.py           # Agent 2 — LLM Reasoner (Groq)
│   ├── web_search.py         # Agent 3 — Web Search Agent (DuckDuckGo)
│   ├── action_planner.py     # Agent 4 — 7-Day Action Planner
│   └── pipeline.py           # LangGraph orchestration pipeline
│
├── frontend/
│   ├── style.css             # Design tokens and component styles
│   └── background.jpeg       # UI background asset
│
├── Ecotrack_rf_model.pkl     # Trained Random Forest model
├── ecotrack_history.db       # Auto-generated local history (SQLite)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
└── README.md                 # This file
```
---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ThrishanthHS/EcoTrack.git
cd EcoTrack
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your environment variables

Copy the example file and add your API keys:

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com) — 
no credit card required. The free tier is more than enough to run EcoTrack.

### 4. Run the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## How to Use

1. Click **Calculate My Carbon Footprint** on the landing page
2. Fill in your details on the left sidebar — commute mode and distance, 
   diet type, screen time, grocery spend, and home energy habits
3. Click **Calculate My Footprint** to get your instant result
4. View your emission breakdown, green score, carbon personality, and 
   top ranked actions in the **My Results** tab
5. Open the **AI Advisor** tab and click **Generate My AI Roadmap** to 
   run all four agents and get your personalised 7-day plan
6. Return regularly and recalculate — your history is saved automatically 
   and tracked in the **My Progress** tab

---

## Key Findings the Model Surfaces

- Users on private vehicles with over 1,000 km of monthly distance 
  consistently show the highest footprints regardless of other habits
- Diet type is the second strongest predictor — omnivore users average 
  38% higher food-related emissions than vegetarians
- Screen time above 7 hours per day adds a meaningful and often overlooked 
  home energy load, especially relevant given India's coal-heavy grid
- Switching from private to public transport alone reduces total footprint 
  by 20–35% for most urban users

---

## Environment Variables

| Variable        | Required | Description                              |
|-----------------|----------|------------------------------------------|
| GROQ_API_KEY    | Yes      | Your Groq API key for LLM inference      |

---

## Roadmap

- [ ] State-level carbon comparison across India
- [ ] Household multi-user mode
- [ ] Integration with MOEFCC and IEA India public emissions datasets
- [ ] Export results as a downloadable PDF report
- [ ] Mobile-responsive UI
- [ ] Streamlit Community Cloud deployment

---

## Contributing

Contributions are welcome and appreciated. If you find a bug, have a feature 
idea, or want to improve the model, the agents, or the UI — open an issue or 
submit a pull request.

Please keep your code clean, well-commented, and consistent with the existing 
structure. If you are adding a new agent, follow the pattern in the existing 
agent files and wire it into `pipeline.py`.

---

## Privacy

Everything you enter stays on your device. EcoTrack stores your history in a 
local SQLite file (`ecotrack_history.db`) and nowhere else. No data is ever 
transmitted, logged, or shared — with anyone, ever.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for 
full details.

---

## Author

Built by [Thrishanth H S](https://github.com/ThrishanthHS)

B.Tech Artificial Intelligence & Machine Learning — JNNCE, Bengaluru  
Joint Secretary, ACM Student Chapter — JNNCE  
LinkedIn: [thrishanth-hs21](https://linkedin.com/in/thrishanth-hs21)  
GitHub: [ThrishanthHS](https://github.com/ThrishanthHS)

---

## Acknowledgements

- [Groq](https://groq.com) — for blazing fast LLM inference on the free tier
- [LangGraph](https://github.com/langchain-ai/langgraph) — for the agent 
  orchestration framework
- [Streamlit](https://streamlit.io) — for making it possible to build a 
  full-stack data app in pure Python
- [DuckDuckGo Search](https://pypi.org/project/ddgs) — for privacy-respecting 
  live web search

---

*EcoTrack is a portfolio project built to demonstrate end-to-end ML engineering 
— from data and modelling to agentic AI systems and production-ready UI. If you 
find it useful, give it a star on GitHub.*