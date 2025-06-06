import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def generate_stock_info():

    load_dotenv()

    try:
        df=pd.read_csv('src/stock_data.csv')
        
        DATABASE_URL = os.environ.get("DATABASE_URL")

        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")

        engine = create_engine(DATABASE_URL)
        df.to_sql("stock_info", engine, if_exists='replace', index=False)

        engine.dispose()


        return {"message": f"Stock info generated successfully", "status": 200}
    except Exception as e:
        return {"message": f"Error generating stock info: {str(e)}", "status": 500}