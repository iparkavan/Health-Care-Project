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

def get_dump_record(icd_code):
    result = None
    if len(icd_code) > 3 and '.' not in icd_code:
        icd_code = icd_code[:3] + "." + icd_code[3:]
    try:
        query = f"""select * from public.icd_dump where code = '{icd_code}'"""
        result = engine.execute(query).fetchone()
        if result:
            return result[1]
    except:
        pass
    return result

def get_dump_record_all():
    result = None
    try:
        query = f"""select * from public.icd_dump"""
        result = engine.execute(query).fetchall()
        if result:
            return result
    except:
        pass
    return result

def insert_dump_record(data):
    if len(data["Code"]) > 3 and '.' not in data["Code"]:
        data["Code"] = data["Code"][:3] + "." + data["Code"][3:]
    if not get_dump_record(data['Code']):
        try:
            query = f"""insert into public.icd_dump values('{data["Code"]}', '{data["Description"]}')"""
            conn = engine.connect()
            conn.execute(query)
            conn.close()
            logger.info(f"""New ICD info added: Code:'{data["Code"]}', Descrition:'{data["Description"]}')""")
        except:
            logger.warning(f"""Error!!! Not able to add ICD info: Code:'{data["Code"]}', Descrition:'{data["Description"]}')""")
    return data