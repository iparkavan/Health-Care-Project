from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from data_ingestion.db_utils import engine
from sqlalchemy import text
from logging import getLogger

logger = getLogger(__name__)

LOG_TABLE = "process_log"

ddl = """
CREATE TABLE IF NOT EXISTS public.process_log (
	request_uuid text NULL,
	uploaded_s3_path text NULL,
	event_received timestamp NULL,
	submitted_to_textract timestamp NULL,
	response_from_textract timestamp NULL,
	transformation_start timestamp NULL,
	transformation_end timestamp NULL,
	follow_up_reason text NULL,
	event_completed timestamp NULL,
    primary key(request_uuid)
);
"""

response = engine.execute(ddl)

logger.info(f"Table creation script {response.rowcount}")

class DataLog(BaseModel):
    request_uuid: str
    uploaded_s3_path: str
    event_received: datetime
    submitted_to_textract: Optional[datetime]
    response_from_textract: Optional[datetime]
    transformation_start: Optional[datetime]
    transformation_end: Optional[datetime]
    follow_up_reason: Optional[str]
    event_completed: Optional[datetime]

    def get_conflict_columns(self):
        return ['request_uuid']

    def update_record(self):
        
        record = self.dict(exclude_none=True)
        col_names = list(record.keys())
        values = ", ".join([f":{col}" for col in col_names])
        conflict_columns = self.get_conflict_columns()
        update_values = ", ".join([f"{col}=:{col}" for col in col_names if col not in conflict_columns])
        query = """INSERT INTO public.{table_name} ({columns}) values ({values}) 
                   ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_values}"""

        query = query.format(table_name=LOG_TABLE,
                             columns=", ".join(col_names),
                             values=values,
                             conflict_cols=", ".join(conflict_columns),
                             update_values=update_values
                             )

        sql_query = text(query)

        response = engine.execute(sql_query, **record)

        return response.rowcount
