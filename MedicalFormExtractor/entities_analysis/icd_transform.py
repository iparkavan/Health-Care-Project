import json
import string

from entities_analysis.xml_parse import ICD


class ICDTransform:

    def __init__(self, icd_val):
        self._icd_value = icd_val.strip()
        self._icd_value_new = None
        self._result = {
            'Response': 'False'
        }

    def tranform_gen_icd(self):
        if not self._icd_value[0].isalpha():
            if self._icd_value[0] == '1' and len(self._icd_value.split('.')[0]) > 2:
                self._icd_value = 'I' + self._icd_value[1:]
                icdObj1 = ICD(self._icd_value)
                icdResponse1 = icdObj1.run()
                if icdResponse1.get('Response') == 'True':
                    return icdResponse1
            elif len(self._icd_value.split('.')[0]) < 3:
                for letter in string.ascii_uppercase:
                    self._icd_value_new = letter + self._icd_value
                    icdObj2 = ICD(self._icd_value_new)
                    icdResponse2 = icdObj2.run()
                    if icdResponse2.get('Response') == 'True':
                        return icdResponse2
            elif len(self._icd_value) >= 3:
                for letter in string.ascii_uppercase:
                    self._icd_value_new = letter + self._icd_value[0:2] + '.' + self._icd_value[2:]
                    icdObj3 = ICD(self._icd_value_new)
                    icdResponse3 = icdObj3.run()
                    if icdResponse3.get('Response') == 'True':
                        return icdResponse3
            return self._result
