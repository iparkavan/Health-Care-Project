from data_ingestion.process_log import DataLog
import pandas as pd
from data_ingestion.db_utils import engine
from uuid import uuid4
from datetime import datetime

if __name__ == "__main__":
    record = {
        "request_uuid": f"{uuid4()}",
        "uploaded_s3_path":"s3://test/test.pdf",
        "event_received": datetime.utcnow(),
        "submitted_to_textract": datetime.utcnow(),
        "response_from_textract":datetime.utcnow(),
        "transformation_start":datetime.utcnow(),
        "transformation_end":datetime.utcnow(),
        "follow_up_reason": "test reason",
        "event_completed": datetime.utcnow(),
    }
    # df = pd.DataFrame([record])
    # df.to_sql("process_log", con=engine, index=False, if_exists='append')
    log = DataLog(**record)
    log.follow_up_reason="Testing the record"
    log.update_record()