# 🔍 Steerable Photo Retrieval MVP

> *Resolving Episodic Search Failures on EXIF-Stripped Messaging Media via Front-End Vector Steering ($V_{\text{steered}}$) and Gemini 2.5 Flash Stateful Chips.*

---

## 📌 Executive Summary

Family archivists frequently struggle to locate shared media (e.g., WhatsApp/Telegram photos) because messaging applications strip EXIF metadata (dates, GPS tags). Single-pass text queries in existing photo platforms lead to **Conversational Context Drift** and **Scan Fatigue** when targets are buried past position #20.

This MVP introduces a **real-time visual steering layer**:
1. **$+1$ / $-1$ Vector Arithmetic:** Instantly pulls active candidate grids toward preferred visual attributes or pushes away unwanted clutter.
2. **Stateful Constraint Chips:** Maintains active prompt criteria across search turns using Gemini 2.5 Flash to prevent context loss.
3. **Conditional Time Prior:** Applies a non-punitive $+0.08$ score boost only when an explicit temporal filter is active, preserving visibility for EXIF-stripped media.

---

## 🛠️ Architecture

┌────────────────┐     ┌────────────────────────────┐     ┌──────────────────────┐
│ User Query /   │ ──► │ SigLIP SO400M Vector Index │ ──► │ Candidate Grid       │
│ Memory Anchors │     │ (1152-Dim Dense Embeddings)│     │ (Top 20 Ranked Pool) │
└────────────────┘     └────────────────────────────┘     └──────────┬───────────┘
│
▼
┌────────────────┐     ┌────────────────────────────┐     ┌──────────────────────┐
│ Interactive    │ ◄── │ Vector Shift Engine        │ ◄── │ Direct UI Controls   │
│ Re-Ranked Grid │     │ (<300ms Sub-Second Shift)  │     │ (+1 Like / -1 Not)   │
└────────────────┘     └────────────────────────────┘     └──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Gemini 2.5 Flash     │
│ Stateful Chip Parser │
└──────────────────────┘

---

## 📐 Vector Steering Mathematics

When users tap **"+1 Like"** ($I_{\text{pos}}$) or **"-1 Not"** ($I_{\text{neg}}$) on result thumbnails, the retrieval engine updates the active query vector dynamically:

$$V_{\text{new}} = \text{Normalize}\left( \alpha \cdot V_{\text{query}} + \beta \cdot \bar{E}_{\text{pos}} - \gamma \cdot \bar{E}_{\text{neg}} \right)$$

* $\alpha = 0.5$ (Base Text Query Anchor)
* $\beta = 0.4$ (Positive Visual Attraction)
* $\gamma = 0.2$ (Negative Visual Suppression)

---

## 🚀 Quick Start & Local Setup

### 1. Clone & Install Dependencies
```bash
git clone [https://github.com/hrishikeshhdatar/mvp_steerable_photos.git](https://github.com/hrishikeshhdatar/mvp_steerable_photos.git)
cd mvp_steerable_photos
pip install -r requirements.txt
