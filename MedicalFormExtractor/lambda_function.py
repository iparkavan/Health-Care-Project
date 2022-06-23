import json
import io
import urllib.parse
import boto3
import fitz
from pathlib import Path
from medicalformextractor.Extract import Extract
from medicalformextractor.ExtractMedicalInfo import ExtractMedicalInfo
from entities_analysis.xml_parse import ICD
from entities_analysis.icd_analyzer import ICDMatcher
from entities_analysis.icd_transform import ICDTransform
from pprint import pprint


s3 = boto3.resource('s3')
textract = boto3.client("textract", region_name='ap-south-1')
s3_cli = boto3.client('s3')


def getResponse(bucket, key):
    response = textract.analyze_document(
                Document={'S3Object': {'Bucket': bucket, 'Name': key}},
                FeatureTypes=["TABLES", "FORMS"])
    
    return response

def fix(parsed_icd_code, parsed_icd_desc):
    if not parsed_icd_desc and parsed_icd_code:
        # ICD Code is given/invalid and No ICD desc
        icdObj = ICD(parsed_icd_code)
        icdResponse = icdObj.run()
        print(icdResponse)
        if icdResponse.get('Response') == 'True':
            parsed_icd_code = icdResponse.get('Name')
            parsed_icd_desc = icdResponse.get('Description')
        if icdResponse.get('Response') == 'False' and icdObj._logger[0] == 'Invalid ICD code':
            icdObj2 = ICDTransform(parsed_icd_code)
            icdResponse2 = icdObj2.tranform_gen_icd()
            print(icdResponse2)
            if icdResponse2.get('Response') == 'True':
                parsed_icd_code = icdResponse2.get('Name')
                parsed_icd_desc = icdResponse2.get('Description')

    if parsed_icd_desc and not parsed_icd_code:
        # ICD Desc is given and No ICD Code - Match >= 65%
        myobj = ICDMatcher(parsed_icd_desc)
        match_score, icd_key, icd_value = myobj.get_icd_data()
        print(match_score, icd_key, icd_value)
        if match_score:
            parsed_icd_code = icd_key
            parsed_icd_desc = icd_value

    if parsed_icd_desc and parsed_icd_code:
        # ICD Code is given and ICD desc is given
        # Verify Match >= 80%
        # Else fetch ICD Code based on desc - match >= 65%
        icdObj = ICD(parsed_icd_code)
        icdResponse = icdObj.run()
        if icdResponse.get('Response') == 'True':
            myobj = ICDMatcher(parsed_icd_desc)
            match_score, icd_key, icd_value = myobj.get_icd_data()
            print(match_score, icd_key, icd_value)
            if match_score:
                parsed_icd_code = icd_key
                parsed_icd_desc = icd_value

    return parsed_icd_code, parsed_icd_desc


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
        keyValuePairs , tableContents , lineContents = extract.extractContent()
        extractMedicalInfo = ExtractMedicalInfo(keyValuePairs , tableContents , lineContents)
        extractMedicalInfo.extract()

        # Fix ICD10 codes
        parsed_icd_code, parsed_icd_desc = extractMedicalInfo._icd_code, extractMedicalInfo._icd_desc
        parsed_icd_code, parsed_icd_desc = fix(parsed_icd_code, parsed_icd_desc)
        extractMedicalInfo._icd_code, extractMedicalInfo._icd_desc = parsed_icd_code, parsed_icd_desc

        # Get the record
        record = extractMedicalInfo.get_extracted_record()

        pprint(record)
        response_key = f"extracted_info/{file_name.stem}_info.json"
        s3_cli.put_object(Body=json.dumps(record), Bucket=bucket, Key=response_key)
        
        print(f"Completed extracting the data ...")
    except Exception as e:
        print(e)
        print('Error processing {} from bucket {}.'.format(key, bucket))


def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    process_file(bucket, key)