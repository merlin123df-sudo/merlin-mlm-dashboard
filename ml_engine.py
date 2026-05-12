import pandas as pd
import sqlite3
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'processed_db/warehouse.db'

def get_inventory_gap():
    conn = sqlite3.connect(DB_PATH)
    try:
        so = pd.read_sql("SELECT * FROM so_master", conn)
        kit = pd.read_sql("SELECT * FROM kitting_table", conn)
        disp = pd.read_sql("SELECT * FROM dispatch_table", conn)

        # Columns ko clean karna (Spaces hatana aur Capital check karna)
        for df in [so, kit, disp]:
            df.columns = [c.strip() for c in df.columns]

        # Rename SKU columns to common name
        so.rename(columns={'ItemNo': 'SKU_Code'}, inplace=True)
        kit.rename(columns={'ItemNo': 'SKU_Code', 'KitQty': 'Quantity'}, inplace=True)
        disp.rename(columns={'SKU': 'SKU_Code'}, inplace=True)

        # Grouping
        so_grouped = so.groupby('SKU_Code')['Quantity'].sum().reset_index()
        kit_grouped = kit.groupby('SKU_Code')['Quantity'].sum().reset_index()
        disp_grouped = disp.groupby('SKU_Code')['Quantity'].sum().reset_index()

        # Merge
        final = so_grouped.merge(kit_grouped, on='SKU_Code', how='left').fillna(0)
        final = final.merge(disp_grouped, on='SKU_Code', how='left', suffixes=('_so', '_disp')).fillna(0)
        
        # Calculation: SO - (Kitting + Dispatch)
        # Yahan hum index use kar rahe hain taaki agar naam alag ho toh bhi chale
        final['Gap'] = final.iloc[:, 1] - (final.iloc[:, 2] + final.iloc[:, 3])
        
        conn.close()
        return final
    except Exception as e:
        print(f"Error in ML Engine: {e}") # Terminal mein error dikhayega
        if conn: conn.close()
        return pd.DataFrame()

def get_logistics_summary(start_date=None, end_date=None):
    conn = sqlite3.connect(DB_PATH)
    try:
        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        
        # Filter by date if provided
        if start_date and end_date:
            cp['Created at'] = pd.to_datetime(cp['Created at'], errors='coerce')
            cp = cp[(cp['Created at'] >= pd.to_datetime(start_date)) & (cp['Created at'] <= pd.to_datetime(end_date))]
        
        # Normalize numeric fields
        cp['Invoice Value'] = pd.to_numeric(cp.get('Invoice Value', 0), errors='coerce').fillna(0)
        cp['AWB'] = cp['AWB'].astype(str).str.strip()
        
        # Rest of the code...
        
        # Summary stats
        total_dispatched = len(cp)
        total_delivered = cp[cp['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)].shape[0]
        total_rto = cp[cp['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)].shape[0]
        total_revenue = cp['Invoice Value'].sum()
        
        # Shipment distribution by courier and payment mode
        shipment_dist = cp.groupby(['Courier Partner', 'Payment Mode']).size().reset_index(name='Count')
        
        # Top cities by volume
        top_cities = cp['Drop City'].value_counts().head(10).reset_index()
        top_cities.columns = ['City', 'Volume']
        
        # Top RTO locations
        rto_data = cp[cp['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)]
        rto_locations = rto_data['Drop City'].value_counts().head(10).reset_index()
        rto_locations.columns = ['City', 'RTO Count']
        
        # 3PL Performance
        performance = cp.groupby('Courier Partner')['Clickpost Unified Status'].value_counts(normalize=True).unstack().fillna(0) * 100
        performance = performance.round(1)

        # Client location mapping using dispatch data
        dispatch = pd.read_sql("SELECT * FROM dispatch_table", conn)
        dispatch.columns = [c.strip() for c in dispatch.columns]
        if 'OrderDate' in dispatch.columns and start_date and end_date:
            dispatch['OrderDate'] = pd.to_datetime(dispatch['OrderDate'], errors='coerce', dayfirst=True)
            dispatch = dispatch[(dispatch['OrderDate'] >= pd.to_datetime(start_date)) & (dispatch['OrderDate'] <= pd.to_datetime(end_date))]
        dispatch['Client'] = dispatch['Client'].astype(str).str.strip()
        dispatch['ShiptoCity'] = dispatch['ShiptoCity'].astype(str).str.strip()
        dispatch['ShiptoCity'] = dispatch['ShiptoCity'].replace({'': 'Unknown', 'nan': 'Unknown'})
        dispatch['InvoiceValue'] = pd.to_numeric(dispatch.get('InvoiceValue', 0), errors='coerce').fillna(0)
        dispatch['Quantity'] = pd.to_numeric(dispatch.get('Quantity', 0), errors='coerce').fillna(0)
        client_locations = dispatch.groupby(['Client', 'ShiptoCity']).size().reset_index(name='Orders')
        client_location_counts = dispatch.groupby('Client')['ShiptoCity'].nunique().reset_index(name='LocationCount').sort_values('LocationCount', ascending=False)
        
        # D2C vs B2B segmentation
        dispatch['IsB2B'] = dispatch['IsB2B'].astype(str).str.strip().str.upper()
        dispatch['OrderType'] = dispatch['IsB2B'].apply(lambda x: 'B2B' if x in ['1', 'TRUE', 'YES'] else 'D2C')
        d2c_b2b_summary = dispatch.groupby('OrderType').agg({
            'OrderNo': 'count',
            'InvoiceValue': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        d2c_b2b_summary.columns = ['OrderType', 'Orders', 'Revenue', 'Quantity']
        
        # Production location mapping (Client as production location)
        production_locations = dispatch.groupby(['Client', 'OrderType']).agg({
            'OrderNo': 'count',
            'InvoiceValue': 'sum',
            'ShiptoCity': 'nunique'
        }).reset_index()
        production_locations.columns = ['ProductionLocation', 'OrderType', 'Orders', 'Revenue', 'Cities']
        production_locations = production_locations.sort_values('Orders', ascending=False)
        
        # Delivered location analytics
        delivered_data = cp[cp['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)]
        delivered_cities = delivered_data['Drop City'].value_counts().head(15).reset_index()
        delivered_cities.columns = ['City', 'Delivered_Count']
        
        delivered_states = delivered_data['Drop State'].value_counts().head(10).reset_index()
        delivered_states.columns = ['State', 'Delivered_Count']
        
        # Route mapping - from pickup to drop (origin-destination routes)
        route_map = delivered_data.groupby(['Pickup City', 'Drop City']).size().reset_index(name='Orders')
        route_map = route_map.sort_values('Orders', ascending=False).head(20)
        
        # Warehouse recommendation logic
        delivery_performance = delivered_data.groupby('Drop City').agg({
            'AWB': 'count',
            'Invoice Value': 'sum'
        }).reset_index()
        delivery_performance.columns = ['City', 'Deliveries', 'Revenue']
        
        # Get RTO data for same cities
        rto_by_city = rto_data.groupby('Drop City').size().reset_index(name='RTO_Count')
        warehouse_score = delivery_performance.merge(rto_by_city, left_on='City', right_on='Drop City', how='left').fillna(0)
        warehouse_score = warehouse_score[['City', 'Deliveries', 'Revenue', 'RTO_Count']]
        warehouse_score['DeliveryRate'] = (warehouse_score['Deliveries'] / (warehouse_score['Deliveries'] + warehouse_score['RTO_Count']) * 100).round(1)
        warehouse_score['Score'] = (warehouse_score['Deliveries'] * warehouse_score['DeliveryRate'] / 100).round(0)
        warehouse_recommendations = warehouse_score.sort_values('Score', ascending=False).head(10)
        
        conn.close()
        return {
            'summary': {'total_dispatched': total_dispatched, 'total_delivered': total_delivered, 'total_rto': total_rto, 'total_revenue': total_revenue},
            'shipment_dist': shipment_dist,
            'top_cities': top_cities,
            'rto_locations': rto_locations,
            'performance': performance,
            'client_locations': client_locations,
            'client_location_counts': client_location_counts,
            'd2c_b2b_summary': d2c_b2b_summary,
            'production_locations': production_locations,
            'delivered_cities': delivered_cities,
            'delivered_states': delivered_states,
            'route_map': route_map,
            'warehouse_recommendations': warehouse_recommendations
        }
    except Exception as e:
        print(f"Error in Logistics: {e}")
        if conn: conn.close()
        return {}

def get_b2b_analytics(start_date=None, end_date=None):
    """B2B specific metrics and performance"""
    conn = sqlite3.connect(DB_PATH)
    try:
        dispatch = pd.read_sql("SELECT * FROM dispatch_table", conn)
        dispatch.columns = [c.strip() for c in dispatch.columns]
        
        # Filter B2B
        dispatch['IsB2B'] = dispatch['IsB2B'].astype(str).str.strip().str.upper()
        b2b_data = dispatch[dispatch['IsB2B'].isin(['1', 'TRUE', 'YES'])]
        
        if start_date and end_date:
            b2b_data['OrderDate'] = pd.to_datetime(b2b_data['OrderDate'], errors='coerce', dayfirst=True)
            b2b_data = b2b_data[(b2b_data['OrderDate'] >= pd.to_datetime(start_date)) & 
                                (b2b_data['OrderDate'] <= pd.to_datetime(end_date))]
        
        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        if start_date and end_date:
            cp['Created at'] = pd.to_datetime(cp['Created at'], errors='coerce')
            cp = cp[(cp['Created at'] >= pd.to_datetime(start_date)) & (cp['Created at'] <= pd.to_datetime(end_date))]
        
        # Summary metrics
        b2b_orders = len(b2b_data)
        # Convert InvoiceValue to numeric
        b2b_data['InvoiceValue'] = pd.to_numeric(b2b_data['InvoiceValue'], errors='coerce').fillna(0)
        b2b_revenue = b2b_data['InvoiceValue'].sum()
        # Convert Quantity to numeric
        b2b_data['Quantity'] = pd.to_numeric(b2b_data['Quantity'], errors='coerce').fillna(0)
        b2b_qty = b2b_data['Quantity'].sum()
        
        # Delivery performance
        b2b_awbs = set(b2b_data['OrderNo'].astype(str))
        b2b_delivery = cp[cp['AWB'].astype(str).isin(b2b_awbs)]
        delivered = b2b_delivery[b2b_delivery['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)].shape[0]
        rto = b2b_delivery[b2b_delivery['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)].shape[0]
        b2b_delivery_rate = (delivered / len(b2b_delivery) * 100) if len(b2b_delivery) > 0 else 0
        
        # Top B2B clients
        top_clients = b2b_data.groupby('Client').agg({
            'OrderNo': 'count',
            'InvoiceValue': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        top_clients.columns = ['Client', 'Orders', 'Revenue', 'Quantity']
        top_clients = top_clients.sort_values('Revenue', ascending=False).head(10)
        
        # Payment modes in B2B
        payment_modes = b2b_data['PaymentMode'].value_counts().reset_index()
        payment_modes.columns = ['Mode', 'Count']
        
        conn.close()
        return {
            'summary': {
                'total_orders': b2b_orders,
                'total_revenue': b2b_revenue,
                'total_qty': b2b_qty,
                'delivered': delivered,
                'rto': rto,
                'delivery_rate': round(b2b_delivery_rate, 1),
                'avg_order_value': round(b2b_revenue / b2b_orders, 2) if b2b_orders > 0 else 0
            },
            'top_clients': top_clients,
            'payment_modes': payment_modes
        }
    except Exception as e:
        print(f"Error in B2B Analytics: {e}")
        if conn: conn.close()
        return {'summary': {}, 'top_clients': pd.DataFrame(), 'payment_modes': pd.DataFrame()}

def get_d2c_analytics(start_date=None, end_date=None):
    """D2C specific metrics and performance"""
    conn = sqlite3.connect(DB_PATH)
    try:
        dispatch = pd.read_sql("SELECT * FROM dispatch_table", conn)
        dispatch.columns = [c.strip() for c in dispatch.columns]
        
        # Filter D2C
        dispatch['IsB2B'] = dispatch['IsB2B'].astype(str).str.strip().str.upper()
        d2c_data = dispatch[~dispatch['IsB2B'].isin(['1', 'TRUE', 'YES'])]
        
        if start_date and end_date:
            d2c_data['OrderDate'] = pd.to_datetime(d2c_data['OrderDate'], errors='coerce', dayfirst=True)
            d2c_data = d2c_data[(d2c_data['OrderDate'] >= pd.to_datetime(start_date)) & 
                                (d2c_data['OrderDate'] <= pd.to_datetime(end_date))]
        
        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        if start_date and end_date:
            cp['Created at'] = pd.to_datetime(cp['Created at'], errors='coerce')
            cp = cp[(cp['Created at'] >= pd.to_datetime(start_date)) & (cp['Created at'] <= pd.to_datetime(end_date))]
        
        # Summary metrics
        d2c_orders = len(d2c_data)
        # Convert InvoiceValue to numeric
        d2c_data['InvoiceValue'] = pd.to_numeric(d2c_data['InvoiceValue'], errors='coerce').fillna(0)
        d2c_revenue = d2c_data['InvoiceValue'].sum()
        # Convert Quantity to numeric
        d2c_data['Quantity'] = pd.to_numeric(d2c_data['Quantity'], errors='coerce').fillna(0)
        d2c_qty = d2c_data['Quantity'].sum()
        
        # Delivery performance
        d2c_awbs = set(d2c_data['OrderNo'].astype(str))
        d2c_delivery = cp[cp['AWB'].astype(str).isin(d2c_awbs)]
        delivered = d2c_delivery[d2c_delivery['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)].shape[0]
        rto = d2c_delivery[d2c_delivery['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)].shape[0]
        d2c_delivery_rate = (delivered / len(d2c_delivery) * 100) if len(d2c_delivery) > 0 else 0
        
        # Top D2C cities
        top_cities = d2c_data.groupby('ShiptoCity').agg({
            'OrderNo': 'count',
            'InvoiceValue': 'sum'
        }).reset_index()
        top_cities.columns = ['City', 'Orders', 'Revenue']
        top_cities = top_cities.sort_values('Revenue', ascending=False).head(10)
        
        # Payment modes in D2C
        payment_modes = d2c_data['PaymentMode'].value_counts().reset_index()
        payment_modes.columns = ['Mode', 'Count']
        
        conn.close()
        return {
            'summary': {
                'total_orders': d2c_orders,
                'total_revenue': d2c_revenue,
                'total_qty': d2c_qty,
                'delivered': delivered,
                'rto': rto,
                'delivery_rate': round(d2c_delivery_rate, 1),
                'avg_order_value': round(d2c_revenue / d2c_orders, 2) if d2c_orders > 0 else 0
            },
            'top_cities': top_cities,
            'payment_modes': payment_modes
        }
    except Exception as e:
        print(f"Error in D2C Analytics: {e}")
        if conn: conn.close()
        return {'summary': {}, 'top_cities': pd.DataFrame(), 'payment_modes': pd.DataFrame()}

def get_production_metrics(start_date=None, end_date=None):
    """Production location metrics and KPIs"""
    conn = sqlite3.connect(DB_PATH)
    try:
        dispatch = pd.read_sql("SELECT * FROM dispatch_table", conn)
        dispatch.columns = [c.strip() for c in dispatch.columns]
        
        if start_date and end_date:
            dispatch['OrderDate'] = pd.to_datetime(dispatch['OrderDate'], errors='coerce', dayfirst=True)
            dispatch = dispatch[(dispatch['OrderDate'] >= pd.to_datetime(start_date)) & 
                                (dispatch['OrderDate'] <= pd.to_datetime(end_date))]
        
        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        
        # Production metrics per client (production location)
        dispatch['InvoiceValue'] = pd.to_numeric(dispatch.get('InvoiceValue', 0), errors='coerce').fillna(0)
        dispatch['Quantity'] = pd.to_numeric(dispatch.get('Quantity', 0), errors='coerce').fillna(0)
        prod_metrics = dispatch.groupby('Client').agg({
            'OrderNo': 'count',
            'Quantity': 'sum',
            'InvoiceValue': 'sum'
        }).reset_index()
        prod_metrics.columns = ['ProductionLocation', 'Orders', 'Quantity', 'Revenue']
        
        # Add delivery and RTO data
        def get_delivery_stats(awbs):
            delivery_data = cp[cp['AWB'].astype(str).isin([str(x) for x in awbs])]
            delivered = delivery_data[delivery_data['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)].shape[0]
            rto = delivery_data[delivery_data['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)].shape[0]
            total = len(delivery_data)
            return delivered, rto, total
        
        delivery_stats = []
        for idx, row in prod_metrics.iterrows():
            client = row['ProductionLocation']
            client_awbs = dispatch[dispatch['Client'] == client]['OrderNo'].tolist()
            delivered, rto, total = get_delivery_stats(client_awbs)
            delivery_stats.append({
                'delivered': delivered,
                'rto': rto,
                'total': total
            })
        
        stats_df = pd.DataFrame(delivery_stats)
        prod_metrics['Delivered'] = stats_df['delivered']
        prod_metrics['RTO'] = stats_df['rto']
        prod_metrics['DeliveryRate'] = ((stats_df['delivered'] / stats_df['total'] * 100).round(1)).fillna(0)
        
        # KPIs
        prod_metrics['AvgOrderValue'] = (prod_metrics['Revenue'] / prod_metrics['Orders']).round(2)
        prod_metrics['AvgQuantity'] = (prod_metrics['Quantity'] / prod_metrics['Orders']).round(2)
        prod_metrics = prod_metrics.sort_values('Revenue', ascending=False)
        
        # Overall production KPIs
        total_prod_revenue = prod_metrics['Revenue'].sum()
        total_prod_orders = prod_metrics['Orders'].sum()
        total_prod_delivered = prod_metrics['Delivered'].sum()
        overall_delivery_rate = (total_prod_delivered / (prod_metrics['Delivered'].sum() + prod_metrics['RTO'].sum()) * 100) if (prod_metrics['Delivered'].sum() + prod_metrics['RTO'].sum()) > 0 else 0
        
        conn.close()
        return {
            'metrics': prod_metrics,
            'summary': {
                'total_revenue': total_prod_revenue,
                'total_orders': total_prod_orders,
                'total_delivered': total_prod_delivered,
                'delivery_rate': round(overall_delivery_rate, 1),
                'avg_order_value': round(total_prod_revenue / total_prod_orders, 2) if total_prod_orders > 0 else 0
            }
        }
    except Exception as e:
        print(f"Error in Production Metrics: {e}")
        if conn: conn.close()
        return {'metrics': pd.DataFrame(), 'summary': {}}

def predict_warehouse_locations(top_n=5):
    """ML model to predict best warehouse locations"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        
        # Prepare data for ML model
        cp['Invoice Value'] = pd.to_numeric(cp.get('Invoice Value', 0), errors='coerce').fillna(0)
        cp['AWB'] = cp['AWB'].astype(str).str.strip()
        delivered_data = cp[cp['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)]
        
        # Feature engineering
        city_features = delivered_data.groupby('Drop City').agg({
            'AWB': 'count',  # Orders
            'Invoice Value': ['sum', 'mean'],  # Revenue metrics
            'Pickup City': 'nunique',  # Source diversity
            'Courier Partner': 'nunique'  # Logistics partner diversity
        }).reset_index()
        
        city_features.columns = ['City', 'Orders', 'TotalRevenue', 'AvgRevenue', 'SourceDiversity', 'LogisticsDiversity']
        
        # Get RTO data
        rto_data = cp[cp['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)]
        rto_by_city = rto_data.groupby('Drop City').size().reset_index(name='RTOCount')
        rto_by_city.columns = ['City', 'RTOCount']
        
        city_features = city_features.merge(rto_by_city, on='City', how='left').fillna(0)
        
        # Calculate delivery rate
        city_features['DeliveryRate'] = (city_features['Orders'] / (city_features['Orders'] + city_features['RTOCount']) * 100)
        city_features['DeliveryRate'] = city_features['DeliveryRate'].fillna(0)
        
        # Prepare features for ML
        X = city_features[['Orders', 'TotalRevenue', 'SourceDiversity', 'LogisticsDiversity', 'DeliveryRate']].values
        y = city_features['TotalRevenue'].values
        
        # Train ML model
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = RandomForestRegressor(n_estimators=10, random_state=42, max_depth=5)
        model.fit(X_scaled, y)
        
        # Prediction score
        city_features['PredictionScore'] = model.predict(X_scaled)
        
        # Warehouse location recommendation with ML score
        warehouse_pred = city_features.copy()
        warehouse_pred['FinalScore'] = (
            warehouse_pred['Orders'] * 0.3 +
            warehouse_pred['DeliveryRate'] * 0.3 +
            (warehouse_pred['PredictionScore'] / warehouse_pred['PredictionScore'].max() * 100) * 0.4
        )
        
        warehouse_pred = warehouse_pred.sort_values('FinalScore', ascending=False).head(top_n)
        warehouse_pred['Recommendation'] = warehouse_pred.apply(
            lambda x: 'High Priority' if x['FinalScore'] > 70 else ('Medium Priority' if x['FinalScore'] > 40 else 'Low Priority'),
            axis=1
        )
        
        conn.close()
        return warehouse_pred[['City', 'Orders', 'TotalRevenue', 'DeliveryRate', 'FinalScore', 'Recommendation']]
    except Exception as e:
        print(f"Error in Warehouse Prediction: {e}")
        if conn: conn.close()
        return pd.DataFrame()

def get_supply_chain_metrics(start_date=None, end_date=None):
    """Supply chain analytics - routes, courier partners, fulfillment"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        
        if start_date and end_date:
            cp['Created at'] = pd.to_datetime(cp['Created at'], errors='coerce')
            cp = cp[(cp['Created at'] >= pd.to_datetime(start_date)) & (cp['Created at'] <= pd.to_datetime(end_date))]
        cp['Invoice Value'] = pd.to_numeric(cp.get('Invoice Value', 0), errors='coerce').fillna(0)
        cp['AWB'] = cp['AWB'].astype(str).str.strip()
        cp['Courier Partner'] = cp['Courier Partner'].astype(str).str.strip()
        
        dispatch = pd.read_sql("SELECT * FROM dispatch_table", conn)
        dispatch.columns = [c.strip() for c in dispatch.columns]
        
        # Courier performance
        courier_metrics = cp.groupby('Courier Partner').agg({
            'AWB': 'count',
            'Invoice Value': 'sum'
        }).reset_index()
        courier_metrics['Revenue'] = pd.to_numeric(courier_metrics['Invoice Value'], errors='coerce').fillna(0)
        courier_metrics = courier_metrics.drop(columns=['Invoice Value'], errors='ignore')
        courier_metrics.columns = ['CourierPartner', 'Orders', 'Revenue']
        
        # Delivery metrics by courier
        delivered_by_courier = cp[cp['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)].groupby('Courier Partner').size().reset_index(name='Delivered')
        rto_by_courier = cp[cp['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)].groupby('Courier Partner').size().reset_index(name='RTO')
        
        courier_metrics = courier_metrics.merge(delivered_by_courier, left_on='CourierPartner', right_on='Courier Partner', how='left').fillna(0)
        courier_metrics = courier_metrics.merge(rto_by_courier, left_on='CourierPartner', right_on='Courier Partner', how='left').fillna(0)
        courier_metrics['DeliveryRate'] = (courier_metrics['Delivered'] / (courier_metrics['Delivered'] + courier_metrics['RTO']) * 100).round(1)
        courier_metrics = courier_metrics.drop(['Courier Partner_x', 'Courier Partner_y'], axis=1, errors='ignore')
        
        # Route efficiency
        route_data = cp.groupby(['Pickup City', 'Drop City']).agg({
            'AWB': 'count',
            'Invoice Value': 'sum'
        }).reset_index()
        route_data['Invoice Value'] = pd.to_numeric(route_data['Invoice Value'], errors='coerce').fillna(0)
        route_data.columns = ['PickupCity', 'DropCity', 'Orders', 'Revenue']
        route_data = route_data.sort_values('Orders', ascending=False).head(10)
        
        # Fulfillment time analysis (if timestamps available)
        fulfillment = cp.copy()
        fulfillment['Created at'] = pd.to_datetime(fulfillment['Created at'], errors='coerce')
        fulfillment_time = fulfillment.groupby('Courier Partner')['Created at'].count().reset_index(name='ProcessingTime')
        
        conn.close()
        return {
            'courier_metrics': courier_metrics,
            'route_data': route_data,
            'total_couriers': len(courier_metrics),
            'best_courier': courier_metrics.loc[courier_metrics['DeliveryRate'].idxmax()] if not courier_metrics.empty else None
        }
    except Exception as e:
        print(f"Error in Supply Chain Metrics: {e}")
        if conn: conn.close()
        return {'courier_metrics': pd.DataFrame(), 'route_data': pd.DataFrame(), 'total_couriers': 0}