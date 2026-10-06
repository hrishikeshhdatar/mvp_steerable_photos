import streamlit as st
import time
import json
import os
from engine import SteeringVectorEngine
from parser import ConstraintParser
from logger import EventLogger

st.set_page_config(
    page_title="Google Photos | Steerable Search",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Google Photos Marketing & Web App Design System (Material You / 3)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

    /* Global Typography & Light Background Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Google Sans', 'Roboto', -apple-system, sans-serif !important;
        background-color: #F0F4F9 !important;
        color: #1F1F1F !important;
    }

    div[data-testid="stAppViewContainer"] {
        background-color: #F0F4F9 !important;
    }

    /* Hero Header Section */
    .gp-hero-container {
        padding: 10px 0px 20px 0px;
    }
    .gp-brand-logo {
        font-size: 22px;
        font-weight: 500;
        color: #1F1F1F;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }
    .gp-hero-title {
        font-size: 42px;
        font-weight: 700;
        color: #1F1F1F;
        letter-spacing: -0.8px;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .gp-hero-subtitle {
        font-size: 16px;
        color: #444746;
        font-weight: 400;
        margin-bottom: 20px;
    }

    /* Navigation Pill Bar */
    .gp-nav-pills {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #FFFFFF;
        padding: 6px 16px;
        border-radius: 100px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        border: 1px solid #E1E3E1;
        width: fit-content;
        margin-bottom: 24px;
        font-size: 14px;
        color: #444746;
    }

    /* Floating Pill Search Bar (Inspiration Image 1) */
    div[data-testid="stTextInput"] > div > div {
        background-color: #FFFFFF !important;
        border-radius: 100px !important;
        border: 1px solid #C4C7C5 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
        padding: 6px 20px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stTextInput"] > div > div:focus-within {
        border-color: #0B57D0 !important;
        box-shadow: 0 4px 24px rgba(11,87,208,0.18) !important;
    }
    div[data-testid="stTextInput"] input {
        color: #1F1F1F !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        background: transparent !important;
    }
    div[data-testid="stTextInput"] label {
        display: none !important;
    }

    /* Soft Rounded White Card Containers (Inspiration Image 2) */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border-radius: 20px !important;
        padding: 16px 20px !important;
        border: 1px solid #E1E3E1 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #444746 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0B57D0 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
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
        box-shadow: 0 2px 8px rgba(11,87,208,0.25) !important;
    }

    /* Left Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #E9EEF6 !important;
        border-right: 1px solid #E1E3E1 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #1F1F1F !important;
    }
    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E1E3E1 !important;
        border-radius: 16px !important;
    }

    /* Metadata Badges */
    .badge-exif {
        background-color: #D3E3FD;
        color: #041E49;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
    }
    .badge-msg {
        background-color: #FFDDAE;
        color: #2A1700;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
    }

    /* Feature Badge Circle (Inspiration Image 2 Accent) */
    .ai-circle-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #0B57D0, #7C4DFF);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Engine & State Initialization
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
if "active_year" not in st.session_state:
    st.session_state.active_year = None
if "alpha" not in st.session_state:
    st.session_state.alpha = 0.5
if "beta" not in st.session_state:
    st.session_state.beta = 0.4
if "gamma" not in st.session_state:
    st.session_state.gamma = 0.2

# -----------------------------------------------------------------------------
# Left Drawer Controls (Material Drawer)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Controls")
    st.caption("Steerable Multimodal Retrieval Lab")
    st.markdown("---")
    
    with st.expander("📋 Strategic Problem Statement", expanded=True):
        st.markdown("""
        **Failure Modes Targeted:**
        - **Context Drift:** Broad queries pulling unwanted visual noise.
        - **EXIF Stripping:** Loss of dates/geotags on messaging media (WhatsApp/Telegram).
        """)

    st.markdown("#### 🎛️ Steering Vector Weights")
    st.session_state.alpha = st.slider("Alpha (Query Weight α)", 0.0, 1.0, st.session_state.alpha, 0.05)
    st.session_state.beta = st.slider("Beta (Positive Shift β)", 0.0, 1.0, st.session_state.beta, 0.05)
    st.session_state.gamma = st.slider("Gamma (Negative Exclusion γ)", 0.0, 1.0, st.session_state.gamma, 0.05)

    if st.button("🔄 Reset Parameters & Exemplars", use_container_width=True):
        st.session_state.pos_indices = set()
        st.session_state.neg_indices = set()
        st.session_state.active_year = None
        st.rerun()

# -----------------------------------------------------------------------------
# Hero Header & Marketing Display Typography
# -----------------------------------------------------------------------------
st.markdown("""
<div class="gp-hero-container">
    <div class="gp-brand-logo">
        <span style="color:#4285F4;">G</span><span style="color:#EA4335;">o</span><span style="color:#FBBC05;">o</span><span style="color:#4285F4;">g</span><span style="color:#34A853;">l</span><span style="color:#EA4335;">e</span>
        <span style="font-weight:400; color:#444746;">Photos</span>
    </div>
    <div class="gp-hero-title">Makes search feel like magic</div>
    <div class="gp-hero-subtitle">Get more from every memory with real-time vector steering and multimodal feedback.</div>
</div>
""", unsafe_allow_html=True)

# Interactive Floating Nav Pills Bar
st.markdown("""
<div class="gp-nav-pills">
    <span style="font-weight:600; color:#0B57D0;">Search</span>
    <span>•</span>
    <span>Filter</span>
    <span>•</span>
    <span>Steer</span>
    <span>•</span>
    <span>Organize</span>
</div>
""", unsafe_allow_html=True)

# High-Contrast Telemetry Cards
m1, m2, m3, m4 = st.columns(4)
total_imgs = len(engine.image_paths)
exif_count = sum(1 for m in engine.metadata if m.get("has_exif"))
msg_media_count = total_imgs - exif_count

m1.metric("Photos Indexed", f"{total_imgs}")
m2.metric("Embedding Space", "SigLIP 1152-D")
m3.metric("Messaging Media", f"{msg_media_count}")
m4.metric("Search Latency", "< 140 ms")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Floating Pill Search Bar (Inspiration Image 1)
# -----------------------------------------------------------------------------
query_text = st.text_input("Search", value=st.session_state.query_input, placeholder="🔍 Search photos or describe visual nuances...")

parsed_chips = parser.parse_query(query_text)
parsed_year = parsed_chips.get("year") or st.session_state.active_year

# Benchmark Scenarios Row
st.markdown("<div style='font-size:13px; color:#444746; font-weight:500; margin-bottom:8px;'>Try Benchmark Scenarios:</div>", unsafe_allow_html=True)

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
# Photos Results Grid
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

status_col1, status_col2 = st.columns([3, 1])
with status_col1:
    st.markdown(f"<span style='font-size:14px; color:#444746;'>Found <b>{len(results)}</b> matching photos ({latency_ms} ms)</span>", unsafe_allow_html=True)
with status_col2:
    if parsed_year:
        st.markdown(f"<span class='badge-exif'>📅 Year Filter: {parsed_year}</span>", unsafe_allow_html=True)

if not results:
    st.info("No photos found in `data/images/`. Upload sample images to your GitHub repository.")
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

            if meta.get("has_exif"):
                st.markdown(f"<span class='badge-exif'>EXIF • {meta.get('year', 'Camera')}</span> <span style='font-size:11px; color:#5F6368;'>Score: {score:.3f}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='badge-msg'>Messaging Media</span> <span style='font-size:11px; color:#5F6368;'>Score: {score:.3f}</span>", unsafe_allow_html=True)

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
# AI-Powered Tools Card (Inspiration Image 2 Accent)
# -----------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div class="ai-circle-icon">✨</div>
""", unsafe_allow_html=True)

with st.expander("AI-Powered Tools | Vector Steering Math & Telemetry"):
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("#### Steered Vector Math")
        st.latex(r"V_{\text{steered}} = \text{Normalize}\left(\alpha V_{\text{query}} + \beta \bar{E}_{\text{pos}} - \gamma \bar{E}_{\text{neg}}\right)")
        st.json({
            "alpha": st.session_state.alpha,
            "beta": st.session_state.beta,
            "gamma": st.session_state.gamma,
            "pos_exemplars": list(st.session_state.pos_indices),
            "neg_exemplars": list(st.session_state.neg_indices)
        })
    with t2:
        st.markdown("#### Gemini Constraint Parser Output")
        st.json({
            "query": query_text,
            "chips": parsed_chips,
            "temporal_prior_offset": "+0.08" if parsed_year else "0.00"
        })
