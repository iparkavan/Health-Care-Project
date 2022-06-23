import json
import math
import re
from collections import Counter

WORD = re.compile(r"\w+")
CHAR = re.compile(r"\w")


class ICDMatcher:

    def __init__(self, data):
        self._data = data
        self._key = None
        self._icd_desc = None
        self._max_match = 0

    @staticmethod
    def get_cosine(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
        sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def get_cosine_avg(self, vec1, vec2):
        vec_word = self.get_cosine(vec1[0], vec2[0])
        vec_char = self.get_cosine(vec1[1], vec2[1])

        return (vec_word + vec_char) / 2

    @staticmethod
    def text_to_vector(word):
        words = WORD.findall(word)
        chars = CHAR.findall(word)
        return Counter(words), Counter(chars)

    def get_icd_data(self):
        vector1 = self.text_to_vector(self._data)
        with open('dataextract\icd10_desc.json', 'r') as icd_file:
            icd_dict_data_1 = json.load(icd_file)
            for key, val in icd_dict_data_1.items():
                vector2 = self.text_to_vector(val[1])
                cosine = self.get_cosine_avg(vector1, vector2)
                if cosine > self._max_match:
                    self._key = key
                    self._icd_desc = val[1]
                    self._max_match = cosine
        with open('dataextract\icd_dump.json', 'r') as icd_file:
            icd_dict_data_2 = json.load(icd_file)
            for key, val in icd_dict_data_2.items():
                vector2 = self.text_to_vector(val['desc'])
                cosine = self.get_cosine_avg(vector1, vector2)
                if cosine > self._max_match:
                    self._key = key
                    self._icd_desc = val['desc']
                    self._max_match = cosine
        if '.' not in self._key and len(self._key) > 3:
            self._key = self._key[:3] + '.' + self._key[3:]
        if self._max_match >= 0.65:
            return self._max_match, self._key, self._icd_desc
        return None, None, None
