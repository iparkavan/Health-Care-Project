import json
import io
import urllib.parse
import boto3
import fitz
from pathlib import Path
from data_ingestion.data_ingest import insert_records
from medicalformextractor.Extract import Extract
from medicalformextractor.ExtractMedicalInfo import ExtractMedicalInfo
from entities_analysis.transformations import MedTransformation
from pprint import pprint
import logging
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


def process_file(bucket, key):
    try:
        bucket_obj = s3.Bucket(bucket)
        obj = s3.Object(bucket, key)
        fs = obj.get()['Body'].read()
        pdf = fitz.open(stream=io.BytesIO(fs))
        n_pages = pdf.page_count
        file_name = Path(key)
        print(f"File {key} has {n_pages} page(s)")
        all_pages_responses = ocr_pages(pdf, bucket, file_name)
        print(f"Text extracted from all the pages.")
        # Run the data extractor
        extract = Extract(all_pages_responses)
        keyValuePairs, tableContents, lineContents = extract.extractContent()
        extractMedicalInfo = ExtractMedicalInfo(keyValuePairs, tableContents, lineContents)
        extractMedicalInfo.extract()
        logger.info(f"Extracted first level of information")
        # Fix ICD10 codes
        transformedInfo = MedTransformation()
        transformedInfo.run(extractMedicalInfo)
        finalMedJson = transformedInfo.mapMedInfo(extractMedicalInfo)
        logger.info(f"Applied Medical transformations")
        pprint(finalMedJson)
        #Data Ingestion
        response = insert_records([finalMedJson], "MedicalInfoExtractData")
        print(" response of Insertion", response)
        # Save the json to S3 bucket
        response_key = f"extracted_info/{file_name.stem}_info.json"
        s3_cli.put_object(Body=json.dumps(finalMedJson), Bucket=bucket, Key=response_key)

        print(f"Completed extracting the data ...")
    except Exception as e:
        print(e)
        logger.error('Error processing {} from bucket {}.'.format(key, bucket), exc_info=True)


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    process_file(bucket, key)
