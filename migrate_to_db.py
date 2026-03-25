import pandas as pd
from sqlalchemy import create_engine
import os

# Database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/gold_db")

def migrate():
    print("🚀 Starting migration...")
    
    # Load CSV
    df = pd.read_csv("GoldUSD.csv")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    
    # Connect to DB
    engine = create_engine(DATABASE_URL)
    
    # Push to SQL
    # 'if_exists="replace"' is okay for a one-time migration
    df.to_sql('gold_prices', engine, if_exists='replace', index=False)
    
    print(f"✅ Successfully migrated {len(df)} records to PostgreSQL!")

if __name__ == "__main__":
    migrate()
