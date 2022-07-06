import json
from rapidfuzz import fuzz
from dotenv import load_dotenv
import os
load_dotenv()

class ICDMatcher:

    def __init__(self, data):
        self._data = data
        self._key = None
        self._icd_desc = None
        self._max_match = 80
        self._key_list = []

    def remove_duplicates(self):
        icd_names = []
        new_icd_list = []
        for val in self._key_list:
            if val['Name'] in icd_names:
                continue
            else:
                icd_names.append(val['Name'])
                new_icd_list.append(val)
        return new_icd_list

    def get_icd_data_fuzz(self):
        with open(f"{os.environ.get('CONFIG_FILES', os.curdir)}/icd10_desc.json", 'r') as icd_file:
            icd_dict_data_1 = json.load(icd_file)
            for key, val in icd_dict_data_1.items():
                similarity = fuzz.partial_ratio(self._data, val[1])
                if similarity >= self._max_match:
                    if '.' not in key and len(key) > 3:
                        key = key[:3] + '.' + key[3:]
                    self._key_list.append({
                        'Name': key,
                        'Description': val[1],
                        'Score': similarity,
                        'Mode': 'data'
                    })
        with open(f"{os.environ.get('CONFIG_FILES', os.curdir)}/icd_dump.json", 'r') as icd_file:
            icd_dict_data_2 = json.load(icd_file)
            for key, val in icd_dict_data_2.items():
                similarity = fuzz.partial_ratio(self._data, val['desc'])
                if similarity >= self._max_match:
                    if '.' not in key and len(key) > 3:
                        key = key[:3] + '.' + key[3:]
                    self._key_list.append({
                        'Name': key,
                        'Description': val['desc'],
                        'Score': similarity,
                        'Mode': 'data'
                    })
        self._key_list = self.remove_duplicates()
        if len(self._key_list) == 1:
            return self._key_list[0]['Name'], self._key_list[0]['Description'], None
        elif len(self._key_list) > 1:
            return None, None, self._key_list
        return None, None, None

    @staticmethod
    def check_datadump(response, code):
        if response:
            for val in response:
                if val['Name'] == code:
                    return val['Name'], val['Description'], None
        return None, None, response
