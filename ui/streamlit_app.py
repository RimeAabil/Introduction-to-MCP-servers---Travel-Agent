# ui/streamlit_app.py
# Run with: streamlit run app_streamlit.py

import streamlit as st
import requests
from agent.runner import run_travel_agent

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Travel Planner AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@300;400;500&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Hero title */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.25rem;
}
.hero-sub {
    color: #888;
    font-size: 0.95rem;
    font-weight: 300;
    letter-spacing: 0.05em;
    margin-bottom: 2rem;
}

/* Example cards */
.example-card {
    background: #f8f7f4;
    border: 1.5px solid #e8e4dc;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    font-size: 0.85rem;
    color: #444;
    cursor: pointer;
    transition: all 0.2s;
    min-height: 70px;
    display: flex;
    align-items: center;
}
.example-card:hover {
    border-color: #c9956c;
    background: #fdf6ef;
    color: #222;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1a1a2e !important;
}
[data-testid="stSidebar"] * {
    color: #e8e4dc !important;
}
[data-testid="stSidebar"] .stSuccess {
    background: rgba(52, 199, 89, 0.15) !important;
    border: 1px solid rgba(52, 199, 89, 0.3) !important;
    color: #34c759 !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stError {
    background: rgba(255, 59, 48, 0.15) !important;
    border: 1px solid rgba(255, 59, 48, 0.3) !important;
    color: #ff6b6b !important;
    border-radius: 8px;
}

/* Input area */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 2px solid #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #c9956c !important;
    box-shadow: 0 0 0 3px rgba(201,149,108,0.15) !important;
}

/* Plan button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a1a2e, #0f3460) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    padding: 0.65rem 2rem !important;
    letter-spacing: 0.03em !important;
    transition: opacity 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.85 !important;
}

/* Travel plan card */
.plan-card {
    background: linear-gradient(145deg, #fdfcfa, #f8f6f1);
    border: 1.5px solid #e8e4dc;
    border-radius: 16px;
    padding: 2rem 2.2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}
.plan-card h1, .plan-card h2, .plan-card h3 {
    font-family: 'Playfair Display', serif !important;
    color: #1a1a2e !important;
}
.plan-card p, .plan-card li {
    color: #444 !important;
    line-height: 1.75 !important;
}
.plan-card strong { color: #0f3460 !important; }

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #15803d;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.82rem;
    font-weight: 500;
    margin-bottom: 1rem;
}

/* Thinking expander */
.streamlit-expanderHeader {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    color: #888 !important;
}

/* Section label */
.section-label {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #aaa;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar — server status ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛠 MCP Servers")
    st.markdown("<p style='font-size:0.82rem; opacity:0.6;'>Tools called automatically by the agent</p>", unsafe_allow_html=True)

    tools_status = {
        "🧮 Budget Estimator":    "http://localhost:3001/health",
        "🌤 Weather Checker":     "http://localhost:3002/health",
        "💱 Currency Converter":  "http://localhost:3003/health",
        "🗺 Destination Search":  "http://localhost:3004/health",
        "➗ Calculator":          "http://localhost:3005/health",
    }

    all_online = True
    headers = {"Accept": "application/json, text/event-stream"}
    for tool_name, url in tools_status.items():
        r = None
        try:
            r = requests.get(url, timeout=2, stream=True, headers=headers)
            ok = r.status_code == 200
        except Exception:
            ok = False
        finally:
            if r is not None:
                try: r.close()
                except: pass

        if ok:
            st.success(f"{tool_name} ✅")
        else:
            st.error(f"{tool_name} ❌ offline")
            all_online = False

    st.divider()
    st.markdown("**Model:** `mistral:latest`")
    st.markdown("**Framework:** LangChain ReAct")
    st.divider()
    st.markdown("**Start servers:**")
    st.code("./start_servers.sh", language="bash")
    st.markdown("**Pull model:**")
    st.code("ollama pull mistral", language="bash")

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Plan your next<br>adventure ✈️</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Powered by Mistral · LangChain ReAct · MCP Tools</div>', unsafe_allow_html=True)

# ── Example prompts ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Quick examples</div>', unsafe_allow_html=True)
examples = [
    ("🏖", "Barcelona · 5 days · Mid-range", "Plan a 5-day mid-range trip to Barcelona in July. Show costs in EUR."),
    ("🗼", "Paris · 3 days · Budget", "I want a budget-friendly 3-day trip to Paris in December. Convert total to MAD."),
    ("🗾", "Tokyo · 7 days · Luxury", "Plan a luxury 7-day trip to Tokyo in August. What's the weather like?"),
]

col1, col2, col3 = st.columns(3)
selected_example = None
for col, (icon, label, prompt) in zip([col1, col2, col3], examples):
    with col:
        if st.button(f"{icon}  {label}", use_container_width=True, key=label):
            selected_example = prompt

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
user_input = st.text_area(
    "Describe your trip",
    value=selected_example or st.session_state.get("last_input", ""),
    height=110,
    placeholder="e.g. Plan a 5-day trip to Barcelona with a mid-range budget in July. Show costs in EUR.",
    label_visibility="collapsed",
)

run_btn = st.button("✈️  Generate Travel Plan", type="primary", use_container_width=True)

# ── Agent run ──────────────────────────────────────────────────────────────────
if run_btn:
    if not user_input.strip():
        st.warning("Please describe your trip first.")
    else:
        st.session_state["last_input"] = user_input
        st.markdown("---")

        with st.spinner("🤔 Agent is thinking and calling tools… this may take a minute."):
            plan = run_travel_agent(user_input)

        # ── Render result ──────────────────────────────────────────────────────
        if plan and not plan.startswith("Error") and "⚠️" not in plan:
            st.markdown('<div class="status-badge">✅ Plan ready</div>', unsafe_allow_html=True)
            st.markdown('<div class="plan-card">', unsafe_allow_html=True)
            st.markdown(plan)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col_dl, _ = st.columns([1, 3])
            with col_dl:
                st.download_button(
                    "⬇️  Download plan (.txt)",
                    data=plan,
                    file_name="travel_plan.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
        else:
            st.error(plan or "Something went wrong. Check that your MCP servers are running.")

        # ── Agent log (collapsed by default) ──────────────────────────────────
        with st.expander("🔍 View agent reasoning log (terminal output)", expanded=False):
            st.info(
                "The full Thought → Action → Observation chain is printed in the "
                "terminal where you launched Streamlit. Check it there for the live ReAct loop."
            )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#bbb; font-size:0.78rem;'>"
    "Agentic loop · ReAct framework · Local inference via Ollama"
    "</p>",
    unsafe_allow_html=True,
)