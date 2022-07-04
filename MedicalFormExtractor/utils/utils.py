from cloudpathlib import S3Path
import logging
logger = logging.getLogger(__name__)
def update_configuration_files():
    s3_folder = S3Path("s3://data-store-igs/config")

    for file in s3_folder.glob("**/*"):
        file.download_to(".")
        logger.info(f"Updated the file from {file}")
