import pandas as pd
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/gold_db")

def get_db_engine():
    """Create and return a database engine."""
    return create_engine(DATABASE_URL)

def load_data_from_db():
    """Query gold prices from the database and return as a DataFrame."""
    engine = get_db_engine()
    # Check if table exists (simplified for this exercise)
    try:
        df = pd.read_sql("SELECT * FROM gold_prices", engine)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        return df
    except Exception as e:
        print(f"Error loading from DB: {e}")
        return None
