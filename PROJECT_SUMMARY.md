# Merlin MLM Dashboard - Project Summary
**Date**: May 10, 2026  
**Status**: ✅ Complete and Production Ready

---

## 📋 Project Overview

Merlin MLM is a **premium operations & logistics dashboard** built with Streamlit for real-time monitoring of MLM operations, inventory management, and supply chain analytics.

### Key Features

#### 1. **📈 Overview Dashboard**
- Real-time inventory gap analysis
- Total logistics metrics (Dispatched, Delivered, RTO, Revenue)
- Shipment distribution by courier and payment mode
- Top cities by volume analysis
- RTO (Return To Origin) location tracking
- Integrated alerts for KPI thresholds

#### 2. **🏢 B2B Analytics Section**
- B2B-specific KPIs (Orders, Delivery Rate, Avg Order Value)
- Top B2B clients ranking by revenue
- Client-wise payment mode breakdown
- Financial metrics and volume tracking
- Separate B2B performance charts

#### 3. **👥 D2C Analytics Section**
- D2C-specific metrics isolated from B2B
- Top D2C cities by orders and revenue
- Geographic performance analysis
- Payment mode distribution in D2C
- Customer segment performance tracking

#### 4. **🏭 Production Metrics Dashboard**
- Production location KPIs
- Revenue and order count per production facility
- Delivery rate by production location
- Average order value and quantity metrics
- Location-wise performance comparison

#### 5. **🔮 ML-Based Warehouse Prediction**
- Advanced RandomForest ML model
- Intelligent scoring system:
  - Order Volume: 30%
  - Delivery Rate: 30%
  - ML Prediction: 40%
- 5 best warehouse location recommendations
- Priority levels (High/Medium/Low)
- Exportable predictions for planning

#### 6. **⛓️ Supply Chain & Logistics Analytics**
- Courier partner performance metrics
- Delivery rate comparison across couriers
- Route efficiency analysis (Origin → Destination)
- Route volume and revenue tracking
- Best performer identification

---

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit 1.57.0 (Premium UI)
- **Backend**: Python 3.x
- **Database**: SQLite (`processed_db/warehouse.db`)
- **Data Processing**: Pandas, NumPy
- **ML Models**: Scikit-learn 1.8.0
- **Data Intake**: Raw CSV/XLSX files

### File Structure
```
python/
├── app.py                 # Main Streamlit dashboard (6 tabs)
├── ml_engine.py          # Analytics & ML functions
├── pipeline.py           # Data ingestion pipeline
├── test_ml.py           # Testing utilities
├── inspect_data.py      # Data inspection helpers
├── processed_db/        # SQLite database
│   └── warehouse.db
├── raw_data/            # Incoming CSV/XLSX files
├── archive/             # Historical data backups
└── .streamlit/          # Streamlit config
```

---

## 🚀 Core Functions

### ml_engine.py Functions

1. **get_inventory_gap()** - Inventory analysis
   - Compares SO (Sales Order) vs Kitting vs Dispatch
   - Identifies over-dispatch and under-supply

2. **get_logistics_summary(start_date, end_date)** - Overall logistics metrics
   - Dispatch, delivery, and RTO counts
   - Shipment distribution
   - Top cities and RTO locations
   - 3PL performance metrics

3. **get_b2b_analytics(start_date, end_date)** - B2B-specific analytics
   - Order metrics and delivery performance
   - Top client identification
   - Payment mode analysis

4. **get_d2c_analytics(start_date, end_date)** - D2C-specific analytics
   - Order volume and revenue by city
   - Payment mode distribution
   - Customer engagement metrics

5. **get_production_metrics(start_date, end_date)** - Production location KPIs
   - Orders, revenue, and quantity per facility
   - Delivery rate calculation
   - Average order values

6. **predict_warehouse_locations(top_n=5)** - ML warehouse prediction
   - Trains RandomForest model
   - Scores locations on multiple factors
   - Recommends best warehouse setup locations

7. **get_supply_chain_metrics(start_date, end_date)** - Supply chain analysis
   - Courier performance metrics
   - Route efficiency analysis
   - Best performer identification

### pipeline.py Functions

1. **run_pipeline()** - Smart data ingestion
   - Detects new files in `raw_data/`
   - Deduplicates using unique keys (OrderNo, AWB, KitNo)
   - Appends only new records to SQLite
   - Archives processed files
   - Returns success/error messages

---

## 💾 Data Flow

```
Raw CSV/XLSX Files
        ↓
    pipeline.py (run_pipeline)
        ↓
    SQLite Database (processed_db/warehouse.db)
        ↓
    ml_engine.py (Analytics functions)
        ↓
    app.py (Streamlit Dashboard)
        ↓
    Browser (Premium UI with Dark/Light Theme)
```

---

## 🎨 UI/UX Features

### Premium Styling
- ✨ Glassmorphism design with backdrop blur
- 🎨 Custom color scheme (#2E86AB, #A23B72, #F18F01)
- 🌓 Dark/Light theme toggle
- 📱 Mobile-responsive layout
- ⚡ Smooth animations and transitions

### Performance Features
- 🚀 Data caching with TTL (300 seconds)
- 🔄 Manual cache refresh button
- 🎯 Fast-loading tabs
- 📊 Efficient chart rendering

### User Experience
- 📅 Date range filters
- 🔄 One-click data sync
- 📥 CSV export functionality
- ⚠️ Smart alerts for thresholds
- 📊 6 independent dashboard tabs

---

## 📊 Database Schema

### Tables
1. **so_master** - Sales Orders
   - ItemNo, Quantity, OrderNo, OrderDate

2. **dispatch_table** - Dispatch Records
   - SKU, Quantity, OrderNo, Client, ShiptoCity, IsB2B, PaymentMode, InvoiceValue

3. **kitting_table** - Kitting/Assembly
   - ItemNo, KitQty, KitNo, CreatedOn

4. **clickpost_table** - Logistics Tracking
   - AWB, Courier Partner, Pickup City, Drop City, Drop State, Invoice Value, Clickpost Unified Status, Payment Mode, Created at

---

## ⚙️ Installation & Setup

### Prerequisites
```
Python 3.7+
streamlit==1.57.0
pandas
numpy
scikit-learn==1.8.0
sqlite3 (built-in)
```

### Installation
```bash
# Install dependencies
pip install streamlit pandas numpy scikit-learn

# Navigate to project
cd c:\Users\amjad\OneDrive\Documents\python

# Run dashboard
streamlit run app.py
```

### Dashboard URL
- Local: `http://localhost:8501`
- Access from browser after running `streamlit run app.py`

---

## 📈 Key Metrics Tracked

### Operational KPIs
- Total Orders Dispatched
- Successful Deliveries
- Return To Origin (RTO) Count
- Delivery Rate (%)
- Average Order Value

### Financial Metrics
- Total Revenue
- Revenue by Customer Segment (B2B/D2C)
- Revenue by Production Location
- Revenue by Route/Corridor

### Logistics Metrics
- Courier Partner Performance
- RTO Rate by Location
- Delivery Rate by Location
- Route Efficiency Scores
- Top Routes by Volume/Revenue

### Supply Chain Metrics
- Warehouse Recommendation Score
- Production Location Health
- Client Geographic Spread
- Delivery Rate by Channel

---

## 🔮 ML Model Details

### Warehouse Prediction Model
- **Algorithm**: Random Forest Regressor
- **Training Data**: Historical delivery data
- **Features Used**:
  - Order volume per city
  - Total revenue generated
  - Source diversity (pickup cities)
  - Logistics partner diversity
  - Historical delivery rate
  
- **Scoring Logic**:
  ```
  FinalScore = (Orders × 0.3) + 
               (DeliveryRate × 0.3) + 
               (MLPredictionScore × 0.4)
  ```

- **Output**: Priority recommendations (High/Medium/Low)

---

## 🔄 Data Ingestion Process

1. **File Detection**: Scans `raw_data/` for:
   - `*dispatch*.csv`
   - `*so*.csv`
   - `*kitting*.xlsx`
   - `*CLICKPOST*.csv`

2. **Deduplication**: Uses unique keys:
   - Dispatch: `OrderNo`
   - SO: `OrderNo`
   - Kitting: `KitNo`
   - ClickPost: `AWB`

3. **Incremental Load**: Only new records appended
4. **Archiving**: Files moved to `archive/` with timestamp
5. **Logging**: Success/failure messages displayed in UI

---

## 📋 Dashboard Tabs

### Tab 1: 📈 Overview
- Quick snapshot of all metrics
- Alerts and thresholds
- Inventory gap analysis
- Shipment distribution

### Tab 2: 🏢 B2B Analytics
- B2B-specific KPIs
- Top clients ranking
- Payment mode breakdown
- Revenue trends

### Tab 3: 👥 D2C Analytics
- D2C-specific KPIs
- Geographic distribution
- Top cities analysis
- Payment patterns

### Tab 4: 🏭 Production
- Production location KPIs
- Facility-wise metrics
- Delivery performance
- Revenue analysis

### Tab 5: 🔮 Warehouse Prediction
- ML model recommendations
- Location scoring
- Priority levels
- Downloadable predictions

### Tab 6: ⛓️ Supply Chain
- Courier performance
- Route efficiency
- Volume & revenue tracking
- Best performer identification

---

## 🛠️ Customization & Extensions

### Adding New Analytics
1. Create function in `ml_engine.py`
2. Add caching wrapper in `app.py`
3. Create tab section in tab-based structure

### Modifying Thresholds
Edit alert conditions in `app.py`:
- RTO threshold: Currently 3%
- Delivery rate threshold: Currently 80%

### Extending ML Model
- Update `predict_warehouse_locations()` in `ml_engine.py`
- Adjust feature weights in scoring logic
- Retrain on new data periodically

---

## 📚 Data Sources

### Input Files Expected
- **Dispatch Data**: Order-level shipment details
- **SO Master**: Sales order inventory
- **Kitting**: Production/assembly records
- **ClickPost**: Logistics tracking from courier API

### Data Frequency
- Real-time updates via dashboard sync
- Historical data retained in archive
- Incremental daily ingestion recommended

---

## ✅ Testing Checklist

- [x] All functions compile without errors
- [x] Data caching implemented
- [x] Tab navigation working
- [x] ML model training successful
- [x] Premium UI rendering correct
- [x] Mobile responsive design
- [x] Dark/Light theme toggle
- [x] CSV exports functional
- [x] Error handling graceful
- [x] Date filters working

---

## 🚀 Deployment Notes

### Local Development
- Run: `streamlit run app.py`
- Uses local SQLite database
- All data cached for performance

### Production Deployment
- Use Streamlit Cloud or Docker
- Consider remote database connection
- Implement authentication
- Set up scheduled data ingestion
- Monitor ML model performance

### Backup & Recovery
- Backup created: `Merlin_MLM_Dashboard_Backup_20260510_0014.zip`
- Backup location: `c:\Users\amjad\OneDrive\Documents\`
- Size: ~84 MB (includes all data)

---

## 📞 Support & Maintenance

### Common Issues
1. **Data not loading**: Click "Clear Cache" button
2. **ML model errors**: Check sklearn installation
3. **Database lock**: Restart Streamlit app
4. **Missing columns**: Verify CSV format matches schema

### Maintenance Tasks
- Weekly: Monitor delivery/RTO rates
- Monthly: Review warehouse recommendations
- Quarterly: Retrain ML models with new data
- Bi-annually: Update courier performance baselines

---

## 📄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-10 | Initial release with all 6 dashboard sections |

---

**Project Status**: ✅ **PRODUCTION READY**

All features implemented, tested, and optimized for performance.
