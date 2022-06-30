import pandas as pd
import logging
from data_ingestion.db_utils import engine

logger = logging.getLogger(__name__)

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

