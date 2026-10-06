# Steerable Photo Retrieval MVP

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

An executive prototype demonstrating **Model-Agnostic Vector Steering** and **Gemini 2.5 Flash Constraint Chips** to eliminate episodic search failures caused by Context Drift and EXIF-stripped messaging media.

---

## 🎯 Executive Summary & Problem Thesis

Standard search in photo applications (Google Photos, Apple Photos) relies heavily on either static EXIF metadata (date, time, location) or strict text-to-image semantic matching. This creates critical failure modes:

1. **Messaging Media Blindspot:** Media downloaded via WhatsApp, Telegram, or Signal has camera EXIF stripped, rendering date/location queries ineffective.
2. **Context Drift:** Users searching for complex visual subjects (e.g., *"brass table lamp"*) experience scan fatigue when results display unwanted adjacent objects (e.g., *"sofas"* or *"floor rugs"*).
3. **Lack of Negative Controls:** Traditional text search lacks a mechanisms to say: *"Show me photos like this (+1), but exclude elements like that (-1)."*

---

## 🏗️ Architecture & Technical Solution

┌──────────────────┐    ┌───────────────────────────┐    ┌────────────────────────┐
│  User Query &    │────>│ Gemini 2.5 Flash Parser   │────>│ Temporal / Constraint  │
│  Feedback (+1/-1)│    │ (Structured Chip Extraction)│   │ Constraint Chips (F3)  │
└──────────────────┘    └───────────────────────────┘    └────────────────────────┘
│                                                           │
▼                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ SigLIP-SO400M Vector Steering Engine (1152-D Space)                            │
│ Formula: V_steered = Normalize(α · V_query + β · E_pos - γ · E_neg)            │
└─────────────────────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Cosine Similarity Ranking + Soft Temporal Prior Shift (+0.08 offset)            │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 🔬 Core Features

- **Feature F1 (SigLIP Vector Arithmetic):** Dynamically steers search vectors using positive exemplar centroids ($\bar{E}_{pos}$) and negative exclusion centroids ($\bar{E}_{neg}$).
- **Feature F2 (Gemini 2.5 Flash Parser):** Extracts intent chips from messy natural language queries without breaking embedding execution.
- **Feature F3 (EXIF-Neutral Temporal Prior):** Boosts relevance scores ($+0.08$ shift) when explicit temporal chips match messaging media without camera EXIF tags.
- **Feature F4 (Live Telemetry Inspector):** Provides real-time visibility into mathematical operations and parsed JSON constraints.

---

## ⚡ Quickstart (Local Execution)

```bash
git clone [https://github.com/hrishikeshhdatar/mvp_steerable_photos.git](https://github.com/hrishikeshhdatar/mvp_steerable_photos.git)
cd mvp_steerable_photos
pip install -r requirements.txt
streamlit run app.py

---

### Step-by-Step GitHub Commit Checklist

1. **Update `app.py`:** Edit `app.py` on GitHub, replace with the code in File 1, and commit.
2. **Update `parser.py`:** Edit `parser.py` on GitHub, replace with the code in File 2, and commit.
3. **Update `README.md`:** Edit `README.md` on GitHub, replace with File 3, and commit.

Once committed, Streamlit Cloud will automatically rebuild. Open your live app link to experience your executive-ready, Top 1% PM deliverable.
