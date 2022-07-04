import json
import io
import urllib.parse
import boto3
import fitz
from pathlib import Path
from pprint import pprint
from datetime import datetime
import logging

from utils.utils import update_configuration_files
update_configuration_files()

from entities_analysis.checks import Checkups
from entities_analysis.transformations import MedTransformation

from data_ingestion.data_ingest import insert_records
from data_ingestion.process_log import DataLog

from medicalformextractor.Extract import Extract
from medicalformextractor.ExtractMedicalInfo import ExtractMedicalInfo



logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.resource('s3')
textract = boto3.client("textract", region_name='us-east-1')
s3_cli = boto3.client('s3')


def getResponse(bucket, key):
    response = textract.analyze_document(
        Document={'S3Object': {'Bucket': bucket, 'Name': key}},
        FeatureTypes=["TABLES", "FORMS"])

    return response


def ocr_pages(pdf, bucket, file_name):
    bucket_obj = s3.Bucket(bucket)
    all_pages_responses = []
    for i, page in enumerate(pdf):  # iterate through the pages
        pix = page.get_pixmap()
        bytes = pix.tobytes(output='png')  # render page to an image
        image_key = f"processed/{file_name.stem}_{i}.png"
        response_key = f"processed/{file_name.stem}_{i}.json"
        bucket_obj.upload_fileobj(io.BytesIO(bytes), image_key)

        # Run the textract on the image
        response = getResponse(bucket, image_key)
        s3_cli.put_object(
            Body=json.dumps(response),
            Bucket=bucket,
            Key=response_key
        )
        all_pages_responses.append(response)
    return all_pages_responses



def process_file(bucket, key, request_id, data_log: DataLog):
    try:
        bucket_obj = s3.Bucket(bucket)
        obj = s3.Object(bucket, key)
        fs = obj.get()['Body'].read()
        pdf = fitz.open(stream=io.BytesIO(fs))
        n_pages = pdf.page_count
        file_name = Path(key)
        print(f"File {key} has {n_pages} page(s)")
        data_log.submitted_to_textract = datetime.utcnow()
        data_log.update_record()
        all_pages_responses = ocr_pages(pdf, bucket, file_name)

        data_log.response_from_textract = datetime.utcnow()
        data_log.update_record()

        print(f"Text extracted from all the pages.")
        # Run the data extractor

        data_log.transformation_start = datetime.utcnow()
        data_log.update_record()
        
        extract = Extract(all_pages_responses)
        keyValuePairs, tableContents, lineContents = extract.extractContent()
        extractMedicalInfo = ExtractMedicalInfo(keyValuePairs, tableContents, lineContents)
        extractMedicalInfo.extract()
        logger.info(f"Extracted first level of information")
        # Fix ICD10 codes
        transformedInfo = MedTransformation()
        transformedInfo.run(extractMedicalInfo)
        finalMedJson = transformedInfo.mapMedInfo(extractMedicalInfo)
        
        data_log.transformation_end = datetime.utcnow()
        data_log.update_record()
        
        logger.info(f"Applied Medical transformations")
        checks = Checkups()
        finaljson = checks.prime_checks(finalMedJson)
        pprint(finaljson)
        #Data Ingestion
        response = insert_records([finaljson], "MedicalInfoExtractData")
        print(" response of Insertion", response)
        # Save the json to S3 bucket
        response_key = f"extracted_info/{file_name.stem}_info.json"
        s3_cli.put_object(Body=json.dumps(finaljson), Bucket=bucket, Key=response_key)

        print(f"Completed extracting the data ...")
    except Exception as e:
        print(e)
        logger.error('Error processing {} from bucket {}.'.format(key, bucket), exc_info=True)

        # TODO: Insert the record to error table
        data_log.transformation_end = datetime.utcnow()
        data_log.follow_up_reason = f"Error occured while processing ... {e}"
        data_log.update_record()

def lambda_handler(event, context):
    request_id = context.aws_request_id
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    data_log = DataLog(request_uuid=request_id, uploaded_s3_path=f"s3://{bucket}/{key}", event_received=datetime.utcnow())
    data_log.update_record()
    process_file(bucket, key, request_id, data_log)
    data_log.event_completed = datetime.utcnow()
    data_log.update_record()
