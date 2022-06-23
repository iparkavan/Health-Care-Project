# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:23:29 2022

@author: DK
"""


import io
import cv2
import boto3

import trp, json

from PIL import Image, ImageDraw

from Extract import Extract
from ExtractMedicalInfo import ExtractMedicalInfo

bucket = "textract-console-ap-south-1-13d8bdf3-2ddb-471a-a8ca-3ea2325bd65"
document = "med1.jpg"
region = "ap-south-1"

def getS3Client():
    client = boto3.client('textract', 
                          region_name=region,
                          aws_access_key_id="AKIAWOINZBSCR2Q6ZMLQ", 
                          aws_secret_access_key="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")
    
    return client

def getResponse(client):
    response = client.analyze_document(
                Document={'S3Object': {'Bucket': bucket, 'Name': document}},
                FeatureTypes=["TABLES", "FORMS"])
    
    return response


def run():
    
    print("** Inside main run method ***")
    client = getS3Client()
    response = getResponse(client)
    
    extract = Extract(response)   
    keyValuePairs , tableContents , lineContents = extract.extractContent()
    
    extractMedicalInfo = ExtractMedicalInfo(keyValuePairs , tableContents , lineContents)
    extractMedicalInfo.extract()
    
    
    
if __name__ == "__main__":
    
    run()