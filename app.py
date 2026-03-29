import streamlit as st
import os
from tabs.tracking import render_tracking_tab
from tabs.trailer import render_trailer_tab

# Page configuration
st.set_page_config(
    page_title="AUVISEGTRA",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Premium Design System with Mobile Responsiveness ─────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
    /* ── CSS Custom Properties (Design Tokens) ── */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: #1a1f35;
        --bg-card-hover: #1f2847;
        --border-subtle: rgba(99, 102, 241, 0.15);
        --border-glow: rgba(99, 102, 241, 0.4);
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --accent-tertiary: #ec4899;
        --accent-success: #10b981;
        --accent-warning: #f59e0b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --gradient-brand: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        --gradient-card: linear-gradient(145deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.04) 100%);
        --gradient-glow: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(236,72,153,0.2));
        --shadow-card: 0 4px 24px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.2);
        --shadow-glow: 0 0 30px rgba(99,102,241,0.15);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
        --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-smooth: 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ── Global Reset & Base ── */
    .main, .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary);
        font-family: var(--font-body) !important;
    }

    .block-container {
        padding: 1.5rem 2rem 3rem 2rem !important;
        max-width: 1400px !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--accent-primary); border-radius: 10px; }

    /* ── Brand Header ── */
    .brand-header {
        text-align: center;
        padding: 2rem 1rem 1.5rem;
        position: relative;
    }
    .brand-header::before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 200px; height: 3px;
        background: var(--gradient-brand);
        border-radius: 2px;
    }
    .brand-title {
        font-size: clamp(2rem, 5vw, 3.2rem);
        font-weight: 900;
        letter-spacing: 6px;
        background: var(--gradient-brand);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: clamp(0.75rem, 2vw, 0.95rem);
        color: var(--text-secondary);
        font-weight: 400;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }
    .brand-badge {
        display: inline-block;
        margin-top: 1rem;
        padding: 4px 14px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 20px;
        font-size: 0.7rem;
        color: var(--accent-primary);
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Typography ── */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-body) !important;
        background: var(--gradient-brand) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 700 !important;
    }

    p, span, label, .stMarkdown p {
        font-family: var(--font-body) !important;
        color: var(--text-secondary);
    }

    /* ── Tabs (Premium Pill Style) ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: 6px;
        border: 1px solid var(--border-subtle);
        justify-content: center;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: nowrap;
        background: transparent;
        border-radius: var(--radius-md);
        color: var(--text-muted);
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0 20px;
        transition: var(--transition-fast);
        border: none;
        font-family: var(--font-body) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: rgba(99, 102, 241, 0.08);
    }
    .stTabs [aria-selected="true"] {
        background: var(--gradient-brand) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 1rem;
    }

    /* ── Metric Cards ── */
    [data-testid="stMetric"] {
        background: var(--gradient-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1rem;
        transition: var(--transition-smooth);
        box-shadow: var(--shadow-card);
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--border-glow);
        box-shadow: var(--shadow-glow);
        transform: translateY(-2px);
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: var(--gradient-brand) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        font-family: var(--font-body) !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.9rem !important;
        transition: var(--transition-smooth) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.45) !important;
    }
    .stButton > button:active {
        transform: translateY(0px);
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        font-family: var(--font-body) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stFileUploader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
        transition: var(--transition-fast) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* ── Data Frames ── */
    .stDataFrame {
        border-radius: var(--radius-md) !important;
        overflow: hidden;
        border: 1px solid var(--border-subtle) !important;
    }

    /* ── Container / Cards ── */
    [data-testid="stExpander"],
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] > div:has(> div > div[data-testid="stVerticalBlock"]) {
        background: var(--gradient-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-card);
    }

    /* ── Progress Bar ── */
    .stProgress > div > div > div {
        background: var(--gradient-brand) !important;
        border-radius: 10px;
    }
    .stProgress > div > div {
        background: var(--bg-card) !important;
        border-radius: 10px;
    }

    /* ── Slider ── */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--accent-primary) !important;
        border-color: var(--accent-primary) !important;
    }

    /* ── Status / Spinner ── */
    .stStatusWidget, [data-testid="stStatusWidget"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ── Divider ── */
    hr {
        border-color: var(--border-subtle) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Video Player ── */
    video, .stVideo {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle);
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1rem !important;
        transition: var(--transition-fast);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-primary) !important;
    }

    /* ── Plotly Charts ── */
    .js-plotly-plot .plotly .modebar {
        background: var(--bg-card) !important;
        border-radius: var(--radius-sm);
    }

    /* ── Info / Warning / Success Alerts ── */
    .stAlert > div {
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
    }

    /* ─────────────────────────────────────────────────── */
    /* ── MOBILE RESPONSIVENESS                       ── */
    /* ─────────────────────────────────────────────────── */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.75rem 2rem 0.75rem !important;
        }

        .brand-title {
            font-size: 1.8rem;
            letter-spacing: 3px;
        }
        .brand-subtitle {
            font-size: 0.7rem;
            letter-spacing: 1.5px;
        }

        /* Stack columns vertically */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.75rem !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Tabs scroll horizontally on mobile */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            flex-wrap: nowrap;
            -webkit-overflow-scrolling: touch;
            padding: 4px;
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem;
            padding: 0 12px;
            height: 38px;
            flex-shrink: 0;
        }

        /* Metric cards compact */
        [data-testid="stMetric"] {
            padding: 0.75rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }

        /* Buttons full width */
        .stButton > button,
        .stDownloadButton > button {
            width: 100% !important;
        }

        /* Sidebar collapses */
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }

        h1, .stMarkdown h1 { font-size: 1.4rem !important; }
        h2, .stMarkdown h2 { font-size: 1.15rem !important; }
        h3, .stMarkdown h3 { font-size: 1rem !important; }
    }

    @media (max-width: 480px) {
        .block-container {
            padding: 0.5rem 0.5rem 1.5rem 0.5rem !important;
        }

        .brand-title {
            font-size: 1.4rem;
            letter-spacing: 2px;
        }
        .brand-badge {
            font-size: 0.6rem;
            padding: 3px 10px;
        }

        [data-testid="stMetric"] {
            padding: 0.5rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
        }
    }

    /* ── Tablet ── */
    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding: 1.5rem 1.5rem 2rem 1.5rem !important;
        }
    }

    /* ── Animations ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 15px rgba(99,102,241,0.15); }
        50% { box-shadow: 0 0 30px rgba(99,102,241,0.3); }
    }

    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }

    /* ── Hide default Streamlit elements ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # ── Brand Header ──
    st.markdown("""
    <div class="brand-header fade-in">
        <h1 class="brand-title" style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AUVISEGTRA</h1>
        <p class="brand-subtitle">Audio · Visual · Segmentation · Tracking</p>
        <span class="brand-badge">🎬 Multimodal Intelligence Engine v2.0</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <span style="font-size: 2rem;">⚙️</span>
            <h3 style="margin: 0.5rem 0 0; font-size: 1rem;">Configuration</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Fusion Weights")
        alpha = st.slider("Visual Weight (α)", 0.0, 1.0, 0.7, 0.05,
                          help="Weight for Face Similarity in cross-scene matching")
        beta = st.slider("Audio Weight (β)", 0.0, 1.0, 0.3, 0.05,
                         help="Weight for Speaker Similarity in cross-scene matching")

        # Normalize weights if necessary
        total = alpha + beta
        if total > 0 and total != 1.0:
            norm_alpha = alpha / total
            norm_beta = beta / total
            st.info(f"Normalized: α = {norm_alpha:.2f}, β = {norm_beta:.2f}")

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; padding: 0.5rem 0; opacity: 0.5;">
            <small>Built with Streamlit · PyTorch · Groq</small>
        </div>
        """, unsafe_allow_html=True)

    # ── Main Tabs ──
    tab1, tab2 = st.tabs(["🔍  Character Tracking", "🎬  Trailer Intelligence"])

    with tab1:
        render_tracking_tab(alpha, beta)

    with tab2:
        render_trailer_tab()


if __name__ == "__main__":
    main()
