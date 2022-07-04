from cloudpathlib import S3Path
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()
def update_configuration_files():
    s3_folder = S3Path("s3://data-store-igs/config")

    for file in s3_folder.glob("**/*"):
        file.download_to(os.environ['CONFIG_FILES'])
        logger.info(f"Updated the file from {file}")
