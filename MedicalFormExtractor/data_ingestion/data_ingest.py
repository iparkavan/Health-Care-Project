import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()
def create_db_engine():
    db_url = os.environ['POSTGRES_URL']
    engine = create_engine(db_url)
    return engine

engine = create_db_engine()


def insert_records(records, table_name):
    """
        records should be list of dictionaries
    """
    df = pd.DataFrame(records)
    response = df.to_sql(table_name, con=engine, if_exists='append', index=False)
    return response

