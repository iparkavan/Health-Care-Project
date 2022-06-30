from pydantic import BaseModel
from datetime import datetime

class DataLog(BaseModel):
    request_uuid: str
    uploaded_s3_path: str
   
    event_received: Optional[datetime]
    
    submitted_to_textract: Optional[datetime]
    response_from_textract: Optiona[datetime]

    transformation_start: Optional[datetime]
    transformation_end: Optional[datetime]



    follow_up_reason: str
    
    event_completed: Optional[datetime]

    
