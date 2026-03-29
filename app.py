"""
Aether — Procedural Ambient Synthesizer
========================================
A browser-based ambient music synthesizer powered by the Web Audio API.
All synthesis happens client-side — no backend AI calls needed.
NLP mood tokens are mapped to DSP synthesis parameters via a rule-based engine.

Author: Muhammad Fahad Hassan (MFH-001)
HF Space: huggingface.co/spaces/MFH-001/Aether-Synth
GitHub:   github.com/mfh-001/Aether-Synth
"""

import streamlit as st

st.set_page_config(
    page_title="Aether — Procedural Ambient Synthesizer",
    page_icon="🎛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome (header, footer, menu)
st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stApp { background: #03040a; }
    iframe { border: none; }
</style>
""", unsafe_allow_html=True)

# Read and embed the HTML app
with open("index.html", "r") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=2000, scrolling=True)
