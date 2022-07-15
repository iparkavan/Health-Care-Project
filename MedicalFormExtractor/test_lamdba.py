import json
import io
import urllib.parse
import boto3
import fitz
from pathlib import Path
from pprint import pprint
from datetime import datetime
import logging

import trp

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



def process_file():
  
    extractMedicalInfo = ExtractMedicalInfo()
    all_pages_responses = []
 
    for i in range(3):
        filename = "Referral_Form_{}.json".format(i)
        with open(filename,"r", encoding='utf-8') as freader:
            cnt = json.load(freader)
            """
            extract = Extract(cnt)
            keyValuePairs, tableContents, lineContents = extract.extractContent()
            #print(keyValuePairs)
            extractMedicalInfo.extract(keyValuePairs , tableContents , lineContents)
            """
        all_pages_responses.append(cnt)
       
    print(f"Text extracted from all the pages.")
    
    print("*******************************************")
   
    # Run the data extractor




    extract = Extract(all_pages_responses)
    keyValuePairs, tableContents, lineContents = extract.extractContent()
    extractMedicalInfo.extract(keyValuePairs , tableContents , lineContents)
    extractMedicalInfo = extractMedicalInfo.generateJsonMessage()
   

   
if __name__ == "__main__":
    process_file()
