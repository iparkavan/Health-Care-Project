import json
from rapidfuzz import fuzz
from dotenv import load_dotenv
from data_ingestion.data_ingest import get_dump_record_all
import os
load_dotenv()

class ICDMatcher:

    def __init__(self, data):
        self._data = data
        self._key = None
        self._icd_desc = None
        self._max_match = 70
        self._key_list = []

    def remove_duplicates(self):
        icd_names = []
        new_icd_list = []
        for val in self._key_list:
            if val['Code'] in icd_names:
                continue
            else:
                icd_names.append(val['Code'])
                new_icd_list.append(val)
        return new_icd_list

    def get_icd_data_fuzz(self):
        icd_records = get_dump_record_all()
        if icd_records:
            for data in icd_records:
                similarity = fuzz.partial_ratio(self._data, data[1])
                if similarity >= self._max_match:
                    self._key_list.append({
                        'Code': data[0],
                        'Description': data[1],
                        'Score': similarity,
                        'Mode': 'dump'
                    })
        if self._key_list:
            self._key_list = sorted(self._key_list, key=lambda d : d['Score'] , reverse= True)[:50]
            self._key_list = self.remove_duplicates()
        if len(self._key_list) == 1:
            return self._key_list[0]['Code'], self._key_list[0]['Description'], None
        elif len(self._key_list) > 1:
            return None, None, self._key_list
        return None, None, None

    @staticmethod
    def check_datadump(response, code):
        if response:
            for val in response:
                if val['Code'] == code:
                    return val['Code'], val['Description'], None
        return None, None, response
