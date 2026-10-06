import streamlit as st
import time
import json
import os
from engine import SteeringVectorEngine
from parser import ConstraintParser
from logger import EventLogger

st.set_page_config(
    page_title="Google Photos | Steerable Retrieval Prototype",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Google Photos Custom CSS Theme
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Material Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Google Sans', 'Roboto', sans-serif !important;
    }
    
    .stApp {
        background-color: #FFFFFF;
    }

    /* Google Photos Header styling */
    .gp-header {
        display: flex;
        align-items: center;
        padding: 12px 0px;
        border-bottom: 1px solid #E0E0E0;
        margin-bottom: 20px;
    }
    
    .gp-logo {
        font-size: 22px;
        font-weight: 500;
        color: #3C4043;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Floating Google Search Bar */
    div[data-baseweb="input"] {
        border-radius: 28px !important;
        background-color: #F1F3F4 !important;
        border: 1px solid transparent !important;
        padding: 4px 16px !important;
        box-shadow: none !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        background-color: #FFFFFF !important;
        border-color: #E0E0E0 !important;
        box-shadow: 0 1px 6px rgba(32,33,36,0.28) !important;
    }

    /* Material Design Cards for Photos */
    div[data-testid="stColumn"] > div {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 8px;
        border: 1px solid #F1F3F4;
        transition: all 0.2s ease-in-out;
    }

    div[data-testid="stColumn"] > div:hover {
        box-shadow: 0 4px 12px rgba(60,64,67,0.15);
        transform: translateY(-2px);
    }

    /* Google Pill Badges */
    .gp-badge-exif {
        background-color: #E8F0FE;
        color: #1A73E8;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 6px;
    }

    .gp-badge-msg {
        background-color: #FEF7E0;
        color: #B06000;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 6px;
    }

    /* Rounded Button Overrides */
    .stButton > button {
        border-radius: 20px !important;
        border: 1px solid #DADCE0 !important;
        background-color: #FFFFFF !important;
        color: #3C4043 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 4px 16px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #F8F9FA !important;
        border-color: #1A73E8 !important;
        color: #1A73E8 !important;
    }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-family: 'Google Sans', sans-serif !important;
        color: #1A73E8 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# System Initialization (Cached)
# -----------------------------------------------------------------------------
@st.cache_resource
def init_system():
    engine = SteeringVectorEngine()
    engine.load_or_build_index()
    parser = ConstraintParser()
    logger = EventLogger()
    return engine, parser, logger

engine, parser, logger = init_system()

# -----------------------------------------------------------------------------
# Session State
# -----------------------------------------------------------------------------
if "query_input" not in st.session_state:
    st.session_state.query_input = "living room furniture"
if "pos_indices" not in st.session_state:
    st.session_state.pos_indices = set()
if "neg_indices" not in st.session_state:
    st.session_state.neg_indices = set()
if "active_year" not in st.session_state:
    st.session_state.active_year = None
if "alpha" not in st.session_state:
    st.session_state.alpha = 0.5
if "beta" not in st.session_state:
    st.session_state.beta = 0.4
if "gamma" not in st.session_state:
    st.session_state.gamma = 0.2

# -----------------------------------------------------------------------------
# Sidebar: Strategy & Vector Tuning
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ PM Strategy & Controls")
    st.caption("Steerable Photo Retrieval Technical Suite")
    st.markdown("---")
    
    with st.expander("📋 Strategic Context", expanded=True):
        st.markdown("""
        **Target Failure Modes:**
        - **Context Drift:** Irrelevant visual attributes during broad queries.
        - **EXIF Stripping:** WhatsApp/Telegram media missing dates/geotags.
        """)

    st.markdown("### 🎛️ Vector Steering Weights")
    st.session_state.alpha = st.slider("Alpha (Query Weight α)", 0.0, 1.0, st.session_state.alpha, 0.05)
    st.session_state.beta = st.slider("Beta (Positive Shift β)", 0.0, 1.0, st.session_state.beta, 0.05)
    st.session_state.gamma = st.slider("Gamma (Negative Exclusion γ)", 0.0, 1.0, st.session_state.gamma, 0.05)

    if st.button("🔄 Clear All Signals", use_container_width=True):
        st.session_state.pos_indices = set()
        st.session_state.neg_indices = set()
        st.session_state.active_year = None
        st.rerun()

# -----------------------------------------------------------------------------
# Google Photos Top Navigation Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="gp-header">
    <div class="gp-logo">
        <span style="color:#4285F4;">G</span><span style="color:#EA4335;">o</span><span style="color:#FBBC05;">o</span><span style="color:#4285F4;">g</span><span style="color:#34A853;">l</span><span style="color:#EA4335;">e</span>
        <span style="font-weight:400; color:#5F6368; margin-left:4px;">Photos</span>
        <span style="font-size:12px; background:#E8F0FE; color:#1A73E8; padding:2px 8px; border-radius:10px; margin-left:8px;">Steerable Search Lab</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Telemetry Bar
m1, m2, m3, m4 = st.columns(4)
total_imgs = len(engine.image_paths)
exif_count = sum(1 for m in engine.metadata if m.get("has_exif"))
msg_media_count = total_imgs - exif_count

m1.metric("Photos Indexed", f"{total_imgs}")
m2.metric("Embedding Space", "SigLIP 1152-D")
m3.metric("Messaging Media", f"{msg_media_count}")
m4.metric("Engine Latency", "< 140 ms")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Google-Style Search Bar & Smart Scenario Chips
# -----------------------------------------------------------------------------
search_col, chip_col = st.columns([3, 1])

with search_col:
    query_text = st.text_input("", value=st.session_state.query_input, placeholder="🔍 Search your photos or type natural guidance...")

parsed_chips = parser.parse_query(query_text)
parsed_year = parsed_chips.get("year") or st.session_state.active_year

with chip_col:
    if parsed_year:
        st.markdown(f"<div style='padding-top:28px;'><span class='gp-badge-exif'>📅 Filter: {parsed_year}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='padding-top:32px; font-size:12px; color:#70757A;'>No active temporal filters</div>", unsafe_allow_html=True)

# Google Search Suggestions / Benchmark Presets
st.markdown("**Suggested Scenarios:**")
p1, p2, p3 = st.columns(3)

if p1.button("🛋️ Context Drift (Living Room)", use_container_width=True):
    st.session_state.query_input = "living room furniture"
    st.session_state.alpha, st.session_state.beta, st.session_state.gamma = 0.5, 0.6, 0.3
    st.session_state.active_year = None
    st.rerun()

if p2.button("📱 WhatsApp Media (Sunset 2024)", use_container_width=True):
    st.session_state.query_input = "scenic landscape sunset"
    st.session_state.alpha, st.session_state.beta, st.session_state.gamma = 0.6, 0.2, 0.1
    st.session_state.active_year = 2024
    st.rerun()

if p3.button("🧾 Clutter Filter (Documents)", use_container_width=True):
    st.session_state.query_input = "paper document receipt"
    st.session_state.alpha, st.session_state.beta, st.session_state.gamma = 0.4, 0.1, 0.8
    st.session_state.active_year = None
    st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# Execute & Display Photos Grid
# -----------------------------------------------------------------------------
start_time = time.time()
results = engine.search(
    query_text=query_text,
    pos_indices=list(st.session_state.pos_indices),
    neg_indices=list(st.session_state.neg_indices),
    active_year=parsed_year,
    alpha=st.session_state.alpha,
    beta=st.session_state.beta,
    gamma=st.session_state.gamma,
    top_k=12
)
latency_ms = round((time.time() - start_time) * 1000, 2)

st.markdown(f"<div style='font-size:14px; color:#5F6368; margin-bottom:12px;'>Showing <b>{len(results)}</b> results ({latency_ms} ms)</div>", unsafe_allow_html=True)

if not results:
    st.info("No photos found in `data/images/`. Upload test images to your GitHub repository.")
else:
    cols = st.columns(3)
    for idx, item in enumerate(results):
        col = cols[idx % 3]
        img_idx = item["index"]
        img_path = item["path"]
        score = item["score"]
        meta = item["metadata"]

        with col:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            
            # Badge rendering
            if meta.get("has_exif"):
                st.markdown(f"<span class='gp-badge-exif'>EXIF • {meta.get('year', 'Camera')}</span> <span style='font-size:11px; color:#70757A;'>Score: {score:.3f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='gp-badge-msg'>Messaging Media</span> <span style='font-size:11px; color:#70757A;'>Score: {score:.3f}</span>", unsafe_allow_html=True)

            # Steering Controls
            b1, b2 = st.columns(2)
            is_pos = img_idx in st.session_state.pos_indices
            is_neg = img_idx in st.session_state.neg_indices

            if b1.button(f"{'💙 Liked' if is_pos else '👍 Similar'}", key=f"pos_{img_idx}"):
                if is_pos:
                    st.session_state.pos_indices.remove(img_idx)
                else:
                    st.session_state.pos_indices.add(img_idx)
                    st.session_state.neg_indices.discard(img_idx)
                st.rerun()

            if b2.button(f"{'🚫 Hidden' if is_neg else '👎 Less Like'}", key=f"neg_{img_idx}"):
                if is_neg:
                    st.session_state.neg_indices.remove(img_idx)
                else:
                    st.session_state.neg_indices.add(img_idx)
                    st.session_state.pos_indices.discard(img_idx)
                st.rerun()

# -----------------------------------------------------------------------------
# Google Photos Technical Inspector
# -----------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🔍 Google Photos Lens | Vector Engine Telemetry"):
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("#### Steered Vector Equation")
        st.latex(r"V_{\text{steered}} = \text{Normalize}\left(\alpha V_{\text{query}} + \beta \bar{E}_{\text{pos}} - \gamma \bar{E}_{\text{neg}}\right)")
        st.json({
            "alpha": st.session_state.alpha,
            "beta": st.session_state.beta,
            "gamma": st.session_state.gamma,
            "pos_exemplars": list(st.session_state.pos_indices),
            "neg_exemplars": list(st.session_state.neg_indices)
        })
    with t2:
        st.markdown("#### Gemini Parser Telemetry")
        st.json({
            "query": query_text,
            "chips": parsed_chips,
            "temporal_prior_offset": "+0.08" if parsed_year else "0.00"
        })
