import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis import clean_data, add_indicators, get_summary_stats, calculate_investment_return, calculate_drawdowns, calculate_rsi, calculate_bollinger_bands
from forecaster import generate_forecast
from database import load_data_from_db

# --- Page Configuration ---
st.set_page_config(
    page_title="GoldUSD Intelligence Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Premium Feel) ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        color: #FFD700;
        font-weight: 700;
    }
    .main {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Header & Sidebar ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d7/Gold-Bars.png", width=100)
    st.title("Settings")
    st.divider()
    
    # Load Data
    @st.cache_data
    def get_data():
        # Try loading from Database first (Engineering Move!)
        df = load_data_from_db()
        
        if df is None or df.empty:
            st.sidebar.warning("Database not found. Falling back to local CSV.")
            df = pd.read_csv("GoldUSD.csv")
            return clean_data(df)
        
        st.sidebar.success("✅ Connected to PostgreSQL Database")
        return df

    raw_df = get_data()
    
    # Date Filter
    start_date = st.date_input("Start Date", raw_df['Date'].min(), min_value=raw_df['Date'].min())
    end_date = st.date_input("End Date", raw_df['Date'].max(), max_value=raw_df['Date'].max())
    
    st.divider()
    st.info("Analysis based on DD-MM-YY historical trading data from Kaggle (2000-2026).")

# Filtering
df = raw_df[(raw_df['Date'].dt.date >= start_date) & (raw_df['Date'].dt.date <= end_date)]
df = add_indicators(df)
stats = get_summary_stats(df)

# --- Main Layout ---
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("🌟 Gold Intelligence Dashboard")
    st.markdown("*Real-time insights from 25 years of gold price history.*")

# KPI Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Price", stats["Current Price (USD)"])
m2.metric("Total Return", stats["Total Return (%)"])
m3.metric("All-Time High", stats["All-Time High"])
m4.metric("Trading Days", stats["Records"])

# --- Analysis Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Price Overview", "📉 Volatility Analysis", "🔮 AI Forecasting", "💰 Investment Simulator", "📈 Technical Analysis"])

with tab1:
    st.subheader("Historical Price Performance")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close Price', line=dict(color='#FFD700', width=2)))
    
    # Add MAs if long range
    if len(df) > 200:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], name='50d MA', line=dict(color='#00BFFF', width=1, dash='dot')))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['MA200'], name='200d MA', line=dict(color='#FF4500', width=1, dash='dot')))
    
    fig.update_layout(
        template="plotly_dark",
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Market Volatility Analysis")
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        # Annualized Volatility
        fig_vol = px.line(df, x='Date', y='Volatility', title="Rolling Annualized Volatility (21-day window)")
        fig_vol.update_layout(template="plotly_dark")
        st.plotly_chart(fig_vol, use_container_width=True)
    
    with col_v2:
        # Monthly Heatmap (Simplified)
        df_monthly = df.set_index('Date').resample('M')['Close'].last().pct_change().dropna()
        df_heatmap = df_monthly.reset_index()
        df_heatmap['Month'] = df_heatmap['Date'].dt.month_name()
        df_heatmap['Year'] = df_heatmap['Date'].dt.year
        
        heatmap_data = df_heatmap.pivot(index='Month', columns='Year', values='Close')
        # Reorder months
        months_ordered = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
        heatmap_data = heatmap_data.reindex(months_ordered)
        
        fig_heat = px.imshow(heatmap_data, labels=dict(color="Monthly Return"), title="Seasonality Heatmap")
        fig_heat.update_layout(template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)
    
    st.divider()
    st.subheader("🌋 Historical Drawdown (Worst Cases)")
    st.markdown("This chart shows how much the price dropped from its previous peak at any given time.")
    
    df['Drawdown'] = calculate_drawdowns(df)
    max_dd = df['Drawdown'].min() * 100
    
    st.metric("Maximum Drawdown in Period", f"{max_dd:.2f}%")
    
    fig_dd = px.area(df, x='Date', y='Drawdown', title="Historical Drawdown (%)", 
                     color_discrete_sequence=['#FF4500'])
    fig_dd.update_layout(template="plotly_dark", yaxis_tickformat=".2%")
    st.plotly_chart(fig_dd, use_container_width=True)

with tab3:
    st.subheader("Future Price Forecast (ARIMA Model)")
    st.write("Generating a 30-day forecast based on recent trends...")
    
    try:
        forecast_df = generate_forecast(raw_df, periods=30)
        
        fig_fc = go.Figure()
        
        # Plot last 100 days of history
        hist_trim = raw_df.tail(100)
        fig_fc.add_trace(go.Scatter(x=hist_trim['Date'], y=hist_trim['Close'], name='History', line=dict(color='#FFD700')))
        
        # Plot Forecast
        fig_fc.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecast'], name='Forecast', line=dict(color='#00FF00', dash='dash')))
        
        # Confidence Intervals
        fig_fc.add_trace(go.Scatter(
            x=forecast_df['Date'].tolist() + forecast_df['Date'].tolist()[::-1],
            y=forecast_df['Upper Bound'].tolist() + forecast_df['Lower Bound'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0,255,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Interval (95%)'
        ))
        
        fig_fc.update_layout(template="plotly_dark", height=600)
        st.plotly_chart(fig_fc, use_container_width=True)
        
        st.success("Forecast generated using an ARIMA model. Note: Past performance is not indicative of future results.")
    except Exception as e:
        st.error(f"Could not generate forecast: {e}")
        st.info("Ensure you have at least 100 data points and the `statsmodels` library installed.")

with tab4:
    st.subheader("💰 Gold Investment 'What-If' Simulator")
    st.markdown("Find out how much you would have made if you bought gold in the past.")
    
    col_sim1, col_sim2 = st.columns([1, 2])
    
    with col_sim1:
        sim_date = st.date_input("When did you buy?", value=pd.to_datetime("2010-01-01"), 
                                  min_value=df['Date'].min(), max_value=df['Date'].max())
        sim_amount = st.number_input("How much did you invest ($)?", min_value=100, value=1000, step=100)
    
    result = calculate_investment_return(raw_df, sim_date, sim_amount)
    
    if result:
        with col_sim1:
            st.divider()
            st.write(f"**Units Owned:** {result['Units Owned']:.3f} oz")
            st.write(f"**Purchase Price:** ${result['Purchase Price']:,.2f}/oz")
            
        with col_sim2:
            s1, s2 = st.columns(2)
            s1.metric("Current Value", f"${result['Current Value']:,.2f}", delta=f"${result['Profit']:,.2f}")
            s2.metric("Total ROI", f"{result['ROI (%)']:.2f}%")
            
            # Visualizing the growth
            sim_df = raw_df[raw_df['Date'] >= pd.to_datetime(sim_date)].copy()
            sim_df['Your Value'] = (sim_amount / result['Purchase Price']) * sim_df['Close']
            
            fig_sim = px.area(sim_df, x='Date', y='Your Value', title="Growth of your investment over time",
                              color_discrete_sequence=['#00FF00'])
            fig_sim.update_layout(template="plotly_dark")
            st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.warning("Please select a valid date within the dataset range.")

with tab5:
    st.subheader("📈 Advanced Technical Indicators")
    st.markdown("Use these professional indicators to identify overbought/oversold conditions and volatility ranges.")
    
    # --- Bollinger Bands ---
    st.divider()
    st.write("#### 1. Bollinger Bands")
    st.markdown("Shows price relative to volatility. Prices near the upper band are 'high', while prices near the lower band are 'low'.")
    
    df['Upper'], df['Mid'], df['Lower'] = calculate_bollinger_bands(df)
    
    fig_bb = go.Figure()
    fig_bb.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close', line=dict(color='#FFD700', width=2)))
    fig_bb.add_trace(go.Scatter(x=df['Date'], y=df['Upper'], name='Upper Band', line=dict(color='rgba(173, 216, 230, 0.4)', width=1)))
    fig_bb.add_trace(go.Scatter(x=df['Date'], y=df['Lower'], name='Lower Band', line=dict(color='rgba(173, 216, 230, 0.4)', width=1), fill='tonexty'))
    fig_bb.add_trace(go.Scatter(x=df['Date'], y=df['Mid'], name='Moving Average', line=dict(color='white', width=1, dash='dot')))
    
    fig_bb.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig_bb, use_container_width=True)
    
    # --- RSI ---
    st.divider()
    st.write("#### 2. RSI (Relative Strength Index)")
    st.markdown("Values above **70** suggest 'Overbought', while values below **30** suggest 'Oversold'.")
    
    df['RSI'] = calculate_rsi(df)
    
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI', line=dict(color='#00FF00', width=2)))
    
    # RSI Thresholds
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="cyan", annotation_text="Oversold")
    
    fig_rsi.update_layout(template="plotly_dark", height=400, yaxis_range=[0, 100])
    st.plotly_chart(fig_rsi, use_container_width=True)
