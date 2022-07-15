# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:23:29 2022

@author: DK
"""


import io,os
import boto3
import trp, json
import json
from PIL import Image, ImageDraw

from Extract import Extract
from ExtractMedicalInfo import ExtractMedicalInfo

bucket = "textract-console-ap-south-1-13d8bdf3-2ddb-471a-a8ca-3ea2325bd65"
document = "image0.jpg"
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
    
    extractMedicalInfo = ExtractMedicalInfo()
    print("** Inside main run method ***")
    client = getS3Client()
    response = getResponse(client)

    
    extract = Extract(response)   
    keyValuePairs , tableContents , lineContents = extract.extractContent()
    
    extractMedicalInfo.extract(keyValuePairs , tableContents , lineContents)
    
    jsonMessage = extractMedicalInfo.generateJsonMessage()
    print(jsonMessage)
    """
    if not os.path.exists("C:\\Users\\DK\\Desktop\\FUB\\poc\\pdf\\extract\\" + document):
        os.makedirs("C:\\Users\\DK\\Desktop\\FUB\\poc\\pdf\\extract\\" + document)
    with open("C:/Users/DK/Desktop/FUB/poc/pdf/extract/" + document + '/keyvalue.json', "w+") as f:
        json.dump(keyValuePairs, f)
    with open("C:/Users/DK/Desktop/FUB/poc/pdf/extract/" + document + '/linecontent.json', "w+") as f:
        json.dump(lineContents, f)
    with open("C:/Users/DK/Desktop/FUB/poc/pdf/extract/" + document + '/tablecontent.json', "w+") as f:
        json.dump(tableContents, f)
    with open("C:/Users/DK/Desktop/FUB/poc/pdf/extract/" + document + '/extract.json', "w+") as f:
        json.dump(jsonMessage, f)
    """
    
if __name__ == "__main__":
    
    run()
