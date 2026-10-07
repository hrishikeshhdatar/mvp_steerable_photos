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
# Material Design 3 & Google Photos Light Theme CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Text:wght@400;500&display=swap');

    /* Force Light Theme across Browser/System Dark Mode Settings */
    :root {
        color-scheme: light !important;
    }

    html, body, [class*="stApp"], .stApp {
        background-color: #FFFFFF !important;
        color: #202124 !important;
        font-family: 'Google Sans Text', 'Google Sans', Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    div[data-testid="stAppViewContainer"], div[data-testid="stVerticalBlock"] {
        background-color: #FFFFFF !important;
    }

    header[data-testid="stHeader"], footer, section[data-testid="stSidebar"] {
        display: none !important;
    }

    .main .block-container {
        max-width: 1200px !important;
        padding-left: 24px !important;
        padding-right: 24px !important;
        padding-top: 0px !important;
        padding-bottom: 48px !important;
        margin: 0 auto !important;
    }

    /* 1. Header */
    .gp-header {
        height: 64px;
        display: flex;
        align-items: center;
        background-color: #FFFFFF;
        border-bottom: 1px solid #F1F3F4;
    }
    .gp-wordmark {
        font-family: 'Google Sans', Roboto, sans-serif;
        font-size: 22px;
        font-weight: 500;
        letter-spacing: 0px !important;
        display: flex;
        align-items: center;
    }
    .gp-photos-text {
        color: #5F6368;
        font-weight: 400;
        font-size: 22px;
        margin-left: 6px;
    }

    /* 2. Page Title */
    .gp-page-title {
        font-family: 'Google Sans', Roboto, sans-serif;
        font-size: 32px;
        line-height: 40px;
        font-weight: 400;
        color: #202124;
        margin-top: 24px;
        margin-bottom: 24px;
    }

    /* 3. Search Bar */
    div[data-testid="stTextInput"] > label {
        display: none !important;
    }
    div[data-testid="stTextInput"] > div > div {
        height: 56px !important;
        min-height: 56px !important;
        background-color: #F1F3F4 !important;
        border-radius: 28px !important;
        border: none !important;
        box-shadow: none !important;
        padding-left: 56px !important;
        padding-right: 24px !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='24' viewBox='0 -960 960 960' width='24' fill='%235F6368'%3E%3Cpath d='M784-120 532-372q-30 24-69 38t-83 14q-109 0-184.5-75.5T120-580q0-109 75.5-184.5T380-840q109 0 184.5 75.5T640-580q0 44-14 83t-38 69l252 252-56 56ZM380-280q125 0 212.5-87.5T680-580q0-125-87.5-212.5T380-760q-125 0-212.5 87.5T80-580q0 125 87.5 212.5T380-280Z'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 20px center !important;
        transition: background-color 150ms ease, box-shadow 150ms ease !important;
    }
    div[data-testid="stTextInput"] > div > div:focus-within {
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(60, 64, 67, 0.3) !important;
    }
    div[data-testid="stTextInput"] input {
        font-family: 'Google Sans Text', Roboto, sans-serif !important;
        font-size: 16px !important;
        color: #202124 !important;
        height: 56px !important;
        background: transparent !important;
    }

    /* 4. Suggested Searches Chips (Explicit All-State Styling) */
    .suggested-section {
        margin-top: 16px;
    }
    .suggested-label {
        font-size: 12px;
        line-height: 16px;
        font-weight: 400;
        color: #5F6368;
        margin-bottom: 8px;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key*="chip_"]) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        width: 100% !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key*="chip_"]) > div[data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
        background-color: transparent !important;
    }

    button[key*="chip_"],
    div[data-testid="stButton"]:has(button[key*="chip_"]) > button {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #DADCE0 !important;
        color: #202124 !important;
        border-radius: 16px !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        padding: 0 12px !important;
        font-family: 'Google Sans Text', 'Google Sans', Roboto, sans-serif !important;
        font-size: 14px !important;
        line-height: 20px !important;
        font-weight: 500 !important;
        width: fit-content !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease !important;
    }

    button[key*="chip_"]:hover,
    div[data-testid="stButton"]:has(button[key*="chip_"]) > button:hover {
        background: #F1F3F4 !important;
        background-color: #F1F3F4 !important;
        border-color: #DADCE0 !important;
        color: #202124 !important;
    }

    button[key*="chip_"]:active,
    button[key*="chip_"][kind="primary"],
    div[data-testid="stButton"]:has(button[key*="chip_"]) > button:active,
    div[data-testid="stButton"]:has(button[key*="chip_"]) > button[kind="primary"] {
        background: #E8F0FE !important;
        background-color: #E8F0FE !important;
        border-color: #1A73E8 !important;
        color: #1A73E8 !important;
    }

    button[key*="chip_"]:focus-visible,
    div[data-testid="stButton"]:has(button[key*="chip_"]) > button:focus-visible {
        outline: 2px solid #1A73E8 !important;
        outline-offset: 2px !important;
    }

    button[key*="chip_"] *,
    div[data-testid="stButton"]:has(button[key*="chip_"]) > button * {
        color: inherit !important;
    }

    /* 5. Result Info Header */
    .result-info-header {
        margin-top: 24px;
        margin-bottom: 12px;
        font-size: 12px;
        line-height: 16px;
        color: #5F6368;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .badge-chip {
        background-color: #E8F0FE;
        color: #1A73E8;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 16px;
    }

    /* 6. Photo Cards & Tight Gap Fix (Bug 2) */
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]) {
        border-radius: 8px !important;
        overflow: hidden !important;
        background-color: transparent !important;
        margin-bottom: 16px !important;
        padding: 0 !important;
    }

    /* Scope vertical gap inside photo cards to 8px (0.5rem) */
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]) div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    /* Remove default margin on image */
    div[data-testid="stImage"] {
        margin-bottom: 0 !important;
    }

    div[data-testid="stImage"] img {
        margin-bottom: 0 !important;
        border-radius: 8px !important;
        width: 100% !important;
        aspect-ratio: 4 / 3 !important;
        object-fit: cover !important;
        display: block !important;
        transition: filter 150ms ease !important;
    }

    div[data-testid="stImage"]:hover img {
        filter: brightness(0.96) !important;
    }

    /* 7. Action Buttons Under Photos (Similar / Hide - Bug 1 & 2) */
    button[key*="pos_"],
    button[key*="neg_"],
    button[data-testid="stBaseButton-secondary"]:has(span),
    div[data-testid="stButton"]:has(button[key*="pos_"]) > button,
    div[data-testid="stButton"]:has(button[key*="neg_"]) > button {
        background: #F1F3F4 !important;
        background-color: #F1F3F4 !important;
        border: none !important;
        color: #5F6368 !important;
        border-radius: 18px !important;
        min-height: 36px !important;
        height: 36px !important;
        padding: 0 12px !important;
        font-family: 'Google Sans Text', 'Google Sans', Roboto, sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease !important;
        width: 100% !important;
    }

    button[key*="pos_"]:hover,
    button[key*="neg_"]:hover,
    div[data-testid="stButton"]:has(button[key*="pos_"]) > button:hover,
    div[data-testid="stButton"]:has(button[key*="neg_"]) > button:hover {
        background: #E8EAED !important;
        background-color: #E8EAED !important;
        color: #202124 !important;
    }

    button[key*="pos_"]:active,
    button[key*="neg_"]:active,
    div[data-testid="stButton"]:has(button[key*="pos_"]) > button:active,
    div[data-testid="stButton"]:has(button[key*="neg_"]) > button:active {
        background: #DADCE0 !important;
        background-color: #DADCE0 !important;
        color: #202124 !important;
    }

    /* Active Liked / Hidden State */
    button[key*="pos_"][kind="primary"],
    button[key*="neg_"][kind="primary"],
    div[data-testid="stButton"]:has(button[key*="pos_"]) > button[kind="primary"],
    div[data-testid="stButton"]:has(button[key*="neg_"]) > button[kind="primary"] {
        background: #E8F0FE !important;
        background-color: #E8F0FE !important;
        color: #1A73E8 !important;
        border: 1px solid #1A73E8 !important;
    }

    button[key*="pos_"]:focus-visible,
    button[key*="neg_"]:focus-visible,
    div[data-testid="stButton"]:has(button[key*="pos_"]) > button:focus-visible,
    div[data-testid="stButton"]:has(button[key*="neg_"]) > button:focus-visible {
        outline: 2px solid #1A73E8 !important;
        outline-offset: 2px !important;
    }

    button[key*="pos_"] *,
    button[key*="neg_"] * {
        color: inherit !important;
    }

    @media (max-width: 600px) {
        button[key*="pos_"],
        button[key*="neg_"],
        div[data-testid="stButton"]:has(button[key*="pos_"]) > button,
        div[data-testid="stButton"]:has(button[key*="neg_"]) > button {
            min-height: 44px !important;
            height: 44px !important;
        }
    }

    /* Telemetry Card Styling */
    .telemetry-card {
        background-color: #F8F9FA;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 16px;
        margin-top: 16px;
        font-size: 13px;
        color: #3C4043;
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

ALPHA = 0.5
BETA = 0.4
GAMMA = 0.2

# -----------------------------------------------------------------------------
# Header & Search Input
# -----------------------------------------------------------------------------
st.markdown("""
<header class="gp-header">
    <div class="gp-wordmark">
        <span style="color:#4285F4;">G</span><span style="color:#EA4335;">o</span><span style="color:#FBBC04;">o</span><span style="color:#4285F4;">g</span><span style="color:#34A853;">l</span><span style="color:#EA4335;">e</span><span class="gp-photos-text">Photos</span>
    </div>
</header>
<div class="gp-page-title">Makes search feel like magic</div>
""", unsafe_allow_html=True)

query_text = st.text_input("Search", value=st.session_state.query_input, placeholder="Ask Photos...", key="search_bar_input")

parsed_chips = parser.parse_query(query_text)
parsed_year = parsed_chips.get("year")

# Suggested Searches Chips
st.markdown('<div class="suggested-section"><div class="suggested-label">Suggested searches</div></div>', unsafe_allow_html=True)
chip_cols = st.columns(3)
with chip_cols[0]:
    if st.button("Living Room Furniture", icon=":material/chair:", key="chip_living_room"):
        st.session_state.query_input = "living room furniture"
        st.rerun()
with chip_cols[1]:
    if st.button("Sunset Photos (2024)", icon=":material/wb_twilight:", key="chip_sunset"):
        st.session_state.query_input = "scenic landscape sunset 2024"
        st.rerun()
with chip_cols[2]:
    if st.button("Receipts & Documents", icon=":material/receipt_long:", key="chip_receipts"):
        st.session_state.query_input = "paper document receipt"
        st.rerun()

# -----------------------------------------------------------------------------
# Search Execution
# -----------------------------------------------------------------------------
start_time = time.time()
total_indexed = max(len(getattr(engine, 'image_paths', [])), 50)

raw_search_res = engine.search(
    query_text=query_text,
    pos_indices=list(st.session_state.pos_indices),
    neg_indices=list(st.session_state.neg_indices),
    active_year=parsed_year,
    alpha=ALPHA,
    beta=BETA,
    gamma=GAMMA,
    top_k=total_indexed
)

if isinstance(raw_search_res, tuple) and len(raw_search_res) == 2:
    results, telemetry = raw_search_res
else:
    results = raw_search_res if isinstance(raw_search_res, list) else []
    telemetry = {
        "cosine_similarity": 1.0,
        "angular_drift_deg": 0.0,
        "mrr": 0.0,
        "precision_at_3": 0.0,
        "dimension": 1152,
        "total_indexed": len(results),
        "is_bounded": True
    }

latency_ms = round((time.time() - start_time) * 1000, 2)

# Result Info Header
st.markdown(f"""
<div class="result-info-header">
    <div>Found {len(results)} photos <span style="color:#70757A; font-weight:300;">· {latency_ms} ms</span></div>
    {f'<span class="badge-chip">📅 Filter: {parsed_year}</span>' if parsed_year else ''}
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Photo Grid & Action Row (Bug 2 Fix)
# -----------------------------------------------------------------------------
if not results:
    st.info("No matching photos found.")
else:
    for row_idx in range(0, len(results), 3):
        row_items = results[row_idx:row_idx+3]
        cols = st.columns(3, gap="small")
        for idx, item in enumerate(row_items):
            col = cols[idx]
            img_idx = item["index"]
            img_path = item["path"]
            is_pos = img_idx in st.session_state.pos_indices
            is_neg = img_idx in st.session_state.neg_indices

            with col:
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)

                # Place "Similar" and "Hide" side-by-side on the left with an 8px gap
                b1, b2, _ = st.columns([1, 1, 2], gap="small")
                with b1:
                    if st.button("Similar", icon=":material/thumb_up:", key=f"pos_{img_idx}", help="Show similar", type="primary" if is_pos else "secondary"):
                        if is_pos:
                            st.session_state.pos_indices.remove(img_idx)
                        else:
                            st.session_state.pos_indices.add(img_idx)
                            st.session_state.neg_indices.discard(img_idx)
                        st.rerun()
                with b2:
                    if st.button("Hide", icon=":material/visibility_off:", key=f"neg_{img_idx}", help="Hide photo", type="primary" if is_neg else "secondary"):
                        if is_neg:
                            st.session_state.neg_indices.remove(img_idx)
                        else:
                            st.session_state.neg_indices.add(img_idx)
                            st.session_state.pos_indices.discard(img_idx)
                        st.rerun()

# -----------------------------------------------------------------------------
# Executive PM Telemetry Drawer
# -----------------------------------------------------------------------------
with st.expander("🔬 Executive PM & Vector Engine Telemetry"):
    st.markdown("#### Real-time Multimodal Vector Performance")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Embedding Model", f"SigLIP {telemetry.get('dimension', 1152)}-D")
    m2.metric("Mean Reciprocal Rank (MRR)", telemetry.get("mrr", 0.0))
    m3.metric("Precision@3 Boost", f"{telemetry.get('precision_at_3', 0.0)}%")
    m4.metric("Vector Cosine Drift", f"{telemetry.get('angular_drift_deg', 0.0)}°")

    st.markdown(f"""
    <div class="telemetry-card">
        <b>Engine Guardrails:</b> Hyper-sphere Bounded (Norm = 1.00) | 
        <b>Active Exemplars:</b> +{len(st.session_state.pos_indices)} Positives, -{len(st.session_state.neg_indices)} Negatives | 
        <b>Latency Target:</b> {latency_ms}ms / 150ms
    </div>
    """, unsafe_allow_html=True)
