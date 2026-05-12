# 📊 Merlin MLM Dashboard

A **premium operations & logistics analytics dashboard** built with Streamlit for real-time monitoring of MLM operations, inventory management, and supply chain optimization.

## ✨ Features

### 📈 **Overview Dashboard**
- Real-time inventory gap analysis
- Total logistics metrics (Dispatched, Delivered, RTO, Revenue)
- Shipment distribution by courier and payment mode
- Top cities by volume and RTO analysis
- Smart alerts for KPI thresholds

### 🏢 **B2B Analytics**
- B2B-specific KPIs and metrics
- Top client ranking by revenue
- Payment mode breakdown
- Financial performance tracking

### 👥 **D2C Analytics**
- D2C-specific metrics (isolated from B2B)
- Top cities by orders and revenue
- Geographic performance analysis
- Customer segment tracking

### 🏭 **Production Metrics**
- Production location KPIs
- Revenue and order count per facility
- Delivery rate by production location
- Average order value analysis

### 🔮 **ML Warehouse Prediction**
- Advanced RandomForest ML model
- Intelligent location scoring system
- 5 best warehouse recommendations
- Priority levels (High/Medium/Low)

### ⛓️ **Supply Chain Analytics**
- Courier partner performance
- Route efficiency analysis
- Delivery rate comparison
- Best performer identification

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

Dashboard will be available at: **http://localhost:8501**

### Deploy to Streamlit Cloud

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Merlin MLM Dashboard"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Sign in with GitHub account
   - Click "New app"
   - Select your repository and branch
   - Set main file path to `app.py`
   - Deploy!

## 📁 Project Structure

```
.
├── app.py                 # Main Streamlit dashboard
├── ml_engine.py          # Analytics & ML functions
├── pipeline.py           # Data ingestion pipeline
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── processed_db/
│   └── warehouse.db     # SQLite database
├── raw_data/            # Input CSV/XLSX files
└── archive/             # Processed data backups
```

## 🔧 Tech Stack

- **Frontend**: Streamlit 1.57.0
- **Backend**: Python 3.x
- **Database**: SQLite
- **Data Processing**: Pandas, NumPy
- **ML**: Scikit-learn
- **UI**: Custom CSS with dark/light theme

## 📊 Core Functions

### Analytics Functions (ml_engine.py)

- `get_inventory_gap()` - Inventory analysis
- `get_logistics_summary(start_date, end_date)` - Overall metrics
- `get_b2b_analytics(start_date, end_date)` - B2B specific
- `get_d2c_analytics(start_date, end_date)` - D2C specific
- `get_production_metrics(start_date, end_date)` - Production KPIs
- `predict_warehouse_locations(top_n=5)` - ML predictions
- `get_supply_chain_metrics(start_date, end_date)` - Supply chain

### Data Pipeline (pipeline.py)

- `run_pipeline()` - Smart incremental data ingestion
  - Detects new files in `raw_data/`
  - Deduplicates using unique keys
  - Appends only new records
  - Archives processed files

## 💾 Database Schema

### Tables
- **so_master**: Sales Orders
- **dispatch_table**: Dispatch Records
- **kitting_table**: Kitting/Assembly
- **clickpost_table**: Logistics Tracking

## 🎨 UI Features

- 🌓 Dark/Light theme toggle
- 📱 Mobile-responsive layout
- ✨ Glassmorphism design
- 🚀 Data caching system
- 📥 CSV export functionality
- ⚠️ Smart alert system

## 📈 Key Metrics

### Operational KPIs
- Total Orders Dispatched
- Successful Deliveries
- Return To Origin (RTO)
- Delivery Rate (%)
- Average Order Value

### Financial Metrics
- Total Revenue
- Revenue by Segment (B2B/D2C)
- Revenue by Location
- Revenue by Route

### Supply Chain Metrics
- Warehouse Recommendation Score
- Delivery Rate by Location
- Route Efficiency
- Courier Performance

## 🔮 ML Model

### Warehouse Prediction
- **Algorithm**: Random Forest Regressor
- **Scoring**: Orders (30%) + Delivery Rate (30%) + ML Score (40%)
- **Output**: Top 5 locations with priority levels
- **Retraining**: Automatic on new data

## 🛠️ Configuration

### Streamlit Config (`.streamlit/config.toml`)
- Theme colors matching brand
- Dark mode enabled by default
- CORS disabled for security
- Toolbar in developer mode

### Environment Variables
- `DB_PATH`: Path to SQLite database (default: `processed_db/warehouse.db`)
- `RAW_FOLDER`: Path to input files (default: `raw_data/`)
- `ARCHIVE_FOLDER`: Path to backups (default: `archive/`)

## 📋 Data Ingestion

### Expected File Format
- **Dispatch**: `*dispatch*.csv`
- **SO**: `*so*.csv`
- **Kitting**: `*kitting*.xlsx`
- **ClickPost**: `*CLICKPOST*.csv`

### Deduplication Keys
- Dispatch/SO: `OrderNo`
- Kitting: `KitNo`
- ClickPost: `AWB`

## ⚠️ Alerts & Thresholds

- RTO Rate > 3%: Warning
- Delivery Rate < 80%: Alert
- Over-dispatched items: Error

## 📞 Support

### Common Issues

1. **Data not loading**
   - Click "🗑️ Clear Cache" in sidebar
   - Check if database exists: `processed_db/warehouse.db`

2. **ML model errors**
   - Ensure scikit-learn is installed: `pip install scikit-learn==1.8.0`
   - Check for sufficient data in database

3. **Dashboard slow**
   - Clear cache
   - Check date range filters
   - Monitor database size

## 🚀 Production Deployment

### Streamlit Cloud (Recommended)
- Free tier available
- Auto-deploy from GitHub
- Managed hosting and scaling
- Custom domain support

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### On-Premises
- Windows Server with Python 3.7+
- SQLite or PostgreSQL database
- Scheduled data ingestion
- Reverse proxy (IIS/Nginx)

## 📝 License

Private project for Merlin MLM Operations

---

**Created**: May 10, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
