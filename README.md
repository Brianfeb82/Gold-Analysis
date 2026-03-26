# 🥇 GoldUSD Intelligence Dashboard

A professional-grade financial terminal built with **Streamlit** for analyzing, forecasting, and deriving insights from historical Gold-USD (XAU/USD) price data (2000–2026).

## 🚀 Live Demo
Check out the live dashboard here: **[Your Streamlit URL]**

## ✨ Features
- **📊 Interactive Overview**: Deep-dive into 25+ years of historical price performance.
- **🔮 AI Forecasting**: Statistical 30-day price projections using **ARIMA** models.
- **📉 Risk Analysis**: Real-time **Drawdown** calculations and Annualized Volatility tracking.
- **📈 Technical Analysis**: Professional indicators including **RSI** and **Bollinger Bands**.
- **💰 Investment Simulator**: "What-If" calculator to visualize historical returns and ROI.
- **🛡️ Engineering-First Design**: Containerized with **Docker**, backed by **PostgreSQL**, and features a robust CSV-fallback system.

## 🛠️ How to Run Locally

### Option 1: Docker (Recommended)
Launch the entire system (App + Database) with one command:
```bash
docker-compose up --build
```

### Option 2: Basic Streamlit
Install dependencies and run directly:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📂 Project Structure
- `app.py`: Main dashboard UI and layout.
- `analysis.py`: Quantitative library (VOL, RSI, Bollinger).
- `forecaster.py`: Time-series forecasting logic.
- `database.py`: PostgreSQL connection and persistence layer.
- `migrate_to_db.py`: Automated CSV-to-DB migration pipeline.

## 📈 Data Source
Historical data provided by the **Gold-USD Kaggle Dataset** (2000–Present).

---
*Created as part of an advanced AI Engineering project.*
