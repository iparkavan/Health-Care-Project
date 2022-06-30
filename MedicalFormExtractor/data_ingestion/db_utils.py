from dotenv import load_dotenv
import os
import logging
from sqlalchemy import create_engine
logger = logging.getLogger(__name__)

load_dotenv()
def create_db_engine():
    db_url = os.environ['POSTGRES_URL']
    engine = create_engine(db_url)
    return engine

engine = create_db_engine()