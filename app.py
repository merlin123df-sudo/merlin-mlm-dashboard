# Streamlit Cloud expects streamlit_app.py or app.py
# This script renders the Merlin MLM dashboard
import streamlit as st
from pipeline import run_pipeline
from ml_engine import (
    get_inventory_gap, 
    get_logistics_summary,
    get_b2b_analytics,
    get_d2c_analytics,
    get_production_metrics,
    predict_warehouse_locations,
    get_supply_chain_metrics
)
import pandas as pd
import os
import time

try:
    import pydeck as pdk
    PYDECK_AVAILABLE = True
except ImportError:
    pdk = None
    PYDECK_AVAILABLE = False

# Caching functions to load data smoothly
@st.cache_data(ttl=60)  # TTL reduced for faster refresh
def cached_inventory_gap():
    try:
        return get_inventory_gap()
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def cached_logistics_summary(start_date, end_date):
    try:
        return get_logistics_summary(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading logistics data: {e}")
        return {}

@st.cache_data(ttl=60)
def cached_b2b_analytics(start_date, end_date):
    try:
        return get_b2b_analytics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading B2B data: {e}")
        return {'summary': {}, 'top_clients': pd.DataFrame(), 'payment_modes': pd.DataFrame()}

@st.cache_data(ttl=60)
def cached_d2c_analytics(start_date, end_date):
    try:
        return get_d2c_analytics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading D2C data: {e}")
        return {'summary': {}, 'top_cities': pd.DataFrame(), 'payment_modes': pd.DataFrame()}

@st.cache_data(ttl=60)
def cached_production_metrics(start_date, end_date):
    try:
        return get_production_metrics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading production metrics: {e}")
        return {'metrics': pd.DataFrame(), 'summary': {}}

@st.cache_data(ttl=60)
def cached_warehouse_prediction():
    try:
        return predict_warehouse_locations(top_n=5)
    except Exception as e:
        st.error(f"Error loading warehouse predictions: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def cached_supply_chain_metrics(start_date, end_date):
    try:
        return get_supply_chain_metrics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading supply chain metrics: {e}")
        return {'courier_metrics': pd.DataFrame(), 'route_data': pd.DataFrame(), 'total_couriers': 0}

# Page configuration
st.set_page_config(
    page_title="Merlin MLM Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Merlin MLM Operations Dashboard - Premium Edition"
    }
)

# Theme Toggle and Premium Style
theme_options = ["🌙 Dark", "☀️ Light"]
col_theme1, col_theme2, col_theme3 = st.columns([3, 1, 1])
with col_theme3:
    theme_toggle = st.selectbox(
        "Theme",
        theme_options,
        index=0,
        label_visibility="collapsed"
    )

dark_mode = theme_toggle.startswith("🌙")

bg_color = "#0F1419" if dark_mode else "#F8F9FA"
card_color = "rgba(15, 20, 25, 0.75)" if dark_mode else "rgba(255, 255, 255, 0.85)"
text_color = "#F8F9FA" if dark_mode else "#111827"
muted_text = "#A8B2C1" if dark_mode else "#6B7280"
page_border = "rgba(255,255,255,0.08)" if dark_mode else "rgba(15,23,42,0.08)"
primary = "#2E86AB"
secondary = "#A23B72"
accent = "#F18F01"

st.markdown(f"""
<style>
    :root {{
        --bg-color: {bg_color};
        --card-color: {card_color};
        --text-color: {text_color};
        --muted-text: {muted_text};
        --primary-color: {primary};
        --secondary-color: {secondary};
        --accent-color: {accent};
        --card-border: {page_border};
    }}

    body, .block-container, .stApp {{
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }}

    * {{
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }}

    .main-title {{
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        color: transparent;
        margin-bottom: 1.25rem;
    }}

    .dashboard-card, .stMetric, .stDataFrame {{
        background: var(--card-color) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 22px !important;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.12);
        backdrop-filter: blur(18px);
        padding: 1.25rem !important;
    }}

    .subheader-modern {{
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.6rem;
        border-bottom: 3px solid var(--accent-color);
    }}

    .alert-success, .alert-warning, .alert-error {{
        border-radius: 16px;
        padding: 1rem 1.15rem;
        font-size: 0.95rem;
        line-height: 1.5;
    }}

    .alert-success {{
        background-color: rgba(6, 167, 125, 0.14);
        border-left: 4px solid #06A77D;
        color: #D2F1E0;
    }}

    .alert-warning {{
        background-color: rgba(241, 143, 1, 0.14);
        border-left: 4px solid #F18F01;
        color: #FFF4D1;
    }}

    .alert-error {{
        background-color: rgba(193, 18, 31, 0.14);
        border-left: 4px solid #C1121F;
        color: #FEE2E2;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--text-color) !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--muted-text) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }}

    .streamlit-expanderHeader {{
        font-weight: 700 !important;
        color: var(--text-color) !important;
    }}

    /* Sidebar Enhancements */
    .sidebar .sidebar-content {{
        background: var(--card-color) !important;
        border-right: 1px solid var(--card-border) !important;
        position: sticky !important;
        top: 0 !important;
        height: 100vh !important;
        overflow-y: auto !important;
    }}

    .sidebar-header {{
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: var(--primary-color) !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid var(--accent-color) !important;
    }}

    .sidebar-section {{
        background: rgba(255,255,255,0.02) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid var(--card-border) !important;
    }}

    .sidebar-section h3 {{
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: var(--secondary-color) !important;
        margin-bottom: 1rem !important;
        margin-top: 0 !important;
    }}

    .sidebar-radio label {{
        display: flex !important;
        align-items: center !important;
        padding: 0.5rem 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        border-radius: 8px !important;
        margin-bottom: 0.25rem !important;
    }}

    .sidebar-radio label:hover {{
        background: rgba(46, 134, 171, 0.1) !important;
        color: var(--primary-color) !important;
    }}

    .sidebar-radio input[type="radio"]:checked + label {{
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(46, 134, 171, 0.3) !important;
        font-weight: 600 !important;
    }}

    .sidebar-radio input[type="radio"] {{
        display: none !important;
    }}

    .sidebar-radio label:before {{
        content: attr(data-icon) !important;
        margin-right: 0.75rem !important;
        font-size: 1.2rem !important;
        transition: transform 0.2s ease !important;
    }}

    .sidebar-radio label:hover:before {{
        transform: scale(1.1) !important;
    }}

    .quick-action-btn {{
        width: 100% !important;
        margin-bottom: 0.5rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }}

    .quick-action-btn:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }}

    .collapsible-section {{
        margin-bottom: 1rem !important;
    }}

    .collapsible-header {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        cursor: pointer !important;
        padding: 0.5rem 0 !important;
        font-weight: 600 !important;
        color: var(--text-color) !important;
        transition: color 0.2s ease !important;
    }}

    .collapsible-header:hover {{
        color: var(--primary-color) !important;
    }}

    .collapsible-content {{
        max-height: 0 !important;
        overflow: hidden !important;
        transition: max-height 0.3s ease !important;
    }}

    .collapsible-content.open {{
        max-height: 500px !important;
    }}

    @media (max-width: 900px) {{
        .main-title {{ font-size: 2.2rem; }}
        .stMetric {{ padding: 1rem !important; }}
        .dashboard-card {{ padding: 1rem !important; }}
        .subheader-modern {{ font-size: 1.25rem; }}
        .sidebar .sidebar-content {{
            position: relative !important;
            height: auto !important;
        }}
    }}

    @media (max-width: 600px) {{
        .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; }}
        .stMarkdown {{ margin: 0 !important; }}
    }}
</style>
""", unsafe_allow_html=True)

CITY_COORDS = {
    'FARIDABAD': [28.4089, 77.3178],
    'DELHI': [28.7041, 77.1025],
    'GURGAON': [28.4595, 77.0266],
    'NOIDA': [28.5355, 77.3910],
    'MUMBAI': [19.0760, 72.8777],
    'KOLKATA': [22.5726, 88.3639],
    'BENGALURU': [12.9716, 77.5946],
    'BANGALORE': [12.9716, 77.5946],
    'CHENNAI': [13.0827, 80.2707],
    'HYDERABAD': [17.3850, 78.4867],
    'PUNE': [18.5204, 73.8567],
    'SURAT': [21.1702, 72.8311],
    'JAIPUR': [26.9124, 75.7873],
    'LUCKNOW': [26.8467, 80.9462],
    'PATNA': [25.5941, 85.1376],
    'AHMEDABAD': [23.0225, 72.5714],
    'KATHUA': [32.3976, 75.5232],
    'BENGALURU': [12.9716, 77.5946],
    'RAIPUR': [21.2514, 81.6296]
}

def get_city_coords(city_name):
    city_name = str(city_name or '').upper().strip()
    if city_name in CITY_COORDS:
        return CITY_COORDS[city_name]
    for key in CITY_COORDS:
        if key in city_name:
            return CITY_COORDS[key]
    return None

st.markdown('<h1 class="main-title">📊 Merlin MLM Dashboard</h1>', unsafe_allow_html=True)

# Sidebar styling and layout
st.sidebar.markdown('<div class="sidebar-section"><h2 class="sidebar-header">⚙️ Control Panel</h2></div>', unsafe_allow_html=True)

# Upload section
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: var(--muted-text); font-size: 0.9rem; margin-bottom: 1rem;'>Upload raw dispatch, SO, CLICKPOST, or kitting CSV/XLSX files for sync.</p>", unsafe_allow_html=True)
uploaded_files = st.sidebar.file_uploader(
    "Upload files",
    type=['csv', 'xlsx'],
    accept_multiple_files=True,
    help="Upload files here and then sync the dashboard.",
    label_visibility="collapsed"
)
if uploaded_files:
    os.makedirs('raw_data', exist_ok=True)
    saved = []
    for uploaded_file in uploaded_files:
        save_path = os.path.join('raw_data', uploaded_file.name)
        with open(save_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        saved.append(uploaded_file.name)
    if saved:
        st.sidebar.success(f"Saved {len(saved)} files to raw_data!")

# Quick action buttons
col_sync1, col_sync2 = st.sidebar.columns(2)
with col_sync1:
    if st.sidebar.button("🔄 Sync", key="sync_btn", help="Sync the latest data"):
        with st.spinner("Syncing data..."):
            success, message = run_pipeline()
        if success:
            st.sidebar.success("Data sync completed!")
            st.cache_data.clear()
        else:
            st.sidebar.error(message)

with col_sync2:
    if st.sidebar.button("🗑️ Clear", key="clear_btn", help="Clear cached data"):
        st.cache_data.clear()
        st.sidebar.success("Cache cleared!")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Date Filters
st.sidebar.markdown('<div class="sidebar-section"><h3 class="sidebar-header">📅 Date Filters</h3>', unsafe_allow_html=True)

start_date = st.sidebar.date_input("From", value=pd.to_datetime("2026-05-01"), label_visibility="collapsed")
end_date = st.sidebar.date_input("To", value=pd.to_datetime("2026-05-09"), label_visibility="collapsed")

# Quick filter buttons
if st.sidebar.button("🔄 Refresh", key="refresh_filters", help="Refresh dashboard filters"):
    st.cache_data.clear()
    st.sidebar.success("Filters refreshed!")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-section"><h3 class="sidebar-header">📊 Navigation</h3></div>', unsafe_allow_html=True)

tabs = [
    "📈 Overview",
    "🏢 B2B Analytics",
    "👥 D2C Analytics",
    "🏭 Production",
    "🔮 Warehouse Prediction",
    "⛓️ Supply Chain"
]

tab_selection = st.sidebar.radio("Navigation", tabs, index=0, label_visibility="collapsed")

# Load data based on selected tab for speed
with st.spinner("Loading data..."):
    if tab_selection == "📈 Overview":
        gap_data = cached_inventory_gap()
        log_data = cached_logistics_summary(start_date, end_date)
        b2b_data = d2c_data = prod_data = warehouse_pred = supply_chain = None
    elif tab_selection == "🏢 B2B Analytics":
        b2b_data = cached_b2b_analytics(start_date, end_date)
        gap_data = log_data = d2c_data = prod_data = warehouse_pred = supply_chain = None
    elif tab_selection == "👥 D2C Analytics":
        d2c_data = cached_d2c_analytics(start_date, end_date)
        gap_data = log_data = b2b_data = prod_data = warehouse_pred = supply_chain = None
    elif tab_selection == "🏭 Production":
        prod_data = cached_production_metrics(start_date, end_date)
        gap_data = log_data = b2b_data = d2c_data = warehouse_pred = supply_chain = None
    elif tab_selection == "🔮 Warehouse Prediction":
        warehouse_pred = cached_warehouse_prediction()
        gap_data = log_data = b2b_data = d2c_data = prod_data = supply_chain = None
    elif tab_selection == "⛓️ Supply Chain":
        supply_chain = cached_supply_chain_metrics(start_date, end_date)
        gap_data = log_data = b2b_data = d2c_data = prod_data = warehouse_pred = None
    else:
        gap_data = cached_inventory_gap()
        log_data = cached_logistics_summary(start_date, end_date)
        b2b_data = d2c_data = prod_data = warehouse_pred = supply_chain = None

# TAB-BASED DASHBOARD
if tab_selection == "📈 Overview":
    # ===== OVERVIEW TAB =====
    st.markdown('<h2 class="subheader-modern">📊 Operational Overview</h2>', unsafe_allow_html=True)
    
    # Alerts
    if log_data and 'summary' in log_data:
        summary = log_data['summary']
        total_disp = summary.get('total_dispatched', 0)
        total_rto = summary.get('total_rto', 0)
        if total_disp > 0:
            rto_rate = (total_rto / total_disp) * 100
            if rto_rate > 3:
                st.markdown(f'<div class="alert-warning">⚠️ High RTO Rate: {rto_rate:.1f}% (Above 3% threshold)</div>', unsafe_allow_html=True)
        
        delivery_rate = (summary.get('total_delivered', 0) / total_disp) * 100 if total_disp > 0 else 0
        if delivery_rate < 80:
            st.markdown(f'<div class="alert-error">❌ Low Delivery Rate: {delivery_rate:.1f}% (Below 80% threshold)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-success">✓ Healthy Delivery Rate: {delivery_rate:.1f}% (Above 80%)</div>', unsafe_allow_html=True)
    
    if not gap_data.empty:
        negative_gaps = gap_data[gap_data['Gap'] < 0]
        if not negative_gaps.empty:
            st.markdown(f'<div class="alert-error">❌ Over-dispatched items: {len(negative_gaps)} SKUs have negative gaps</div>', unsafe_allow_html=True)
    
    # Inventory Gap
    st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📦 Inventory Gap Analysis</h3>', unsafe_allow_html=True)
    if not gap_data.empty:
        st.dataframe(gap_data.head(50), width='stretch')  # Limited to 50 rows for speed
        if len(gap_data) > 50:
            st.info(f"Total {len(gap_data)} rows available. Showing first 50 for performance.")
    else:
        st.info("No inventory data available.")
    
    # Key Metrics
    if log_data and 'summary' in log_data:
        st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📊 Key Logistics Metrics</h3>', unsafe_allow_html=True)
        summary = log_data.get('summary', {})
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📤 Dispatched", summary.get('total_dispatched', 0))
        col2.metric("✓ Delivered", summary.get('total_delivered', 0))
        col3.metric("↩️ RTO", summary.get('total_rto', 0))
        col4.metric("💰 Revenue", f"₹{summary.get('total_revenue', 0):,.0f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            shipment_dist = log_data.get('shipment_dist')
            if shipment_dist is not None and not shipment_dist.empty:
                st.markdown('<h3 style="color: #2E86AB; font-size: 1rem; font-weight: 600;">📦 Shipment Distribution</h3>', unsafe_allow_html=True)
                dist_chart = shipment_dist.pivot(index='Courier Partner', columns='Payment Mode', values='Count').fillna(0)
                st.bar_chart(dist_chart)
        
        with col2:
            top_cities = log_data.get('top_cities')
            if top_cities is not None and not top_cities.empty:
                st.markdown('<h3 style="color: #A23B72; font-size: 1rem; font-weight: 600;">🏙️ Top Cities</h3>', unsafe_allow_html=True)
                st.bar_chart(top_cities.set_index('City'))
        
        # RTO Locations
        rto_locations = log_data.get('rto_locations')
        if rto_locations is not None and not rto_locations.empty:
            st.markdown('<h3 style="color: #C1121F; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">⚠️ Top RTO Locations</h3>', unsafe_allow_html=True)
            st.bar_chart(rto_locations.set_index('City'))

elif tab_selection == "🏢 B2B Analytics":

    # ===== B2B TAB =====
    b2b_data = cached_b2b_analytics(start_date, end_date)
    
    st.markdown('<h2 class="subheader-modern">🏢 B2B Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    if b2b_data and b2b_data['summary']:
        summary = b2b_data['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Orders", summary.get('total_orders', 0))
        col2.metric("✓ Delivered", summary.get('delivered', 0))
        col3.metric("📤 Delivery Rate", f"{summary.get('delivery_rate', 0):.1f}%")
        col4.metric("📈 Partial Delivery", f"{summary.get('partial_delivery_pct', 0):.1f}%")
        
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">💰 Financial Metrics</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Revenue", f"₹{summary.get('total_revenue', 0):,.0f}")
        col2.metric("Total Quantity", f"{summary.get('total_qty', 0):.0f} units")
        
        st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🎯 Top B2B Clients</h3>', unsafe_allow_html=True)
        top_clients = b2b_data.get('top_clients', pd.DataFrame())
        if not top_clients.empty:
            st.dataframe(top_clients.head(20), width='stretch')  # Limited to 20 rows for speed
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(top_clients.set_index('Client')[['Orders']])
            with col2:
                st.bar_chart(top_clients.set_index('Client')[['Revenue']])
        
        channel_summary = b2b_data.get('channel_summary', pd.DataFrame())
        if not channel_summary.empty:
            st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🌐 Channel Distribution</h3>', unsafe_allow_html=True)
            st.bar_chart(channel_summary.set_index('Channel'))
    else:
        st.warning("No B2B data available for the selected date range")

elif tab_selection == "👥 D2C Analytics":

    # ===== D2C TAB =====
    d2c_data = cached_d2c_analytics(start_date, end_date)
    
    st.markdown('<h2 class="subheader-modern">👥 D2C Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    if d2c_data and d2c_data['summary']:
        summary = d2c_data['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Orders", summary.get('total_orders', 0))
        col2.metric("✓ Delivered", summary.get('delivered', 0))
        col3.metric("🚚 In Transit", summary.get('in_transit', 0))
        col4.metric("↩️ RTO", summary.get('rto', 0))
        
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">💰 Financial Metrics</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Revenue", f"₹{summary.get('total_revenue', 0):,.0f}")
        col2.metric("Total Quantity", f"{summary.get('total_qty', 0):.0f} units")
        
        st.markdown('<h3 style="color: #06A77D; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🏙️ Top D2C Cities</h3>', unsafe_allow_html=True)
        top_cities = d2c_data.get('top_cities', pd.DataFrame())
        if not top_cities.empty:
            st.dataframe(top_cities, width='stretch')
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(top_cities.set_index('City')[['Orders']])
            with col2:
                st.bar_chart(top_cities.set_index('City')[['Revenue']])
        
        payment_split = d2c_data.get('payment_split', pd.DataFrame())
        if not payment_split.empty:
            st.markdown('<h3 style="color: #F18F01; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">💳 COD vs Prepaid Split</h3>', unsafe_allow_html=True)
            st.bar_chart(payment_split.set_index('Mode'))

        city_rto = d2c_data.get('city_rto', pd.DataFrame())
        if not city_rto.empty:
            st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📍 City-wise RTO %</h3>', unsafe_allow_html=True)
            st.bar_chart(city_rto.set_index('Drop City')[['RTO %']])
    else:
        st.warning("No D2C data available for the selected date range")

elif tab_selection == "Production":
    # ===== PRODUCTION TAB =====
    prod_data = cached_production_metrics(start_date, end_date)
    
    st.markdown('<h2 class="subheader-modern">🏭 Production Location Metrics and KPIs</h2>', unsafe_allow_html=True)
    
    if prod_data and prod_data['summary']:
        summary = prod_data['summary']
        
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600;">📊 Production KPIs</h3>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Orders", summary.get('total_orders', 0))
        col2.metric("📈 Kitting→Dispatch Conversion", f"{summary.get('kitting_to_dispatch_conversion', 0):.1f}%")
        col3.metric("⏳ Pending SO", summary.get('pending_so', 0))
        col4.metric("🛠️ Make Quantity", summary.get('make_quantity', 0))
        
        st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📈 Total Revenue</h3>', unsafe_allow_html=True)
        st.metric("", f"₹{summary.get('total_revenue', 0):,.0f}")
        
        pending_sku = prod_data.get('pending_sku', pd.DataFrame())
        if not pending_sku.empty:
            st.markdown('<h3 style="color: #F18F01; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📦 SKU-level Pending SO Tracker</h3>', unsafe_allow_html=True)
            st.dataframe(pending_sku[['ItemNo', 'OrderedQty', 'Stock in Hand', 'PendingSO', 'MakeQty']], width='stretch')

        production_stage = prod_data.get('production_stage', pd.DataFrame())
        if not production_stage.empty:
            st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">⚙️ Process View</h3>', unsafe_allow_html=True)
            st.bar_chart(production_stage.set_index('Process')[['Volume']])

        metrics = prod_data.get('metrics', pd.DataFrame())
        if not metrics.empty:
            st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🏢 Production Location Revenue</h3>', unsafe_allow_html=True)
            st.dataframe(metrics.head(15), width='stretch')
    else:
        st.warning("No production data available for the selected date range")

elif tab_selection == "Warehouse Prediction":
    # ===== WAREHOUSE PREDICTION TAB =====
    st.markdown('<h2 class="subheader-modern">🔮 ML-based Warehouse Location Prediction</h2>', unsafe_allow_html=True)
    
    with st.spinner("🤖 Running ML model..."):
        warehouse_pred = cached_warehouse_prediction()
    
    if not warehouse_pred.empty:
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600;">🎯 Recommended Warehouse Locations</h3>', unsafe_allow_html=True)
        st.write("**Scoring breakdown:**")
        st.write("- Orders (30%): shipment volume")
        st.write("- Delivery rate (30%): successful delivery percentage")
        st.write("- ML prediction score (40%): advanced ML model output")
        
        for idx, row in warehouse_pred.iterrows():
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("🏙️ City", row['City'])
            col2.metric("📦 Orders", int(row['Orders']))
            col3.metric("💰 Revenue", f"₹{row['TotalRevenue']/100000:.1f}L")
            col4.metric("✓ Rate", f"{row['DeliveryRate']:.1f}%")
            col5.metric("⭐ Score", f"{row['FinalScore']:.1f}")
            
            recommendation = row['Recommendation']
            if recommendation == 'High Priority':
                st.success(f"✅ {recommendation} - prioritize immediate warehouse setup")
            elif recommendation == 'Medium Priority':
                st.info(f"⚠️ {recommendation} - consider warehouse expansion")
            else:
                st.warning(f"❌ {recommendation} - monitor before investing")
            st.divider()
        
        st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📊 All Predictions</h3>', unsafe_allow_html=True)
        st.dataframe(warehouse_pred, width='stretch')
        
        csv = warehouse_pred.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Warehouse Predictions",
            data=csv,
            file_name="warehouse_predictions_ml.csv",
            mime="text/csv",
            key="download_warehouse_pred"
        )
    else:
        st.warning("Unable to generate warehouse predictions")

elif tab_selection == "Supply Chain":
    # ===== SUPPLY CHAIN TAB =====
    supply_chain = cached_supply_chain_metrics(start_date, end_date)
    
    st.markdown('<h2 class="subheader-modern">⛓️ Supply Chain and Logistics Analytics</h2>', unsafe_allow_html=True)
    
    st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600;">🚚 Courier Partner Performance</h3>', unsafe_allow_html=True)
    courier_metrics = supply_chain.get('courier_metrics', pd.DataFrame())
    
    if not courier_metrics.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("🏢 Total Couriers", supply_chain.get('total_couriers', 0))
        best = supply_chain.get('best_courier')
        if best is not None:
            col2.metric("⭐ Best Performer", best.get('CourierPartner', 'N/A'))
            col3.metric("Delivery Rate", f"{best.get('DeliveryRate', 0):.1f}%")
        
        st.dataframe(courier_metrics, width='stretch')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h3 style="color: #A23B72; font-size: 1rem; font-weight: 600;">📦 Orders by Courier</h3>', unsafe_allow_html=True)
            st.bar_chart(courier_metrics.set_index('CourierPartner')[['Orders']])
        with col2:
            st.markdown('<h3 style="color: #06A77D; font-size: 1rem; font-weight: 600;">✓ Delivery Rate by Courier</h3>', unsafe_allow_html=True)
            st.bar_chart(courier_metrics.set_index('CourierPartner')[['DeliveryRate']])
    
    st.markdown('<h3 style="color: #F18F01; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🗺️ Route Efficiency</h3>', unsafe_allow_html=True)
    route_data = supply_chain.get('route_data', pd.DataFrame())
    
    if not route_data.empty:
        st.dataframe(route_data, width='stretch')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h3 style="color: #2E86AB; font-size: 1rem; font-weight: 600;">📦 Route Volume</h3>', unsafe_allow_html=True)
            route_display = route_data.copy()
            route_display['Route'] = route_display['PickupCity'] + ' → ' + route_display['DropCity']
            st.bar_chart(route_display.set_index('Route')[['Orders']])
        
        with col2:
            st.markdown('<h3 style="color: #A23B72; font-size: 1rem; font-weight: 600;">💰 Route Revenue</h3>', unsafe_allow_html=True)
            st.bar_chart(route_display.set_index('Route')[['Revenue']])

        map_rows = []
        hub_coords = get_city_coords('Faridabad')
        if hub_coords is not None:
            for _, row in route_data.iterrows():
                target_coords = get_city_coords(row['DropCity'])
                if target_coords is None:
                    continue
                map_rows.append({
                    'source_lon': hub_coords[1],
                    'source_lat': hub_coords[0],
                    'target_lon': target_coords[1],
                    'target_lat': target_coords[0],
                    'Orders': row['Orders'],
                    'DropCity': row['DropCity']
                })

        if map_rows:
            if PYDECK_AVAILABLE:
                st.markdown('<h3 style="color: #F18F01; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🗺️ Airport-style Hub Routes</h3>', unsafe_allow_html=True)
                arc_df = pd.DataFrame(map_rows)
                deck = pdk.Deck(
                    initial_view_state=pdk.ViewState(
                        latitude=hub_coords[0],
                        longitude=hub_coords[1],
                        zoom=4.5,
                        pitch=30
                    ),
                    layers=[
                        pdk.Layer(
                            'ArcLayer',
                            data=arc_df,
                            get_source_position=['source_lon', 'source_lat'],
                            get_target_position=['target_lon', 'target_lat'],
                            get_width='Orders',
                            get_source_color=[255, 100, 100],
                            get_target_color=[30, 144, 255],
                            pickable=True,
                            auto_highlight=True
                        ),
                        pdk.Layer(
                            'ScatterplotLayer',
                            data=arc_df,
                            get_position=['target_lon', 'target_lat'],
                            get_fill_color=[0, 128, 255, 180],
                            get_radius=25000,
                            pickable=True
                        )
                    ]
                )
                st.pydeck_chart(deck)
            else:
                st.info('pydeck is not installed. Install pydeck to render airport-style route maps.')
        else:
            st.info('Not enough location coordinates available to build the route map.')
    else:
        st.info("No route data available")