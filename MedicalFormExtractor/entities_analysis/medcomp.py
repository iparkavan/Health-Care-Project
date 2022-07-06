import boto3
from rapidfuzz import fuzz
region = "us-east-1"


client = boto3.client('comprehendmedical',
                      region_name=region,
                      #aws_access_key_id="AKIAWOINZBSCR2Q6ZMLQ",
                      #aws_secret_access_key="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"
                      )



def get_avg_score(response):
    icd_response = {}
    for data in response:
        if data.get('ICD10CMConcepts'):
            for val in data.get('ICD10CMConcepts'):
                if val['Code'] in icd_response.keys():
                    val['Score'] = (val['Score'] + icd_response[val['Code']]['Score']) / 2
                    icd_response[val['Code']]['Score'] = val['Score']
                else :
                    icd_response[val['Code']] = val
    return list(icd_response.values())
    
def get_fuzzy_simularity(response, text):
    fuzzy_response = []
    for val in response:
        similarity = fuzz.partial_ratio(text, val['Description'])
        val['Score'] = (similarity + (val['Score'] * 100)) / 2
        fuzzy_response.append(val)
    return fuzzy_response
        
#@staticmethod
def get_icd_medcomp(text):
    code, desc, score = None, None, None
    icd_avg_response = []
    try:
        response = client.infer_icd10_cm(Text=text)
        icd_med_avg_response = get_avg_score(response['Entities'])
        icd_avg_response = get_fuzzy_simularity(icd_med_avg_response, text)
    except Exception:
        pass
    if len(icd_avg_response) == 1:
        if icd_avg_response[0]['Score'] >= 0.55:
            code = icd_avg_response[0]['Code']
            desc = icd_avg_response[0]['Description']
            return code, desc, None
    elif len(icd_avg_response) > 1:
        code_list = []
        for val in icd_avg_response:
            if val['Score'] >= 0.55:
                code_list.append(val)
        return None, None, code_list
    return None, None, None


#@staticmethod
def check_medcomp(response, code):
    if response:
        for val in response:
            if val['Code'] == code:
                return val['Code'], val['Description'], None
    return None, None, response
