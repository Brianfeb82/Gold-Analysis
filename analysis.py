import pandas as pd
import numpy as np

def clean_data(df):
    """Clean the GoldUSD dataset."""
    df = df.copy()
    # Handle the DD-MM-YY format
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values('Date')
    return df

def add_indicators(df):
    """Add financial indicators for analysis."""
    df = df.copy()
    # Moving Averages
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # Volatility (Daily Returns)
    df['Returns'] = df['Close'].pct_change()
    df['Volatility'] = df['Returns'].rolling(window=21).std() * np.sqrt(252) # Annualized
    
    return df

def get_summary_stats(df):
    """Calculate key performance metrics."""
    total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
    current_price = df['Close'].iloc[-1]
    ath = df['High'].max()
    
    return {
        "Total Return (%)": f"{total_return:.2f}%",
        "Current Price (USD)": f"${current_price:,.2f}",
        "All-Time High": f"${ath:,.2f}",
        "Records": len(df)
    }

def calculate_investment_return(df, purchase_date, amount):
    """Calculate ROI based on a purchase date and amount."""
    # Find the closest date available in the dataset
    df_date = df[df['Date'] <= pd.to_datetime(purchase_date)].iloc[-1:]
    
    if df_date.empty:
        return None
    
    purchase_price = df_date['Close'].values[0]
    current_price = df['Close'].iloc[-1]
    
    units = amount / purchase_price
    current_value = units * current_price
    profit = current_value - amount
    roi = (profit / amount) * 100
    
    return {
        "Purchase Price": purchase_price,
        "Current Value": current_value,
        "Profit": profit,
        "ROI (%)": roi,
        "Units Owned": units
    }

def calculate_drawdowns(df):
    """Calculate historical drawdown metrics."""
    rolling_max = df['Close'].cummax()
    drawdown = (df['Close'] - rolling_max) / rolling_max
    
    return drawdown

def calculate_rsi(df, window=14):
    """Calculate Relative Strength Index."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands."""
    middle_band = df['Close'].rolling(window=window).mean()
    std_dev = df['Close'].rolling(window=window).std()
    
    upper_band = middle_band + (std_dev * num_std)
    lower_band = middle_band - (std_dev * num_std)
    
    return upper_band, middle_band, lower_band
