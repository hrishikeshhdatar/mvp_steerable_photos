import streamlit as st
import time
import os
from engine import SteeringVectorEngine
from parser import ConstraintParser
from logger import EventLogger

st.set_page_config(
    page_title="Google Photos | Search",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Google Photos Authentic Design System
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Google Sans', 'Roboto', sans-serif !important;
        background-color: #F0F4F9 !important;
        color: #1F1F1F !important;
    }

    div[data-testid="stAppViewContainer"] {
        background-color: #F0F4F9 !important;
    }

    /* Hide Sidebar Completely for Clean Consumer UI */
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Header */
    .gp-brand-logo {
        font-size: 24px;
        font-weight: 500;
        color: #1F1F1F;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .gp-hero-title {
        font-size: 38px;
        font-weight: 700;
        color: #1F1F1F;
        letter-spacing: -0.8px;
        margin-bottom: 16px;
    }

    /* Floating Pill Search Bar */
    div[data-testid="stTextInput"] > div > div {
        background-color: #FFFFFF !important;
        border-radius: 100px !important;
        border: 1px solid #C4C7C5 !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.05) !important;
        padding: 6px 20px !important;
    }
    div[data-testid="stTextInput"] > div > div:focus-within {
        border-color: #0B57D0 !important;
        box-shadow: 0 4px 24px rgba(11,87,208,0.18) !important;
    }
    div[data-testid="stTextInput"] input {
        color: #1F1F1F !important;
        font-size: 16px !important;
        background: transparent !important;
    }
    div[data-testid="stTextInput"] label {
        display: none !important;
    }

    /* Material Action Pill Buttons */
    .stButton > button {
        border-radius: 100px !important;
        border: 1px solid #747775 !important;
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        padding: 8px 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        background-color: #0B57D0 !important;
        color: #FFFFFF !important;
        border-color: #0B57D0 !important;
    }

    /* Badges */
    .badge-chip {
        background-color: #D3E3FD;
        color: #041E49;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 100px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# System Initialization
# -----------------------------------------------------------------------------
@st.cache_resource
def init_system():
    engine = SteeringVectorEngine()
    engine.load_or_build_index()
    parser = ConstraintParser()
    logger = EventLogger()
    return engine, parser, logger

engine, parser, logger = init_system()

if "query_input" not in st.session_state:
    st.session_state.query_input = "living room furniture"
if "pos_indices" not in st.session_state:
    st.session_state.pos_indices = set()
if "neg_indices" not in st.session_state:
    st.session_state.neg_indices = set()

# Fixed optimal weights (preset behind the scenes)
ALPHA = 0.5
BETA = 0.4
GAMMA = 0.2

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="gp-brand-logo">
    <span style="color:#4285F4;">G</span><span style="color:#EA4335;">o</span><span style="color:#FBBC05;">o</span><span style="color:#4285F4;">g</span><span style="color:#34A853;">l</span><span style="color:#EA4335;">e</span>
    <span style="font-weight:400; color:#444746;">Photos</span>
</div>
<div class="gp-hero-title">Makes search feel like magic</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Search Bar & Benchmark Scenarios
# -----------------------------------------------------------------------------
query_text = st.text_input("Search", value=st.session_state.query_input, placeholder="🔍 Search photos...")

parsed_chips = parser.parse_query(query_text)
parsed_year = parsed_chips.get("year")

st.markdown("<div style='font-size:13px; color:#444746; font-weight:500; margin: 12px 0 8px 0;'>Suggested Searches:</div>", unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
if p1.button("🛋️ Living Room Furniture", use_container_width=True):
    st.session_state.query_input = "living room furniture"
    st.rerun()

if p2.button("📱 Sunset Photos (2024)", use_container_width=True):
    st.session_state.query_input = "scenic landscape sunset 2024"
    st.rerun()

if p3.button("🧾 Receipts & Documents", use_container_width=True):
    st.session_state.query_input = "paper document receipt"
    st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# Photos Results Stream
# -----------------------------------------------------------------------------
start_time = time.time()
results = engine.search(
    query_text=query_text,
    pos_indices=list(st.session_state.pos_indices),
    neg_indices=list(st.session_state.neg_indices),
    active_year=parsed_year,
    alpha=ALPHA,
    beta=BETA,
    gamma=GAMMA,
    top_k=12
)
latency_ms = round((time.time() - start_time) * 1000, 2)

status_col1, status_col2 = st.columns([3, 1])
with status_col1:
    st.markdown(f"<span style='font-size:14px; color:#444746;'>Found <b>{len(results)}</b> photos ({latency_ms} ms)</span>", unsafe_allow_html=True)
with status_col2:
    if parsed_year:
        st.markdown(f"<span class='badge-chip'>📅 Filter: {parsed_year}</span>", unsafe_allow_html=True)

if not results:
    st.info("No photos found in `data/images/`.")
else:
    cols = st.columns(3)
    for idx, item in enumerate(results):
        col = cols[idx % 3]
        img_idx = item["index"]
        img_path = item["path"]

        with col:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)

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

            if b2.button(f"{'🚫 Hidden' if is_neg else '👎 Hide'}", key=f"neg_{img_idx}"):
                if is_neg:
                    st.session_state.neg_indices.remove(img_idx)
                else:
                    st.session_state.neg_indices.add(img_idx)
                    st.session_state.pos_indices.discard(img_idx)
                st.rerun()
