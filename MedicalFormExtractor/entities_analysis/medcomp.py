import boto3
region = "us-east-1"


client = boto3.client('comprehendmedical',
                      region_name=region,
                      #aws_access_key_id="AKIAWOINZBSCR2Q6ZMLQ",
                      #aws_secret_access_key="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"
                      )


#@staticmethod
def get_icd_medcomp(text):
    code, desc, score = None, None, None
    icd_response = []
    try:
        response = client.infer_icd10_cm(Text=text)
        icd_response = response['Entities'][0]['ICD10CMConcepts']
    except Exception:
        pass
    if len(icd_response) == 1:
        if response['Entities'][0]['ICD10CMConcepts'][0]['Score'] >= 0.60:
            code = response['Entities'][0]['ICD10CMConcepts'][0]['Code']
            desc = response['Entities'][0]['ICD10CMConcepts'][0]['Description']
            return code, desc, None
    elif len(icd_response) > 1:
        code_list = []
        for val in icd_response:
            if val['Score'] >= 0.60:
                code_list.append(val)
        return None, None, code_list
    return None, None, None


#@staticmethod
def check_medcomp(response, code):
    for val in response:
        if val['Code'] == code:
            return val['Code'], val['Description'], None
    return None, None, response
