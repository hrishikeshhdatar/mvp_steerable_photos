import streamlit as st
import os
from engine import SteeringVectorEngine
from parser import FollowupQueryParser
from logger import TelemetryLogger

st.set_page_config(page_title="Steerable Photo Retrieval MVP", layout="wide")

@st.cache_resource
def init_system():
    engine = SteeringVectorEngine()
    engine.load_or_build_index()
    parser = FollowupQueryParser()
    logger = TelemetryLogger()
    return engine, parser, logger

engine, parser, logger = init_system()

# Session State Initialization
if "pos_indices" not in st.session_state:
    st.session_state.pos_indices = []
if "neg_indices" not in st.session_state:
    st.session_state.neg_indices = []
if "active_year" not in st.session_state:
    st.session_state.active_year = None
if "active_query" not in st.session_state:
    st.session_state.active_query = "child yellow kurta brass lamp"

st.title("🔍 Steerable Photo Retrieval MVP")
st.caption("Standalone Prototype testing Vector Steering (+1/-1) & Stateful Constraint Chips")

# Top Search Controls
col_q, col_yr = st.columns([4, 1])
with col_q:
    query_input = st.text_input("Initial Visual Search Prompt:", value=st.session_state.active_query)
with col_yr:
    year_input = st.text_input("Temporal Filter (Optional Year):", value=str(st.session_state.active_year) if st.session_state.active_year else "")
    st.session_state.active_year = int(year_input) if year_input.isdigit() else None

# Active Chips Display (F3)
st.subheader("Active Constraints & Steering State")
chip_cols = st.columns([3, 1])
with chip_cols[0]:
    st.info(
        f"🔹 Query: `{query_input}` | "
        f"🟢 Positive Anchors: `{len(st.session_state.pos_indices)}` | "
        f"🔴 Negative Exclusions: `{len(st.session_state.neg_indices)}` | "
        f"📅 Conditional Time Boost: `{st.session_state.active_year if st.session_state.active_year else 'None (Neutral)'}`"
    )
with chip_cols[1]:
    if st.button("Reset Steering State"):
        st.session_state.pos_indices = []
        st.session_state.neg_indices = []
        st.session_state.active_year = None
        st.rerun()

# Conversational Follow-up Bar (F3)
followup_text = st.text_input("💬 Conversational Follow-up (e.g., 'show indoor living room ones'):")
if st.button("Apply Follow-up"):
    if followup_text:
        parsed = parser.parse_followup(query_input, followup_text, st.session_state.active_year)
        st.session_state.active_query = " ".join(parsed.visual_descriptors)
        if parsed.active_year:
            st.session_state.active_year = parsed.active_year
        logger.log_event("followup_applied", {"text": followup_text, "parsed": parsed.dict()})
        st.rerun()

# Execute Vector Steering Search
results = engine.search(
    query_text=query_input,
    pos_indices=st.session_state.pos_indices,
    neg_indices=st.session_state.neg_indices,
    active_year=st.session_state.active_year
)

# Results Grid
st.subheader("Candidate Results Grid (Top 20)")
if not results:
    st.warning("No images found in `data/images`. Please place test images in the folder and restart.")
else:
    cols = st.columns(4)
    for idx, item in enumerate(results):
        col = cols[idx % 4]
        with col:
            st.image(item["path"], use_column_width=True)
            st.caption(f"Rank #{item['rank']} | Similarity: {item['score']:.3f}")
            
            b_pos, b_neg = st.columns(2)
            img_idx = item["index"]

            with b_pos:
                is_pos = img_idx in st.session_state.pos_indices
                btn_label = "🟢 Liked" if is_pos else "+1 Like"
                if st.button(btn_label, key=f"pos_{img_idx}"):
                    if is_pos:
                        st.session_state.pos_indices.remove(img_idx)
                    else:
                        st.session_state.pos_indices.append(img_idx)
                        if img_idx in st.session_state.neg_indices:
                            st.session_state.neg_indices.remove(img_idx)
                    logger.log_event("pos_steer_toggle", {"img_idx": img_idx, "path": item["path"]})
                    st.rerun()

            with b_neg:
                is_neg = img_idx in st.session_state.neg_indices
                btn_label = "🔴 Excluded" if is_neg else "-1 Not"
                if st.button(btn_label, key=f"neg_{img_idx}"):
                    if is_neg:
                        st.session_state.neg_indices.remove(img_idx)
                    else:
                        st.session_state.neg_indices.append(img_idx)
                        if img_idx in st.session_state.pos_indices:
                            st.session_state.pos_indices.remove(img_idx)
                    logger.log_event("neg_steer_toggle", {"img_idx": img_idx, "path": item["path"]})
                    st.rerun()
