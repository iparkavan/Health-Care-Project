import requests

URL = 'http://icd10api.com/'
HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': 'en',
    'API-Version': 'v2'
}
PARAMS = {
    'desc': 'long',
    'r': 'json'
}


def extractapi(icd_val):
    result = {
        'Response': 'False'
    }
    response = {}
    try:
        PARAMS['code'] = icd_val.strip()
        response = requests.get(url=URL, headers=HEADERS, params=PARAMS, verify=False).json()
    except requests.exceptions.ConnectionError:
        pass

    if response.get('Response') == 'True':
        result['Response'] = 'True'
        result['Code'] = response['Name']
        result['Description'] = response['Description']
        result['Mode'] = 'api'
        if '.' not in result['Code'] and len(result['Code']) > 3:
            result['Code'] = result['Code'][:3] + '.' + result['Code'][3:]
    return result
