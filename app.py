import streamlit as st
from database.db import init_db

st.set_page_config(
    page_title="Product2Shopify AI — by Trend & Brand",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Premium CSS Theme ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── Google Font ─── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ─── Global Reset & Font ─── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background-color: #090d16 !important;
    color: #f3f4f6 !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #090d16; }
::-webkit-scrollbar-thumb { background: #8b5cf6; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #7c3aed; }

/* ─── Main Container ─── */
[data-testid="stAppViewContainer"] > .main {
    background-color: #090d16 !important;
    padding: 0 !important;
}
.main .block-container {
    padding: 2rem 2.5rem 6rem 2.5rem !important;
    max-width: 1400px !important;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090d16 0%, #111827 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] .block-container { padding: 0 !important; }

/* Sidebar Decorative Line */
[data-testid="stSidebarNav"]::before {
    content: "";
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #8b5cf6, #6366f1, #3b82f6);
    margin-bottom: 12px;
}

/* Sidebar Nav Items */
[data-testid="stSidebarNav"] a {
    color: #9ca3af !important;
    border-radius: 8px !important;
    margin: 4px 12px !important;
    padding: 10px 14px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(139, 92, 246, 0.08) !important;
    color: #a78bfa !important;
    transform: translateX(4px) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, rgba(139, 92, 246, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%) !important;
    color: #c084fc !important;
    border-left: 3px solid #8b5cf6 !important;
    font-weight: 700 !important;
}

/* ─── Headings ─── */
h1 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    letter-spacing: -0.025em !important;
    padding-bottom: 0.6rem !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    margin-bottom: 1.5rem !important;
}
h2 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: #f3f4f6 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.75rem !important;
}
h3 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #e5e7eb !important;
    margin-top: 1.25rem !important;
    margin-bottom: 0.5rem !important;
}

/* ─── Metric Cards ─── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
    box-shadow: 0 10px 20px -5px rgba(139, 92, 246, 0.15) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 10px 20px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.35) !important;
    background: linear-gradient(135deg, #9b6bf7 0%, #7579f2 100%) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary button (type="secondary") */
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #d1d5db !important;
    box-shadow: none !important;
}
button[kind="secondary"]:hover {
    border-color: #8b5cf6 !important;
    color: #a78bfa !important;
    background: rgba(139, 92, 246, 0.06) !important;
    box-shadow: none !important;
}

/* ─── Inputs ─── */
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox select {
    background: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
    color: #f3f4f6 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
}

/* ─── Select / Multiselect ─── */
[data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
    color: #f3f4f6 !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
}

/* ─── Tabs ─── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 6px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #9ca3af !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 18px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s !important;
}
[data-baseweb="tab"]:hover { color: #f3f4f6 !important; background: rgba(255,255,255,0.03) !important; }
[aria-selected="true"][data-baseweb="tab"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #8b5cf6 !important;
    background: rgba(139, 92, 246, 0.06) !important;
}

/* ─── Dataframe / Data Editor ─── */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ─── Alert Boxes ─── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    font-size: 0.88rem !important;
}
[data-testid="stAlert"].stSuccess { background: rgba(16, 185, 129, 0.08) !important; border: 1px solid rgba(16, 185, 129, 0.2) !important; color: #34d399 !important; }
[data-testid="stAlert"].stWarning { background: rgba(245, 158, 11, 0.08) !important; border: 1px solid rgba(245, 158, 11, 0.2) !important; color: #fbbf24 !important; }
[data-testid="stAlert"].stError   { background: rgba(239, 68, 68, 0.08) !important; border: 1px solid rgba(239, 68, 68, 0.2) !important; color: #f87171 !important; }
[data-testid="stAlert"].stInfo    { background: rgba(59, 130, 246, 0.08) !important; border: 1px solid rgba(59, 130, 246, 0.2) !important; color: #60a5fa !important; }

/* ─── Progress Bar ─── */
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #8b5cf6, #6366f1) !important;
    border-radius: 4px !important;
}

/* ─── Expander ─── */
[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #d1d5db !important;
    font-weight: 600 !important;
}

/* ─── Radio & Checkbox ─── */
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label {
    color: #d1d5db !important;
    font-size: 0.9rem !important;
}

/* ─── Slider ─── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #8b5cf6 !important;
    border-color: #8b5cf6 !important;
}

/* ─── Divider ─── */
hr { border-color: rgba(255, 255, 255, 0.08) !important; }

/* ─── Sidebar Brand Header ─── */
.sidebar-brand {
    padding: 24px 20px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 12px;
}
.sidebar-brand .app-name {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
}
.sidebar-brand .app-tagline {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 4px;
}
.sidebar-brand .brand-link {
    display: inline-block;
    margin-top: 10px;
    font-size: 0.78rem;
    color: #a78bfa;
    font-weight: 700;
    text-decoration: none;
    transition: color 0.2s;
}
.sidebar-brand .brand-link:hover {
    color: #c084fc;
}

/* ─── Footer ─── */
.app-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    background: rgba(9, 13, 22, 0.8) !important;
    backdrop-filter: blur(12px);
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #9ca3af !important;
}
.app-footer a { color: #a78bfa !important; text-decoration: none; font-weight: 600; }
.app-footer a:hover { color: #c084fc !important; text-decoration: underline; }
.app-footer .footer-dot { margin: 0 8px; opacity: 0.4; }

/* ─── Selectbox dropdown ─── */
[data-baseweb="popover"] { background: #111827 !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 8px !important; }
[data-baseweb="menu"] li { color: #f3f4f6 !important; }
[data-baseweb="menu"] li:hover { background: rgba(139, 92, 246, 0.08) !important; }

/* ─── Download Button ─── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: none !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
    border-color: #8b5cf6 !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2) !important;
}

/* ─── Form ─── */
[data-testid="stForm"] {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px !important;
}

/* ─── Quick Action Cards ─── */
.quick-action-card {
    background: linear-gradient(135deg, #111827 0%, #1f2937 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 24px 20px !important;
    text-align: center !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
}
.quick-action-card:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(139, 92, 246, 0.4) !important;
    box-shadow: 0 12px 24px -10px rgba(139, 92, 246, 0.25) !important;
}
.quick-action-card .card-icon {
    font-size: 2.2rem !important;
    margin-bottom: 12px !important;
    transition: transform 0.25s ease !important;
}
.quick-action-card:hover .card-icon {
    transform: scale(1.15) !important;
}
.quick-action-card .card-title {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    margin-top: 4px !important;
}
.quick-action-card .card-desc {
    color: #9ca3af !important;
    font-size: 0.78rem !important;
    margin-top: 6px !important;
    line-height: 1.3 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar Branding ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
            <span style="font-size:1.6rem;">🛍️</span>
            <div>
                <div class="app-name">Product2Shopify AI</div>
                <div class="app-tagline">Shopify Catalog Builder</div>
            </div>
        </div>
        <a href="https://www.trendandbrands.com/" target="_blank" class="brand-link">
            🏷️ A Trend & Brand Product ↗
        </a>
    </div>
    """, unsafe_allow_html=True)

# ─── Page Registry ────────────────────────────────────────────────────────────
dashboard_page       = st.Page("pages/dashboard.py",       title="Dashboard",               icon="📊")
link_importer_page   = st.Page("pages/link_importer.py",   title="Product Link Importer",   icon="📥")
amazon_hunting_page  = st.Page("pages/amazon_hunting.py",  title="Amazon Product Hunting",  icon="🔎")
product_editor_page  = st.Page("pages/product_editor.py",  title="Product Editor",          icon="✏️")
sku_generator_page   = st.Page("pages/sku_generator.py",   title="SKU Generator",           icon="🏷️")
price_calculator_page= st.Page("pages/price_calculator.py",title="Price Calculator",        icon="🧮")
seo_tags_page        = st.Page("pages/seo_tags.py",        title="Tags & SEO Generator",    icon="🔍")
image_manager_page   = st.Page("pages/image_manager.py",   title="Image Manager",           icon="🖼️")
csv_validator_page   = st.Page("pages/csv_validator.py",   title="CSV Validator",           icon="✅")
exporter_page        = st.Page("pages/exporter.py",        title="Shopify CSV Exporter",    icon="📤")
import_history_page  = st.Page("pages/import_history.py",  title="Import History",          icon="⏳")
settings_page        = st.Page("pages/settings.py",        title="Settings",                icon="⚙️")
about_page           = st.Page("pages/about_policies.py",  title="About & Policies",        icon="📄")

pg = st.navigation({
    "🏠 Main": [dashboard_page],
    "📦 Product Import": [link_importer_page, amazon_hunting_page],
    "🛠️ Catalog Tools": [
        product_editor_page, sku_generator_page, price_calculator_page,
        seo_tags_page, image_manager_page
    ],
    "📤 Export & Validate": [csv_validator_page, exporter_page, import_history_page],
    "🔧 System": [settings_page, about_page]
})

pg.run()

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    <span>
        🛍️ <strong>Product2Shopify AI</strong>
        <span class="footer-dot">•</span>
        A product by <a href="https://www.trendandbrands.com/" target="_blank">Trend & Brand</a>
    </span>
    <span>
        <a href="https://www.trendandbrands.com/" target="_blank">Website</a>
        <span class="footer-dot">•</span>
        <a href="#" onclick="window.parent.document.querySelector('[data-testid=\\"stSidebarNav\\"] a:last-child').click()">Policies</a>
        <span class="footer-dot">•</span>
        © 2026 Trend & Brand
    </span>
</div>
""", unsafe_allow_html=True)
