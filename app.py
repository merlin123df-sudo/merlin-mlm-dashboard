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
import time

# Caching functions to load data smoothly
@st.cache_data(ttl=120)
def cached_inventory_gap():
    try:
        return get_inventory_gap()
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=120)
def cached_logistics_summary(start_date, end_date):
    try:
        return get_logistics_summary(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading logistics: {e}")
        return {}

@st.cache_data(ttl=120)
def cached_b2b_analytics(start_date, end_date):
    try:
        return get_b2b_analytics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading B2B data: {e}")
        return {'summary': {}, 'top_clients': pd.DataFrame(), 'payment_modes': pd.DataFrame()}

@st.cache_data(ttl=120)
def cached_d2c_analytics(start_date, end_date):
    try:
        return get_d2c_analytics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading D2C data: {e}")
        return {'summary': {}, 'top_cities': pd.DataFrame(), 'payment_modes': pd.DataFrame()}

@st.cache_data(ttl=120)
def cached_production_metrics(start_date, end_date):
    try:
        return get_production_metrics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading production metrics: {e}")
        return {'metrics': pd.DataFrame(), 'summary': {}}

@st.cache_data(ttl=120)
def cached_warehouse_prediction():
    try:
        return predict_warehouse_locations(top_n=5)
    except Exception as e:
        st.error(f"Error predicting warehouses: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=120)
def cached_supply_chain_metrics(start_date, end_date):
    try:
        return get_supply_chain_metrics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading supply chain metrics: {e}")
        return {'courier_metrics': pd.DataFrame(), 'route_data': pd.DataFrame(), 'total_couriers': 0}

# Modern Premium Page Configuration
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

    @media (max-width: 900px) {{
        .main-title {{ font-size: 2.2rem; }}
        .stMetric {{ padding: 1rem !important; }}
        .dashboard-card {{ padding: 1rem !important; }}
        .subheader-modern {{ font-size: 1.25rem; }}
    }}

    @media (max-width: 600px) {{
        .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; }}
        .stMarkdown {{ margin: 0 !important; }}
    }}
</style>

<script>
    // Mobile detection
    const isMobile = window.innerWidth <= 768;
    window.parent.postMessage({{'type': 'streamlit:setSessionState', 'key': 'mobile', 'value': isMobile}}, '*');
</script>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">📊 Merlin MLM Dashboard</h1>', unsafe_allow_html=True)

# Sidebar - Premium Styling
st.sidebar.markdown("<h2 style='color: #2E86AB; font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)

# Sync button
col_sync1, col_sync2 = st.sidebar.columns(2)
with col_sync1:
    if st.sidebar.button("🔄 Sync Data"):
        success, message = run_pipeline()
        if success:
            st.sidebar.success(message)
            st.cache_data.clear()  # Clear cache after syncing
        else:
            st.sidebar.error(message)

with col_sync2:
    if st.sidebar.button("🗑️ Clear Cache"):
        st.cache_data.clear()
        st.sidebar.success("Cache cleared!")

# Date Filters - Premium Styling
st.sidebar.markdown("<h3 style='color: #A23B72; font-size: 1.2rem; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem;'>📅 Date Filters</h3>", unsafe_allow_html=True)
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2026-05-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2026-05-09"))

# Navigation tabs
st.sidebar.markdown("<h3 style='color: #F18F01; font-size: 1.2rem; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem;'>📊 Navigation</h3>", unsafe_allow_html=True)

tab_selection = st.sidebar.radio(
    "Select Dashboard:",
    ["📈 Overview", "🏢 B2B Analytics", "👥 D2C Analytics", "🏭 Production", "🔮 Warehouse Prediction", "⛓️ Supply Chain"]
)

# Load all data with caching
gap_data = cached_inventory_gap()
log_data = cached_logistics_summary(start_date, end_date)

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
            st.markdown(f'<div class="alert-error">❌ Over-dispatched Items: {len(negative_gaps)} SKUs have negative gaps</div>', unsafe_allow_html=True)
    
    # Inventory Gap
    st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📦 Inventory Gap Analysis</h3>', unsafe_allow_html=True)
    if not gap_data.empty:
        st.dataframe(gap_data, width='stretch')
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
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Orders", summary.get('total_orders', 0))
        col2.metric("✓ Delivered", summary.get('delivered', 0))
        col3.metric("Delivery Rate", f"{summary.get('delivery_rate', 0):.1f}%")
        col4.metric("Avg Order Value", f"₹{summary.get('avg_order_value', 0):,.0f}")
        
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">💰 Financial Metrics</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Revenue", f"₹{summary.get('total_revenue', 0):,.0f}")
        col2.metric("Total Quantity", f"{summary.get('total_qty', 0):.0f} units")
        
        # Top B2B Clients
        st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🎯 Top B2B Clients</h3>', unsafe_allow_html=True)
        top_clients = b2b_data.get('top_clients', pd.DataFrame())
        if not top_clients.empty:
            st.dataframe(top_clients, width='stretch')
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(top_clients.set_index('Client')[['Orders']])
            with col2:
                st.bar_chart(top_clients.set_index('Client')[['Revenue']])
        
        # Payment Modes
        payment_modes = b2b_data.get('payment_modes', pd.DataFrame())
        if not payment_modes.empty:
            st.markdown('<h3 style="color: #F18F01; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">💳 Payment Modes</h3>', unsafe_allow_html=True)
            st.bar_chart(payment_modes.set_index('Mode'))
    else:
        st.warning("No B2B data available for selected date range")

elif tab_selection == "👥 D2C Analytics":
    # ===== D2C TAB =====
    d2c_data = cached_d2c_analytics(start_date, end_date)
    
    st.markdown('<h2 class="subheader-modern">👥 D2C Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    if d2c_data and d2c_data['summary']:
        summary = d2c_data['summary']
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Orders", summary.get('total_orders', 0))
        col2.metric("✓ Delivered", summary.get('delivered', 0))
        col3.metric("Delivery Rate", f"{summary.get('delivery_rate', 0):.1f}%")
        col4.metric("Avg Order Value", f"₹{summary.get('avg_order_value', 0):,.0f}")
        
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">💰 Financial Metrics</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Revenue", f"₹{summary.get('total_revenue', 0):,.0f}")
        col2.metric("Total Quantity", f"{summary.get('total_qty', 0):.0f} units")
        
        # Top D2C Cities
        st.markdown('<h3 style="color: #06A77D; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🏙️ Top D2C Cities</h3>', unsafe_allow_html=True)
        top_cities = d2c_data.get('top_cities', pd.DataFrame())
        if not top_cities.empty:
            st.dataframe(top_cities, width='stretch')
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(top_cities.set_index('City')[['Orders']])
            with col2:
                st.bar_chart(top_cities.set_index('City')[['Revenue']])
        
        # Payment Modes
        payment_modes = d2c_data.get('payment_modes', pd.DataFrame())
        if not payment_modes.empty:
            st.markdown('<h3 style="color: #F18F01; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">💳 Payment Modes</h3>', unsafe_allow_html=True)
            st.bar_chart(payment_modes.set_index('Mode'))
    else:
        st.warning("No D2C data available for selected date range")

elif tab_selection == "🏭 Production":
    # ===== PRODUCTION TAB =====
    prod_data = cached_production_metrics(start_date, end_date)
    
    st.markdown('<h2 class="subheader-modern">🏭 Production Location Metrics & KPIs</h2>', unsafe_allow_html=True)
    
    if prod_data and prod_data['summary']:
        summary = prod_data['summary']
        
        # Overall KPIs
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600;">📊 Production KPIs</h3>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Orders", summary.get('total_orders', 0))
        col2.metric("✓ Delivered", summary.get('total_delivered', 0))
        col3.metric("Delivery Rate", f"{summary.get('delivery_rate', 0):.1f}%")
        col4.metric("Avg Order Value", f"₹{summary.get('avg_order_value', 0):,.0f}")
        
        st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📈 Total Revenue</h3>', unsafe_allow_html=True)
        st.metric("", f"₹{summary.get('total_revenue', 0):,.0f}")
        
        # Production Location Details
        st.markdown('<h3 style="color: #F18F01; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">🏢 Production Locations Performance</h3>', unsafe_allow_html=True)
        metrics = prod_data.get('metrics', pd.DataFrame())
        if not metrics.empty:
            st.dataframe(metrics.head(15), width='stretch')
            
            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<h3 style="color: #2E86AB; font-size: 1rem; font-weight: 600;">📦 Orders by Production Location</h3>', unsafe_allow_html=True)
                st.bar_chart(metrics.set_index('ProductionLocation')[['Orders']])
            
            with col2:
                st.markdown('<h3 style="color: #A23B72; font-size: 1rem; font-weight: 600;">💰 Revenue by Production Location</h3>', unsafe_allow_html=True)
                st.bar_chart(metrics.set_index('ProductionLocation')[['Revenue']])
            
            # Delivery Rate Chart
            st.markdown('<h3 style="color: #06A77D; font-size: 1rem; font-weight: 600; margin-top: 2rem;">✓ Delivery Rate by Location</h3>', unsafe_allow_html=True)
            st.bar_chart(metrics.set_index('ProductionLocation')[['DeliveryRate']])
    else:
        st.warning("No production data available for selected date range")

elif tab_selection == "🔮 Warehouse Prediction":
    # ===== WAREHOUSE PREDICTION TAB =====
    st.markdown('<h2 class="subheader-modern">🔮 ML-Based Warehouse Location Prediction</h2>', unsafe_allow_html=True)
    
    with st.spinner("🤖 Running ML Model..."):
        warehouse_pred = cached_warehouse_prediction()
    
    if not warehouse_pred.empty:
        st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600;">🎯 Recommended Warehouse Locations</h3>', unsafe_allow_html=True)
        st.write("**Scoring Mechanism:**")
        st.write("- Orders (30%): Volume of shipments")
        st.write("- Delivery Rate (30%): Success delivery percentage")
        st.write("- ML Prediction Score (40%): Advanced ML model prediction")
        
        # Display recommendations
        for idx, row in warehouse_pred.iterrows():
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("🏙️ City", row['City'])
            col2.metric("📦 Orders", int(row['Orders']))
            col3.metric("💰 Revenue", f"₹{row['TotalRevenue']/100000:.1f}L")
            col4.metric("✓ Rate", f"{row['DeliveryRate']:.1f}%")
            col5.metric("⭐ Score", f"{row['FinalScore']:.1f}")
            
            # Recommendation badge
            recommendation = row['Recommendation']
            if recommendation == 'High Priority':
                st.success(f"✅ {recommendation} - Immediate warehouse setup recommended")
            elif recommendation == 'Medium Priority':
                st.info(f"⚠️ {recommendation} - Consider warehouse expansion")
            else:
                st.warning(f"❌ {recommendation} - Monitor before investment")
            st.divider()
        
        # Full table
        st.markdown('<h3 style="color: #A23B72; font-size: 1.1rem; font-weight: 600; margin-top: 2rem;">📊 All Predictions</h3>', unsafe_allow_html=True)
        st.dataframe(warehouse_pred, width='stretch')
        
        # Download
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

elif tab_selection == "⛓️ Supply Chain":
    # ===== SUPPLY CHAIN TAB =====
    supply_chain = cached_supply_chain_metrics(start_date, end_date)
    
    st.markdown('<h2 class="subheader-modern">⛓️ Supply Chain & Logistics Analytics</h2>', unsafe_allow_html=True)
    
    # Courier Performance
    st.markdown('<h3 style="color: #2E86AB; font-size: 1.1rem; font-weight: 600;">🚚 Courier Partner Performance</h3>', unsafe_allow_html=True)
    courier_metrics = supply_chain.get('courier_metrics', pd.DataFrame())
    
    if not courier_metrics.empty:
        # Top metrics
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
    
    # Route Analysis
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
    else:
        st.info("No route data available")