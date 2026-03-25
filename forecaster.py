import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import datetime

def generate_forecast(df, periods=30):
    """Generate price forecast using ARIMA."""
    # We only need the Close price
    data = df['Close'].values
    
    # Simple ARIMA model - parameters (5,1,0) are often a good starting point for financial data
    model = ARIMA(data, order=(5,1,0))
    model_fit = model.fit()
    
    # Forecast
    forecast = model_fit.get_forecast(steps=periods)
    forecast_values = forecast.predicted_mean
    conf_int = forecast.conf_int(alpha=0.05)
    
    # Create a DataFrame for the forecast
    last_date = df['Date'].iloc[-1]
    forecast_dates = [last_date + datetime.timedelta(days=i+1) for i in range(periods)]
    
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Forecast': forecast_values,
        'Lower Bound': conf_int[:, 0],
        'Upper Bound': conf_int[:, 1]
    })
    
    return forecast_df
