import pandas as pd
from data_ingestion.db_utils import engine
import io

filename = 'data_file.csv'
table_name = 'icd_dump'

df = pd.read_csv(filename)
df.columns=['code', 'description']
df.head(0).to_sql(table_name, engine, if_exists='replace',index=False) #drops old table and creates new empty table

conn = engine.raw_connection()
cur = conn.cursor()
output = io.StringIO()
df.to_csv(output, sep='\t', header=False, index=False)
output.seek(0)
contents = output.getvalue()
cur.copy_from(output, table_name, null="") # null values become ''
conn.commit()
