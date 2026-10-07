import os
import glob
import re
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & GLOBAL LIGHT THEME ENFORCEMENT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Google Photos Search Insights Engine & Sandbox",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force Streamlit frontend theme state to Light Mode via JavaScript
st.components.v1.html("""
<script>
    const setLight = () => {
        try {
            const parentDoc = window.parent.document;
            parentDoc.documentElement.setAttribute('data-theme', 'light');
            parentDoc.body.setAttribute('data-theme', 'light');
            window.parent.localStorage.setItem('stActiveTheme', '{"base":"light"}');
        } catch (e) {
            console.log("Theme initialized");
        }
    };
    setLight();
    setTimeout(setLight, 500);
</script>
""", height=0, width=0)

# Material Design 3 Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Text:wght@400;500&family=Roboto:wght@400;500;700&display=swap');

    /* 1. FORCE STREAMLIT GLOBAL CSS VARIABLES TO LIGHT MODE */
    :root, [data-testid="stAppViewContainer"], .stApp, [class*="stApp"], body {
        color-scheme: light !important;
        --background-color: #FFFFFF !important;
        --secondary-background-color: #F8F9FA !important;
        --text-color: #202124 !important;
        --primary-color: #1A73E8 !important;
    }

    /* Hide Default Streamlit Chrome Header & Footer */
    header[data-testid="stHeader"], footer, #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    /* Canvas & Global App Background */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #202124 !important;
        font-family: 'Google Sans Text', 'Roboto', Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Main Content Container Layout */
    .main .block-container {
        max-width: 1200px !important;
        padding-left: 32px !important;
        padding-right: 32px !important;
        padding-top: 32px !important;
        padding-bottom: 48px !important;
        margin: 0 auto !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 280px !important;
        background-color: #F8F9FA !important;
        border-right: 1px solid #DADCE0 !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 24px 16px !important;
    }

    .sb-label {
        font-size: 12px !important;
        line-height: 16px !important;
        font-weight: 500 !important;
        color: #5F6368 !important;
        text-transform: none !important;
        margin-bottom: 12px !important;
    }

    .sb-metric-row {
        margin-bottom: 16px !important;
    }

    .sb-metric-label {
        font-size: 12px !important;
        line-height: 16px !important;
        color: #5F6368 !important;
        font-weight: 400 !important;
    }

    .sb-metric-value {
        font-family: 'Google Sans', sans-serif !important;
        font-size: 24px !important;
        line-height: 32px !important;
        font-weight: 500 !important;
        color: #202124 !important;
        margin-top: 4px !important;
    }

    .sb-divider {
        height: 1px !important;
        background-color: #DADCE0 !important;
        margin: 16px 0 !important;
        border: none !important;
    }

    /* Status Pill Chips */
    .status-pill-success {
        display: inline-flex !important;
        align-items: center !important;
        height: 28px !important;
        padding: 0 12px !important;
        border-radius: 14px !important;
        background-color: #E6F4EA !important;
        color: #137333 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    .status-pill-error {
        display: inline-flex !important;
        align-items: center !important;
        height: 28px !important;
        padding: 0 12px !important;
        border-radius: 14px !important;
        background-color: #FCE8E6 !important;
        color: #B3261F !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    .status-dot-success {
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        background-color: #137333 !important;
        margin-right: 8px !important;
        display: inline-block !important;
    }

    .status-dot-error {
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        background-color: #B3261F !important;
        margin-right: 8px !important;
        display: inline-block !important;
    }

    /* Header & Section Typography */
    .md-header-title {
        font-family: 'Google Sans', sans-serif !important;
        font-size: 32px !important;
        line-height: 40px !important;
        font-weight: 500 !important;
        color: #202124 !important;
        margin: 0 !important;
    }

    .md-header-subtitle {
        font-size: 14px !important;
        line-height: 20px !important;
        color: #5F6368 !important;
        margin-top: 8px !important;
        margin-bottom: 24px !important;
    }

    .md-header-divider {
        height: 1px !important;
        background-color: #DADCE0 !important;
        border: none !important;
        margin-bottom: 24px !important;
    }

    .md-section-title {
        font-family: 'Google Sans', sans-serif !important;
        font-size: 22px !important;
        line-height: 28px !important;
        font-weight: 500 !important;
        color: #202124 !important;
        margin-bottom: 8px !important;
    }

    .md-section-caption {
        font-size: 14px !important;
        line-height: 20px !important;
        color: #5F6368 !important;
        margin-bottom: 24px !important;
    }

    /* Navigation Tabs */
    div[data-testid="stTabs"] {
        margin-bottom: 24px !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 0px !important;
        border-bottom: 1px solid #DADCE0 !important;
        background-color: transparent !important;
        padding-bottom: 0px !important;
    }

    button[data-baseweb="tab"] {
        height: 48px !important;
        padding: 0 24px !important;
        font-family: 'Google Sans Text', 'Roboto', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        transition: background-color 150ms ease, color 150ms ease !important;
    }

    button[data-baseweb="tab"] * {
        color: #3C4043 !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }

    button[data-baseweb="tab"]:hover {
        background-color: #F1F3F4 !important;
    }

    button[data-baseweb="tab"]:hover * {
        color: #1A73E8 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: transparent !important;
        border-bottom: 3px solid #1A73E8 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] * {
        color: #1A73E8 !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="tab-highlight"] {
        background-color: #1A73E8 !important;
    }

    /* =========================================================
       UNIFORM GALLERY IMAGE HEIGHT & CROP FIX
       ========================================================= */
    div[data-testid="stImage"] {
        width: 100% !important;
        margin-bottom: 8px !important;
    }

    div[data-testid="stImage"] img {
        width: 100% !important;
        height: 200px !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 1px solid #DADCE0 !important;
        transition: transform 200ms ease, box-shadow 200ms ease !important;
    }

    div[data-testid="stImage"] img:hover {
        box-shadow: 0px 4px 12px rgba(60, 64, 67, 0.15) !important;
    }

    /* =========================================================
       LIGHT GREY NEUTRAL BUTTONS (PREVIOUS VERSION)
       ========================================================= */
    div[data-testid="stButton"] > button {
        height: 32px !important;
        min-height: 32px !important;
        border-radius: 16px !important;
        background-color: #F1F3F4 !important;
        color: #3C4043 !important;
        font-family: 'Google Sans Text', 'Roboto', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 0 16px !important;
        border: 1px solid #DADCE0 !important;
        box-shadow: none !important;
        transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease !important;
        cursor: pointer !important;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: #E8F0FE !important;
        color: #1A73E8 !important;
        border-color: #AECBFA !important;
    }

    /* Container Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #F8F9FA !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: none !important;
        margin-bottom: 24px !important;
    }

    /* Dataframe Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #DADCE0 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
        box-shadow: none !important;
    }

    /* Selectboxes */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] * {
        color: #202124 !important;
        background-color: transparent !important;
    }

    div[data-baseweb="select"] svg {
        fill: #5F6368 !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] [data-baseweb="menu"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] div {
        background-color: #FFFFFF !important;
        color: #202124 !important;
    }

    div[data-baseweb="popover"] [data-baseweb="menu"] {
        border: 1px solid #DADCE0 !important;
        border-radius: 8px !important;
        box-shadow: 0px 4px 12px rgba(60, 64, 67, 0.15) !important;
    }

    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] li * {
        background-color: #FFFFFF !important;
        color: #202124 !important;
        font-size: 14px !important;
        font-family: 'Google Sans Text', 'Roboto', sans-serif !important;
    }

    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li:hover *,
    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="popover"] li[aria-selected="true"] * {
        background-color: #E8F0FE !important;
        color: #1A73E8 !important;
    }

    /* Inputs */
    div[data-testid="stTextArea"] label, 
    div[data-testid="stTextInput"] label, 
    div[data-testid="stSelectbox"] label, 
    div[data-testid="stSlider"] label {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #202124 !important;
        margin-bottom: 8px !important;
    }

    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        color: #202124 !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 8px !important;
    }

    .input-helper-text {
        font-size: 12px !important;
        line-height: 16px !important;
        color: #5F6368 !important;
        margin-top: 4px !important;
    }

    /* Summary Card Output */
    .summary-output-card {
        background-color: #FFFFFF !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        max-width: 72ch !important;
        font-size: 14px !important;
        line-height: 22px !important;
        color: #202124 !important;
        margin-top: 24px !important;
    }

    .summary-output-card h1, .summary-output-card h2, .summary-output-card h3 {
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #202124 !important;
        margin-top: 16px !important;
        margin-bottom: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. API KEY & RESILIENT IMAGE INDEXING
# -----------------------------------------------------------------------------
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GEMINI_API_KEY", "")

@st.cache_data(show_spinner=False)
def init_system(image_dirs=None):
    """Fast, memory-safe photo library indexer."""
    if image_dirs is None:
        image_dirs = [os.path.join("data", "images"), "images", "."]
        
    found_images = []
    extensions = ('*.jpg', '*.jpeg', '*.png', '*.webp', '*.JPG', '*.JPEG', '*.PNG')
    
    for folder in image_dirs:
        if os.path.exists(folder):
            for ext in extensions:
                found_images.extend(glob.glob(os.path.join(folder, ext)))
                
    return sorted(list(set(found_images)))

image_library = init_system()

# -----------------------------------------------------------------------------
# 2. DATA INGESTION & HEURISTIC ENGINE
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_analyze_corpus():
    csv_files = glob.glob("*.csv")
    if not csv_files:
        return pd.DataFrame()
        
    column_mapping = {
        'title': 'title', 'post_title': 'title', 'subject': 'title',
        'selftext': 'content', 'text': 'content', 'body': 'content', 
        'review_text': 'content', 'content': 'content',
        'rating': 'user_score', 'score': 'user_score', 'user_score': 'user_score',
        'upvotes': 'user_score', 'ups': 'user_score', 'stars': 'user_score',
        'likes': 'user_score', 'thumbs_up': 'user_score'
    }
    
    dfs = []
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig", on_bad_lines="skip", low_memory=False)
            if not df.empty:
                df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
                df = df.loc[:, ~df.columns.duplicated()]
                df = df.rename(columns=column_mapping)
                
                fname = file_path.lower()
                if 'reddit' in fname:
                    df['source_platform'] = 'Reddit Discussions'
                elif 'discussions' in fname or 'public' in fname or 'forum' in fname:
                    df['source_platform'] = 'Support Forums'
                else:
                    df['source_platform'] = 'App Store / Play Store'
                    
                dfs.append(df)
        except Exception:
            continue

    if not dfs:
        return pd.DataFrame()

    master_df = pd.concat(dfs, ignore_index=True, sort=False)
    
    title_s = master_df.get('title', pd.Series(['']*len(master_df))).fillna('').astype(str)
    content_s = master_df.get('content', pd.Series(['']*len(master_df))).fillna('').astype(str)
    
    master_df['full_text'] = (title_s + " " + content_s).str.strip()
    master_df = master_df[master_df['full_text'].str.len() > 10].drop_duplicates(subset=['full_text'])

    # Taxonomy Tagging
    retrieval_kw = r"search|find|cant find|can't find|missing|lost|where|date|location|album|ocr|text|gemini|scroll|remember|face|people"
    master_df['is_retrieval_issue'] = master_df['full_text'].str.contains(retrieval_kw, case=False, na=False)

    taxonomies = {
        'Temporal / Milestone Ambiguity': r'date|year|month|timeline|old|years ago|timestamp|chronological',
        'Relational & Person Context': r'face|people|person|untagged|tag|child|baby|family|friend',
        'Document / OCR & Text Retrieval': r'ocr|text|document|receipt|screenshot|notes|paper|read',
        'Spatial & Event Context': r'location|place|city|trip|vacation|wedding|party|event|where',
        'Visual & Attribute Matching': r'color|dog|cat|car|shirt|object|thing|background|visual'
    }
    
    def tag_taxonomy(text):
        for category, pattern in taxonomies.items():
            if re.search(pattern, text, re.IGNORECASE):
                return category
        return 'General Retrieval Friction'

    master_df['problem_category'] = master_df['full_text'].apply(tag_taxonomy)

    # Search Strategy Tagging
    def tag_search_strategy(text):
        if re.search(r'filename|\.jpg|\.png|file name|folder|album name', text, re.I):
            return 'Exact Metadata / Structured Search'
        elif re.search(r'ocr|text|read|receipt|screenshot|document|words', text, re.I):
            return 'OCR & Text Content Search'
        elif re.search(r'face|people|person|tag|mom|dad|baby|friend|family', text, re.I):
            return 'Relational & Person Search'
        elif re.search(r'date|year|month|old|time|ago|timeline|202|201', text, re.I):
            return 'Broad Temporal / Lifecycle Search'
        else:
            return 'Visual & Semantic Keyword Search'

    master_df['search_strategy'] = master_df['full_text'].apply(tag_search_strategy)

    # Memory Anchors
    master_df['remembered_anchor'] = master_df['full_text'].apply(
        lambda x: 'Event / Emotion / Visual Context' if re.search(r'wedding|trip|vacation|party|dog|happy|red|blue', x, re.I)
        else ('Person / Relational Context' if re.search(r'mom|dad|friend|baby|son|daughter|face', x, re.I)
        else 'General Salient Memory')
    )

    master_df['forgotten_anchor'] = master_df['full_text'].apply(
        lambda x: 'Exact Date / Year' if re.search(r'date|year|when|time|month', x, re.I)
        else ('Exact Folder / Album Name' if re.search(r'folder|album|where|location|path', x, re.I)
        else 'Exact Metadata / File String')
    )

    return master_df

df = load_and_analyze_corpus()

# -----------------------------------------------------------------------------
# PLOTLY CHART HELPER
# -----------------------------------------------------------------------------
def render_horizontal_bar_chart(series_data, x_label="Mentions", height=320):
    chart_df = series_data.reset_index()
    chart_df.columns = ['category', 'count']
    total_val = chart_df['count'].sum() if chart_df['count'].sum() > 0 else 1
    chart_df['share'] = (chart_df['count'] / total_val) * 100
    
    chart_df = chart_df.sort_values(by='count', ascending=True)
    chart_df['label_text'] = chart_df.apply(lambda r: f"{r['count']:,} · {r['share']:.1f}%", axis=1)

    colors = ['#AECBFA'] * len(chart_df)
    if len(colors) > 0:
        colors[-1] = '#1A73E8'

    fig = px.bar(
        chart_df,
        x='count',
        y='category',
        orientation='h',
        text='label_text'
    )
    
    fig.update_traces(
        marker_color=colors,
        marker_line_width=0,
        textposition='outside',
        textfont=dict(color='#202124', size=12, family='Roboto, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>'
    )
    
    fig.update_layout(
        margin=dict(l=220, r=80, t=10, b=30),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title=dict(text=x_label, font=dict(color='#5F6368', size=12)),
            showgrid=False,
            zeroline=True,
            zerolinecolor='#DADCE0',
            zerolinewidth=1,
            tickfont=dict(color='#5F6368', size=11)
        ),
        yaxis=dict(
            title='',
            showgrid=False,
            automargin=True,
            tickfont=dict(color='#202124', size=14, family='Google Sans Text, Roboto, sans-serif')
        )
    )
    return fig

# -----------------------------------------------------------------------------
# 3. HEADER & SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.markdown("""
<div style="margin-bottom: 24px;">
    <div class="md-header-title">Google Photos Search Insights Engine & Sandbox</div>
    <div class="md-header-subtitle">Analyzing photo retrieval friction, user memory decay, and steerable photo search</div>
    <div class="md-header-divider"></div>
</div>
""", unsafe_allow_html=True)

retrieval_df = df[df['is_retrieval_issue'] == True] if not df.empty else pd.DataFrame()

# Sidebar Status
with st.sidebar:
    status_pill = '<div class="status-pill-success"><span class="status-dot-success"></span>Gemini connected</div>' if api_key else '<div class="status-pill-error"><span class="status-dot-error"></span>Offline Mode</div>'
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div class="sb-label">Dataset Stats</div>
        <div class="sb-metric-row">
            <div class="sb-metric-label">Total Ingested Feedback</div>
            <div class="sb-metric-value">{len(df):,}</div>
        </div>
        <div class="sb-divider"></div>
        <div class="sb-metric-row">
            <div class="sb-metric-label">Indexed Library Photos</div>
            <div class="sb-metric-value">{len(image_library):,}</div>
        </div>
        <div class="sb-divider"></div>
        <div class="sb-label">AI Status</div>
        {status_pill}
    </div>
    """, unsafe_allow_html=True)

# Navigation Tabs (Clean text, no emojis)
tab_gallery, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Photo Library Gallery",
    "AI Summary",
    "Priorities", 
    "Memory Patterns", 
    "Search Evidence",
    "All Data"
])

# -----------------------------------------------------------------------------
# TAB 0: PHOTO LIBRARY GALLERY
# -----------------------------------------------------------------------------
with tab_gallery:
    st.markdown("""
    <div>
        <div class="md-section-title">MVP Photo Library Grid</div>
        <div class="md-section-caption">Explore all indexed sandbox target and distractor photos in a clean, uniform grid.</div>
    </div>
    """, unsafe_allow_html=True)

    if not image_library:
        st.info("No images found in `data/images/`. Please verify target and distractor photos are uploaded to GitHub.")
    else:
        with st.container(border=True):
            filter_query = st.text_input("Filter library by keyword:", placeholder="e.g. sunset, baby, desk, lamp")
        
        filtered_imgs = [img for img in image_library if filter_query.lower() in img.lower()] if filter_query else image_library

        # Render 3-column uniform grid
        cols_per_row = 3
        for i in range(0, len(filtered_imgs), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(filtered_imgs):
                    img_path = filtered_imgs[i + j]
                    fname = os.path.basename(img_path)
                    
                    with cols[j]:
                        st.image(img_path, use_column_width=True)
                        
                        # Action Buttons (Clean text: Similar / Hide)
                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            st.button("Similar", key=f"sim_{i+j}_{fname}")
                        with btn_c2:
                            st.button("Hide", key=f"hide_{i+j}_{fname}")

# -----------------------------------------------------------------------------
# TAB 1: AI SUMMARY
# -----------------------------------------------------------------------------
with tab1:
    st.markdown("""
    <div>
        <div class="md-section-title">AI Research Synthesizer</div>
        <div class="md-section-caption">Synthesize real user complaint logs into executive research findings using Gemini.</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        user_query = st.text_area(
            "Research Question:", 
            value="What kinds of old photos do users struggle to retrieve, and what information have they forgotten?",
            height=96
        )
        st.markdown('<div class="input-helper-text">Ask about retrieval issues, memory gaps, or opportunity areas.</div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        generate_btn = st.button("Generate Executive Summary")

    if generate_btn:
        if not api_key:
            st.warning("No Gemini API key found. Displaying standard summary baseline:")
            st.markdown("""
            <div class="summary-output-card">
            <h3>Executive Summary: User Retrieval Friction & Memory Cognitive Load</h3>
            
            <h4>1. Direct Answer</h4>
            <ul>
                <li><b>Primary Struggling Photo Types:</b> Screenshots, document scans/receipts, and milestone event photos from 3+ years ago.</li>
                <li><b>Search Formulation Behavior:</b> Users input natural language descriptions rather than structured metadata filters.</li>
            </ul>
            
            <h4>2. Memory Anchor Analysis</h4>
            <ul>
                <li><b>What Users Remember:</b> Salient visual anchors (e.g., <i>'red jacket'</i>, <i>'beach trip'</i>), broad timeframes, or people present.</li>
                <li><b>What Users Forget:</b> Precise timestamps, exact folder structures, or original file tags.</li>
            </ul>
            
            <h4>3. Strategic Opportunity</h4>
            <ul>
                <li>Fix core semantic search indexing failures.</li>
                <li>De-clutter AI recommendations to prioritize chronological retrieval.</li>
                <li>Improve device vs. cloud storage clarity.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                
                selected_samples = retrieval_df['full_text'].head(30).tolist() if not retrieval_df.empty else []
                sample_text = "\n".join([f"- {text}" for text in selected_samples])
                
                prompt = (
                    "You are a Principal Product Manager for Google Photos.\n\n"
                    f"TASK:\nSynthesize user feedback to answer: '{user_query}'\n\n"
                    f"USER FEEDBACK CONTEXT:\n{sample_text}\n\n"
                    "REQUIRED REPORT STRUCTURE:\n"
                    "# Executive Summary: User Retrieval Friction & Memory Cognitive Load\n\n"
                    "### 1. Direct Answer & Retrieval Friction\n"
                    "Synthesize primary categories of photos users struggle to retrieve with user quote evidence.\n\n"
                    "### 2. Memory Anchor Analysis\n"
                    "Provide a Markdown table comparing:\n"
                    "- What Users Remember (The Emotional / Intentional Anchor)\n"
                    "- What Users Forget (The Technical / Structural Gap)\n\n"
                    "### 3. Strategic Opportunity Pillars\n"
                    "Detail 3 actionable product initiatives for Google Photos to solve these friction points.\n"
                )
                
                with st.spinner("Generating summary..."):
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    res = model.generate_content(prompt)
                    if res and res.text:
                        st.markdown('<div class="summary-output-card">', unsafe_allow_html=True)
                        st.markdown(res.text)
                        st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Gemini API Error: {str(e)}")

# -----------------------------------------------------------------------------
# TAB 2: PRIORITIES
# -----------------------------------------------------------------------------
with tab2:
    if retrieval_df.empty:
        st.info("No retrieval complaint dataset loaded. Please verify CSV files in directory.")
    else:
        st.markdown("""
        <div>
            <div class="md-section-title">What's going wrong in search, and what to fix first</div>
            <div class="md-section-caption">Comparing search friction volume against issue severity to prioritize fixes.</div>
        </div>
        """, unsafe_allow_html=True)
        
        category_counts = retrieval_df['problem_category'].value_counts()
        total_retrieval = len(retrieval_df)
        
        top_issue = category_counts.index[0] if not category_counts.empty else "N/A"
        top_share = (category_counts.iloc[0] / total_retrieval * 100) if not category_counts.empty else 0
        
        kpi1, kpi2, kpi3 = st.columns(3, gap="medium")
        with kpi1:
            st.markdown(f"""
            <div style="background-color: #F8F9FA; border: 1px solid #DADCE0; border-radius: 12px; padding: 20px; height: 100%;">
                <div style="font-size: 12px; line-height: 16px; font-weight: 500; color: #5F6368; margin-bottom: 8px;">Total Search Complaints</div>
                <div style="font-family: 'Google Sans', sans-serif; font-size: 32px; line-height: 40px; font-weight: 500; color: #202124;">{total_retrieval:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div style="background-color: #F8F9FA; border: 1px solid #DADCE0; border-radius: 12px; padding: 20px; height: 100%;">
                <div style="font-size: 12px; line-height: 16px; font-weight: 500; color: #5F6368; margin-bottom: 8px;">Top Search Friction Area</div>
                <div style="font-family: 'Google Sans', sans-serif; font-size: 24px; line-height: 30px; font-weight: 500; color: #202124; word-break: break-word;">{top_issue}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"""
            <div style="background-color: #F8F9FA; border: 1px solid #DADCE0; border-radius: 12px; padding: 20px; height: 100%;">
                <div style="font-size: 12px; line-height: 16px; font-weight: 500; color: #5F6368; margin-bottom: 8px;">Top Area Share</div>
                <div style="font-family: 'Google Sans', sans-serif; font-size: 32px; line-height: 40px; font-weight: 500; color: #202124;">{top_share:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("""
            <div style="font-family: 'Google Sans', sans-serif; font-size: 16px; font-weight: 500; color: #202124;">Search Issue Distribution</div>
            <div style="font-size: 12px; color: #5F6368; margin-bottom: 24px;">Total mentions per search friction category across user feedback.</div>
            """, unsafe_allow_html=True)
            fig_cats = render_horizontal_bar_chart(category_counts, x_label="Mentions", height=320)
            st.plotly_chart(fig_cats, use_container_width=True)

        with st.container(border=True):
            st.markdown("""
            <div style="font-family: 'Google Sans', sans-serif; font-size: 16px; font-weight: 500; color: #202124;">Fix-First Priority Score</div>
            <div style="font-size: 12px; color: #5F6368; margin-bottom: 16px;">Priority = volume share × frustration severity rating.</div>
            """, unsafe_allow_html=True)
            
            opp_data = []
            for cat, group in retrieval_df.groupby('problem_category'):
                count = len(group)
                pct = (count / total_retrieval) * 100
                scores = pd.to_numeric(group['user_score'], errors='coerce').dropna()
                avg_score = scores.mean() if not scores.empty else 2.5
                
                friction_factor = max(1.0, 5.0 - avg_score) if not scores.empty else 1.5
                raw_opp_score = pct * friction_factor
                opp_data.append({
                    "Search Issue": cat,
                    "Share": pct / 100.0,
                    "Raw Score": raw_opp_score
                })
                
            opp_df = pd.DataFrame(opp_data)
            max_raw = opp_df['Raw Score'].max() if not opp_df.empty else 1
            opp_df['Priority'] = (opp_df['Raw Score'] / max_raw) * 100
            opp_df = opp_df.drop(columns=['Raw Score']).sort_values(by='Priority', ascending=False)
            
            st.dataframe(
                opp_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Search Issue": st.column_config.TextColumn("Search Issue", width="large"),
                    "Share": st.column_config.ProgressColumn("Share of Issues", format="%.1f%%", min_value=0, max_value=1, width="medium"),
                    "Priority": st.column_config.ProgressColumn("Fix Priority", format="%.0f / 100", min_value=0, max_value=100, width="medium")
                }
            )

# -----------------------------------------------------------------------------
# TAB 3: MEMORY PATTERNS
# -----------------------------------------------------------------------------
with tab3:
    if not retrieval_df.empty:
        st.markdown("""
        <div>
            <div class="md-section-title">What people remember vs. what they forget</div>
            <div class="md-section-caption">Mapping emotional and visual cues against lost technical metadata.</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown('<div style="font-family: \'Google Sans\', sans-serif; font-size: 16px; font-weight: 500;">Details people remember</div>', unsafe_allow_html=True)
            rem_counts = retrieval_df['remembered_anchor'].value_counts().reset_index()
            rem_counts.columns = ['Memory Cue', 'Mentions']
            st.dataframe(rem_counts, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div style="font-family: \'Google Sans\', sans-serif; font-size: 16px; font-weight: 500;">Details people forget</div>', unsafe_allow_html=True)
            for_counts = retrieval_df['forgotten_anchor'].value_counts().reset_index()
            for_counts.columns = ['Forgotten Detail', 'Mentions']
            st.dataframe(for_counts, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# TAB 4: SEARCH EVIDENCE
# -----------------------------------------------------------------------------
with tab4:
    if not retrieval_df.empty:
        st.markdown("""
        <div>
            <div class="md-section-title">How people search when memory fails</div>
            <div class="md-section-caption">Analysis of search formulations and verbatim user feedback.</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            strategy_counts = retrieval_df['search_strategy'].value_counts()
            fig_strat = render_horizontal_bar_chart(strategy_counts, x_label="Posts Using Strategy", height=280)
            st.plotly_chart(fig_strat, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 5: ALL DATA
# -----------------------------------------------------------------------------
with tab5:
    st.markdown("""
    <div>
        <div class="md-section-title">Full Ingested Corpus Browser</div>
        <div class="md-section-caption">Inspect raw data rows, tagged metadata, and platform sources.</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        search_query_table = st.text_input("Filter table by keyword:", placeholder="e.g. receipt, date, album", key="corpus_search")
        
        display_df = retrieval_df.copy() if not retrieval_df.empty else pd.DataFrame()
        if search_query_table and not display_df.empty:
            display_df = display_df[display_df['full_text'].str.contains(search_query_table, case=False, na=False)]
            
        if not display_df.empty:
            st.dataframe(
                display_df[['source_platform', 'problem_category', 'search_strategy', 'remembered_anchor', 'forgotten_anchor', 'full_text']],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No matching feedback rows found.")
