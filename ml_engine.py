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

        for df in [so, kit, disp]:
            df.columns = [c.strip() for c in df.columns]

        # Normalize keys for matching
        so['No'] = so.get('No', so.get('OrderNo', pd.Series(dtype=str))).astype(str).str.strip()
        disp['OrderNo'] = disp['OrderNo'].astype(str).str.strip()
        so['ItemNo'] = so['ItemNo'].astype(str).str.strip()
        kit['ItemNo'] = kit['ItemNo'].astype(str).str.strip()
        disp['SKU'] = disp['SKU'].astype(str).str.strip()

        so.rename(columns={'ItemNo': 'SKU_Code', 'Quantity': 'OrderedQty'}, inplace=True)
        kit.rename(columns={'ItemNo': 'SKU_Code', 'KitQty': 'Stock in Hand'}, inplace=True)
        disp.rename(columns={'SKU': 'SKU_Code', 'Quantity': 'Dispatched'}, inplace=True)

        so_grouped = so.groupby(['No', 'SKU_Code'])['OrderedQty'].sum().reset_index()
        kit_grouped = kit.groupby('SKU_Code')['Stock in Hand'].sum().reset_index()
        disp_grouped = disp.groupby(['OrderNo', 'SKU_Code'])['Dispatched'].sum().reset_index()

        merged = so_grouped.merge(
            disp_grouped,
            left_on=['No', 'SKU_Code'],
            right_on=['OrderNo', 'SKU_Code'],
            how='left'
        ).merge(
            kit_grouped,
            on='SKU_Code',
            how='left'
        ).fillna(0)

        merged['Status'] = merged.apply(
            lambda row: 'Dispatched' if row['Dispatched'] >= row['OrderedQty'] else 'Pending',
            axis=1
        )
        merged['DispatchPercent'] = ((merged['Dispatched'] / merged['OrderedQty']) * 100).fillna(0).clip(0, 100).round(1)
        merged['Gap'] = merged['OrderedQty'] - (merged['Stock in Hand'] + merged['Dispatched'])

        final = merged[[
            'No', 'SKU_Code', 'Stock in Hand', 'OrderedQty', 'Dispatched', 'DispatchPercent', 'Status', 'Gap'
        ]].rename(columns={
            'No': 'OrderNo',
            'OrderedQty': 'Required'
        })

        conn.close()
        return final
    except Exception as e:
        print(f"Error in ML Engine: {e}")
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
        
        dispatch['IsB2B'] = dispatch['IsB2B'].astype(str).str.strip().str.upper()
        dispatch['CustomerName'] = dispatch.get('CustomerName', dispatch.get('Customer', pd.Series(dtype=str))).astype(str).str.strip()
        dispatch['OrderDate'] = pd.to_datetime(dispatch['OrderDate'], errors='coerce', dayfirst=True)
        dispatch['AWBNo'] = dispatch.get('AWBNo', '').astype(str).str.strip()
        dispatch['Quantity'] = pd.to_numeric(dispatch.get('Quantity', 0), errors='coerce').fillna(0)
        dispatch['InvoiceValue'] = pd.to_numeric(dispatch.get('InvoiceValue', 0), errors='coerce').fillna(0)
        dispatch['PaymentMode'] = dispatch.get('PaymentMode', dispatch.get('ModeOfPayment', '')).astype(str).str.strip().replace({'': 'Unknown'})

        b2b_data = dispatch[dispatch['IsB2B'].isin(['1', 'TRUE', 'YES'])]
        if start_date and end_date:
            b2b_data = b2b_data[(b2b_data['OrderDate'] >= pd.to_datetime(start_date)) & 
                                (b2b_data['OrderDate'] <= pd.to_datetime(end_date))]

        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        cp['AWB'] = cp['AWB'].astype(str).str.strip()
        if start_date and end_date:
            cp['Created at'] = pd.to_datetime(cp['Created at'], errors='coerce')
            cp = cp[(cp['Created at'] >= pd.to_datetime(start_date)) & (cp['Created at'] <= pd.to_datetime(end_date))]

        def map_channel(customer_name, is_b2b_flag):
            customer_name = str(customer_name).strip().lower()
            if 'amazon' in customer_name:
                return 'Amazon'
            if 'flipkart' in customer_name:
                return 'Flipkart'
            if 'offline' in customer_name:
                return 'Offline'
            if is_b2b_flag:
                return 'B2B'
            return 'Other'

        b2b_data['Channel'] = b2b_data.apply(
            lambda row: map_channel(row['CustomerName'], True),
            axis=1
        )

        b2b_orders = len(b2b_data)
        b2b_revenue = b2b_data['InvoiceValue'].sum()
        b2b_qty = b2b_data['Quantity'].sum()

        related_awbs = set(b2b_data['AWBNo'].dropna().astype(str))
        b2b_delivery = cp[cp['AWB'].isin(related_awbs)]
        delivered = b2b_delivery[b2b_delivery['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)].shape[0]
        rto = b2b_delivery[b2b_delivery['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)].shape[0]
        delivered_qty = pd.to_numeric(b2b_delivery.loc[b2b_delivery['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False), 'Items Quantity'], errors='coerce').fillna(0).sum()
        partial_delivery_pct = (delivered_qty / b2b_qty * 100) if b2b_qty > 0 else 0
        b2b_delivery_rate = (delivered / len(b2b_delivery) * 100) if len(b2b_delivery) > 0 else 0

        top_clients = b2b_data.groupby('Client').agg({
            'OrderNo': 'count',
            'InvoiceValue': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        top_clients.columns = ['Client', 'Orders', 'Revenue', 'Quantity']
        top_clients = top_clients.sort_values('Revenue', ascending=False).head(10)

        channel_summary = b2b_data['Channel'].value_counts().reset_index()
        channel_summary.columns = ['Channel', 'Orders']

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
                'partial_delivery_pct': round(partial_delivery_pct, 1),
                'avg_order_value': round(b2b_revenue / b2b_orders, 2) if b2b_orders > 0 else 0
            },
            'top_clients': top_clients,
            'payment_modes': payment_modes,
            'channel_summary': channel_summary
        }
    except Exception as e:
        print(f"Error in B2B Analytics: {e}")
        if conn: conn.close()
        return {'summary': {}, 'top_clients': pd.DataFrame(), 'payment_modes': pd.DataFrame(), 'channel_summary': pd.DataFrame()}

def get_d2c_analytics(start_date=None, end_date=None):
    """D2C specific metrics and performance"""
    conn = sqlite3.connect(DB_PATH)
    try:
        dispatch = pd.read_sql("SELECT * FROM dispatch_table", conn)
        dispatch.columns = [c.strip() for c in dispatch.columns]
        
        dispatch['IsB2B'] = dispatch['IsB2B'].astype(str).str.strip().str.upper()
        dispatch['OrderDate'] = pd.to_datetime(dispatch['OrderDate'], errors='coerce', dayfirst=True)
        dispatch['AWBNo'] = dispatch.get('AWBNo', '').astype(str).str.strip()
        dispatch['Quantity'] = pd.to_numeric(dispatch.get('Quantity', 0), errors='coerce').fillna(0)
        dispatch['InvoiceValue'] = pd.to_numeric(dispatch.get('InvoiceValue', 0), errors='coerce').fillna(0)
        dispatch['PaymentMode'] = dispatch.get('PaymentMode', dispatch.get('ModeOfPayment', '')).astype(str).str.strip().replace({'': 'Unknown'})

        d2c_data = dispatch[~dispatch['IsB2B'].isin(['1', 'TRUE', 'YES'])]
        if start_date and end_date:
            d2c_data = d2c_data[(d2c_data['OrderDate'] >= pd.to_datetime(start_date)) & 
                                (d2c_data['OrderDate'] <= pd.to_datetime(end_date))]

        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        cp['AWB'] = cp['AWB'].astype(str).str.strip()
        if start_date and end_date:
            cp['Created at'] = pd.to_datetime(cp['Created at'], errors='coerce')
            cp = cp[(cp['Created at'] >= pd.to_datetime(start_date)) & (cp['Created at'] <= pd.to_datetime(end_date))]

        d2c_orders = len(d2c_data)
        d2c_revenue = d2c_data['InvoiceValue'].sum()
        d2c_qty = d2c_data['Quantity'].sum()

        related_awbs = set(d2c_data['AWBNo'].dropna().astype(str))
        d2c_delivery = cp[cp['AWB'].isin(related_awbs)]
        delivered = d2c_delivery[d2c_delivery['Clickpost Unified Status'].str.contains('Delivered', case=False, na=False)].shape[0]
        rto = d2c_delivery[d2c_delivery['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False)].shape[0]
        in_transit = max(0, len(d2c_delivery) - delivered - rto)
        d2c_delivery_rate = (delivered / len(d2c_delivery) * 100) if len(d2c_delivery) > 0 else 0

        top_cities = d2c_data.groupby('ShiptoCity').agg({
            'OrderNo': 'count',
            'InvoiceValue': 'sum'
        }).reset_index()
        top_cities.columns = ['City', 'Orders', 'Revenue']
        top_cities = top_cities.sort_values('Revenue', ascending=False).head(10)

        payment_split = d2c_data['PaymentMode'].value_counts().reset_index()
        payment_split.columns = ['Mode', 'Count']

        city_rto = d2c_delivery.groupby('Drop City').apply(
            lambda g: (g['Clickpost Unified Status'].str.contains('RTO|Return', case=False, na=False).sum() / len(g) * 100) if len(g) > 0 else 0
        ).reset_index(name='RTO %').sort_values('RTO %', ascending=False).head(10)

        conn.close()
        return {
            'summary': {
                'total_orders': d2c_orders,
                'total_revenue': d2c_revenue,
                'total_qty': d2c_qty,
                'delivered': delivered,
                'rto': rto,
                'in_transit': in_transit,
                'delivery_rate': round(d2c_delivery_rate, 1)
            },
            'top_cities': top_cities,
            'payment_split': payment_split,
            'city_rto': city_rto
        }
    except Exception as e:
        print(f"Error in D2C Analytics: {e}")
        if conn: conn.close()
        return {'summary': {}, 'top_cities': pd.DataFrame(), 'payment_split': pd.DataFrame(), 'city_rto': pd.DataFrame()}

def get_production_metrics(start_date=None, end_date=None):
    """Production location metrics and KPIs"""
    conn = sqlite3.connect(DB_PATH)
    try:
        dispatch = pd.read_sql("SELECT * FROM dispatch_table", conn)
        dispatch.columns = [c.strip() for c in dispatch.columns]
        so = pd.read_sql("SELECT * FROM so_master", conn)
        so.columns = [c.strip() for c in so.columns]
        kitting = pd.read_sql("SELECT * FROM kitting_table", conn)
        kitting.columns = [c.strip() for c in kitting.columns]

        if start_date and end_date:
            dispatch['OrderDate'] = pd.to_datetime(dispatch['OrderDate'], errors='coerce', dayfirst=True)
            dispatch = dispatch[(dispatch['OrderDate'] >= pd.to_datetime(start_date)) & 
                                  (dispatch['OrderDate'] <= pd.to_datetime(end_date))]
            so['OrderDate'] = pd.to_datetime(so['OrderDate'], errors='coerce', dayfirst=True)
            so = so[(so['OrderDate'] >= pd.to_datetime(start_date)) & 
                    (so['OrderDate'] <= pd.to_datetime(end_date))]
            kitting['CreatedOn'] = pd.to_datetime(kitting['CreatedOn'], errors='coerce')

        dispatch['Quantity'] = pd.to_numeric(dispatch.get('Quantity', 0), errors='coerce').fillna(0)
        dispatch['InvoiceValue'] = pd.to_numeric(dispatch.get('InvoiceValue', 0), errors='coerce').fillna(0)
        kitting['KitQty'] = pd.to_numeric(kitting.get('KitQty', 0), errors='coerce').fillna(0)
        so['Quantity'] = pd.to_numeric(so.get('Quantity', 0), errors='coerce').fillna(0)
        so['ToBePacked'] = pd.to_numeric(so.get('ToBePacked', 0), errors='coerce').fillna(0)
        so['ToBeDispatched'] = pd.to_numeric(so.get('ToBeDispatched', 0), errors='coerce').fillna(0)
        so['ToBeAllocated'] = pd.to_numeric(so.get('ToBeAllocated', 0), errors='coerce').fillna(0)
        so['ToBePicked'] = pd.to_numeric(so.get('ToBePicked', 0), errors='coerce').fillna(0)
        so['Delivered'] = pd.to_numeric(so.get('Delivered', 0), errors='coerce').fillna(0)
        so['RTO'] = pd.to_numeric(so.get('RTO', 0), errors='coerce').fillna(0)

        so['ItemNo'] = so['ItemNo'].astype(str).str.strip()
        kitting['ItemNo'] = kitting['ItemNo'].astype(str).str.strip()

        pending_sku = so.groupby('ItemNo').agg({
            'Quantity': 'sum',
            'ToBePicked': 'sum',
            'ToBeAllocated': 'sum',
            'ToBePacked': 'sum',
            'ToBeDispatched': 'sum',
            'Delivered': 'sum',
            'RTO': 'sum'
        }).reset_index().rename(columns={
            'Quantity': 'OrderedQty'
        })

        current_stock = kitting.groupby('ItemNo')['KitQty'].sum().reset_index().rename(columns={'KitQty': 'Stock in Hand'})
        pending_sku = pending_sku.merge(current_stock, on='ItemNo', how='left').fillna(0)
        pending_sku['PendingSO'] = (pending_sku['OrderedQty'] - pending_sku['Delivered'] - pending_sku['RTO']).clip(lower=0)
        pending_sku['MakeQty'] = (pending_sku['PendingSO'] - pending_sku['Stock in Hand']).clip(lower=0)
        pending_sku['ProcessPending'] = pending_sku['ToBePicked'] + pending_sku['ToBeAllocated'] + pending_sku['ToBePacked'] + pending_sku['ToBeDispatched']

        production_stage = pd.DataFrame({
            'Process': ['Kitting', 'Packing', 'Ready to Dispatch'],
            'Volume': [
                pending_sku['ToBeAllocated'].sum() + pending_sku['ToBePicked'].sum(),
                pending_sku['ToBePacked'].sum(),
                pending_sku['ToBeDispatched'].sum()
            ]
        })

        cp = pd.read_sql("SELECT * FROM clickpost_table", conn)
        cp.columns = [c.strip() for c in cp.columns]
        cp['AWB'] = cp['AWB'].astype(str).str.strip()
        if start_date and end_date:
            cp['Created at'] = pd.to_datetime(cp['Created at'], errors='coerce')
            cp = cp[(cp['Created at'] >= pd.to_datetime(start_date)) & (cp['Created at'] <= pd.to_datetime(end_date))]

        kitted_qty = kitting['KitQty'].sum()
        dispatched_qty = dispatch['Quantity'].sum()
        conversion_rate = (dispatched_qty / kitted_qty * 100) if kitted_qty > 0 else 0

        total_prod_revenue = dispatch['InvoiceValue'].sum()
        total_prod_orders = dispatch['OrderNo'].nunique()

        prod_metrics = dispatch.groupby('Client').agg({
            'OrderNo': 'count',
            'Quantity': 'sum',
            'InvoiceValue': 'sum'
        }).reset_index()
        prod_metrics.columns = ['ProductionLocation', 'Orders', 'Quantity', 'Revenue']
        prod_metrics = prod_metrics.sort_values('Revenue', ascending=False)

        conn.close()
        return {
            'metrics': prod_metrics,
            'pending_sku': pending_sku.sort_values('MakeQty', ascending=False).head(20),
            'production_stage': production_stage,
            'summary': {
                'total_revenue': total_prod_revenue,
                'total_orders': total_prod_orders,
                'kitting_to_dispatch_conversion': round(conversion_rate, 1),
                'pending_so': int(pending_sku['PendingSO'].sum()),
                'make_quantity': int(pending_sku['MakeQty'].sum())
            }
        }
    except Exception as e:
        print(f"Error in Production Metrics: {e}")
        if conn: conn.close()
        return {'metrics': pd.DataFrame(), 'pending_sku': pd.DataFrame(), 'production_stage': pd.DataFrame(), 'summary': {}}

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