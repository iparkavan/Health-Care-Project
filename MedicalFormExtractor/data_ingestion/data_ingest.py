import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

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
    try:
        response = df.to_sql(table_name, con=engine, if_exists='append', index=False)
    except Exception as e:
        logger.error(f"Unable to insert data to database", exc_info=True)
        response = None
    return response

