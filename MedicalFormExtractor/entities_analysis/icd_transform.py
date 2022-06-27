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
        self._icd_value_list = []

    def remove_duplicates(self):
        icd_names = []
        new_icd_list = []
        for val in self._icd_value_list:
            if val['Name'] in icd_names:
                continue
            else:
                icd_names.append(val['Name'])
                new_icd_list.append(val)
        return new_icd_list

    def tranform_gen_icd(self):
        if not self._icd_value[0].isalpha():
            if len(self._icd_value.split('.')[0]) < 3:
                for letter in string.ascii_uppercase:
                    self._icd_value_new = letter + self._icd_value
                    icdObj2 = ICD(self._icd_value_new)
                    icdResponse2 = icdObj2.run_dump()
                    if icdResponse2.get('Response') == 'False':
                        icdResponse2 = icdObj2.run_api()
                    if icdResponse2.get('Response') == 'True':
                        self._icd_value_list.append({
                            'Name': icdResponse2.get('Name'),
                            'Description': icdResponse2.get('Description'),
                            'Mode': icdResponse2.get('Mode')
                        })
            elif len(self._icd_value) >= 3:
                for letter in string.ascii_uppercase:
                    self._icd_value_new = letter + self._icd_value[0:2] + '.' + self._icd_value[2:]
                    icdObj3 = ICD(self._icd_value_new)
                    icdResponse3 = icdObj3.run_dump()
                    if icdResponse3.get('Response') == 'False':
                        icdResponse3 = icdObj3.run_api()
                    if icdResponse3.get('Response') == 'True':
                        self._icd_value_list.append({
                            'Name': icdResponse3.get('Name'),
                            'Description': icdResponse3.get('Description'),
                            'Mode': icdResponse3.get('Mode')
                        })

            if self._icd_value_list:
                if len(self._icd_value_list) == 1:
                    return {
                        'Response': 'True',
                        '_icd_value_list': self._icd_value_list,
                        'Name': self._icd_value_list[0]['Name'],
                        'Description': self._icd_value_list[0]['Description'],
                        'Mode': self._icd_value_list[0]['Mode']
                    }
                else:
                    return {
                        'Response': 'True',
                        '_icd_value_list': self.remove_duplicates()
                    }
            return self._result
