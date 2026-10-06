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
# Material Design 3 & Google Photos Design System CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Text:wght@400;500&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

    /* Global Typography & Canvas Reset */
    html, body, [class*="stApp"], .stApp {
        background-color: #FFFFFF !important;
        color: #202124 !important;
        font-family: 'Google Sans Text', 'Google Sans', Roboto, Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Hide Default Streamlit Header, Footer, and Sidebar */
    header[data-testid="stHeader"], footer, section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Max Content Width (1200px centered, 24px side padding) */
    .main .block-container {
        max-width: 1200px !important;
        padding-left: 24px !important;
        padding-right: 24px !important;
        padding-top: 0px !important;
        padding-bottom: 48px !important;
        margin: 0 auto !important;
    }

    /* 1. Google Photos Header (64px tall, left-aligned) */
    .gp-header {
        height: 64px;
        display: flex;
        align-items: center;
        background-color: #FFFFFF;
        border-bottom: 1px solid #F1F3F4;
        margin-bottom: 0px;
    }
    .gp-wordmark {
        font-family: 'Google Sans', Roboto, sans-serif;
        font-size: 22px;
        font-weight: 500;
        line-height: 28px;
        letter-spacing: 0px !important;
        display: flex;
        align-items: center;
    }
    .gp-wordmark span {
        letter-spacing: 0px !important;
    }
    .gp-photos-text {
        color: #5F6368;
        font-weight: 400;
        font-size: 22px;
        margin-left: 6px;
    }

    /* 2. Page Title (32px / 40px line-height, weight 400, 24px margins) */
    .gp-page-title {
        font-family: 'Google Sans', Roboto, sans-serif;
        font-size: 32px;
        line-height: 40px;
        font-weight: 400;
        color: #202124;
        margin-top: 24px;
        margin-bottom: 24px;
    }

    /* 3. Search Bar (56px tall, 28px radius, no border, elevation shadow on focus) */
    div[data-testid="stTextInput"] {
        margin-bottom: 0px !important;
    }
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
        border: none !important;
    }
    div[data-testid="stTextInput"] input {
        font-family: 'Google Sans Text', 'Google Sans', Roboto, sans-serif !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        color: #202124 !important;
        height: 56px !important;
        background: transparent !important;
    }

    /* 4. Suggested Searches Chips (Strictly Scoped Pill Styling) */
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

    /* Target ONLY the suggested searches row */
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
    }
    div[data-testid="stHorizontalBlock"]:has(button[key*="chip_"]) button {
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        border-radius: 16px !important;
        border: 1px solid #DADCE0 !important;
        background-color: #FFFFFF !important;
        color: #202124 !important;
        font-family: 'Google Sans Text', 'Google Sans', Roboto, sans-serif !important;
        font-size: 14px !important;
        line-height: 20px !important;
        font-weight: 500 !important;
        padding: 0 16px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
        width: auto !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: background-color 150ms ease, border-color 150ms ease !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key*="chip_"]) button:hover {
        background-color: #F1F3F4 !important;
        border-color: #DADCE0 !important;
        color: #202124 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(button[key*="chip_"]) button span[data-testid="stIconMaterial"] {
        font-size: 18px !important;
        color: #5F6368 !important;
        margin-right: 6px !important;
    }

    /* 5. Result Info Header */
    .result-info-header {
        margin-top: 32px;
        margin-bottom: 16px;
        font-size: 12px;
        line-height: 16px;
        font-weight: 400;
        color: #5F6368;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .result-info-header .latency {
        color: #70757A;
        font-weight: 300;
    }
    .badge-chip {
        background-color: #E8F0FE;
        color: #1A73E8;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 16px;
        display: inline-block;
    }

    /* 6. Photo Grid & Action Overlay */
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]) {
        position: relative !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        background-color: #E8EAED !important;
        transition: transform 150ms ease !important;
        margin-bottom: 8px !important;
    }

    /* Photo Image */
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]) div[data-testid="stImage"] {
        margin: 0 !important;
        line-height: 0 !important;
    }
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]) div[data-testid="stImage"] img {
        border-radius: 8px !important;
        width: 100% !important;
        aspect-ratio: 4 / 3 !important;
        object-fit: cover !important;
        display: block !important;
        transition: filter 150ms ease !important;
    }

    /* Dim photo slightly on hover */
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]):hover div[data-testid="stImage"] img {
        filter: brightness(0.92) !important;
    }

    /* Action Buttons Row Container (Overlay at Bottom-Right Corner) */
    div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) {
        position: absolute !important;
        bottom: 12px !important;
        right: 12px !important;
        top: auto !important;
        left: auto !important;
        width: auto !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-end !important;
        gap: 8px !important;
        z-index: 10 !important;
        opacity: 0 !important;
        pointer-events: none !important;
        transition: opacity 150ms ease-in-out !important;
        margin: 0 !important;
    }

    /* Column wrappers inside the action row */
    div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) > div[data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Action Buttons (36px circular icons side-by-side) */
    div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) button {
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        min-height: 36px !important;
        max-width: 36px !important;
        max-height: 36px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        background-color: rgba(32, 33, 36, 0.6) !important;
        color: #FFFFFF !important;
        border: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
        transition: background-color 150ms ease, transform 150ms ease !important;
        backdrop-filter: blur(4px) !important;
        cursor: pointer !important;
    }

    /* Liked/Selected state (Accent Blue) */
    div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) button[kind="primary"] {
        background-color: #1A73E8 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) button:hover {
        background-color: rgba(32, 33, 36, 0.85) !important;
        transform: scale(1.05) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) button span[data-testid="stIconMaterial"] {
        font-size: 20px !important;
        color: #FFFFFF !important;
        margin: 0 !important;
    }

    /* HOVER TRIGGER: Show buttons grouped in bottom-right ONLY on photo hover/focus */
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]):hover div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]),
    div[data-testid="stColumn"]:has(div[data-testid="stImage"]):focus-within div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) {
        opacity: 1 !important;
        pointer-events: auto !important;
    }

    @media (hover: none) {
        div[data-testid="stHorizontalBlock"]:has(button[key*="pos_"]) {
            opacity: 1 !important;
            pointer-events: auto !important;
        }
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 48px 16px;
        color: #202124;
    }
    .empty-state-icon {
        font-size: 48px;
        color: #5F6368;
        margin-bottom: 12px;
    }
    .empty-state-title {
        font-size: 16px;
        font-weight: 500;
        line-height: 24px;
        color: #202124;
        margin-bottom: 4px;
    }
    .empty-state-hint {
        font-size: 14px;
        font-weight: 400;
        line-height: 20px;
        color: #5F6368;
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
# 1. Header
# -----------------------------------------------------------------------------
st.markdown("""
<header class="gp-header">
    <div class="gp-wordmark">
        <span style="color:#4285F4;">G</span><span style="color:#EA4335;">o</span><span style="color:#FBBC04;">o</span><span style="color:#4285F4;">g</span><span style="color:#34A853;">l</span><span style="color:#EA4335;">e</span><span class="gp-photos-text">Photos</span>
    </div>
</header>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Page Title
# -----------------------------------------------------------------------------
st.markdown('<div class="gp-page-title">Makes search feel like magic</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Search Bar
# -----------------------------------------------------------------------------
query_text = st.text_input(
    "Search",
    value=st.session_state.query_input,
    placeholder="Ask Photos...",
    key="search_bar_input"
)

parsed_chips = parser.parse_query(query_text)
parsed_year = parsed_chips.get("year")

# -----------------------------------------------------------------------------
# 4. Suggested Searches Chips
# -----------------------------------------------------------------------------
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
total_indexed = max(len(engine.image_paths), 50)

results = engine.search(
    query_text=query_text,
    pos_indices=list(st.session_state.pos_indices),
    neg_indices=list(st.session_state.neg_indices),
    active_year=parsed_year,
    alpha=ALPHA,
    beta=BETA,
    gamma=GAMMA,
    top_k=total_indexed
)
latency_ms = round((time.time() - start_time) * 1000, 2)

# -----------------------------------------------------------------------------
# 5. Result Info
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="result-info-header">
    <div>Found {len(results)} photos <span class="latency">· {latency_ms} ms</span></div>
    {f'<span class="badge-chip">📅 Filter: {parsed_year}</span>' if parsed_year else ''}
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. Photo Grid & Hover Actions
# -----------------------------------------------------------------------------
if not results:
    st.markdown("""
    <div class="empty-state">
        <div class="material-symbols-outlined empty-state-icon">search_off</div>
        <div class="empty-state-title">No photos found</div>
        <div class="empty-state-hint">Try adjusting your search terms or clearing your filters</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for row_idx in range(0, len(results), 3):
        row_items = results[row_idx:row_idx+3]
        cols = st.columns(3)
        
        for idx, item in enumerate(row_items):
            col = cols[idx]
            img_idx = item["index"]
            img_path = item["path"]
            is_pos = img_idx in st.session_state.pos_indices
            is_neg = img_idx in st.session_state.neg_indices

            with col:
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)

                # Overlaid side-by-side action buttons
                b1, b2 = st.columns(2)
                
                with b1:
                    if st.button(
                        "",
                        icon=":material/thumb_up:",
                        key=f"pos_{img_idx}",
                        help="Show similar",
                        type="primary" if is_pos else "secondary"
                    ):
                        if is_pos:
                            st.session_state.pos_indices.remove(img_idx)
                        else:
                            st.session_state.pos_indices.add(img_idx)
                            st.session_state.neg_indices.discard(img_idx)
                        st.rerun()

                with b2:
                    if st.button(
                        "",
                        icon=":material/visibility_off:",
                        key=f"neg_{img_idx}",
                        help="Hide photo",
                        type="primary" if is_neg else "secondary"
                    ):
                        if is_neg:
                            st.session_state.neg_indices.remove(img_idx)
                        else:
                            st.session_state.neg_indices.add(img_idx)
                            st.session_state.pos_indices.discard(img_idx)
                        st.rerun()
