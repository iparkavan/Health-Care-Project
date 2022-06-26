from lxml import etree
from entities_analysis.icd_request import extractapi
import json

tree = etree.parse("icd10cm_tabular_2023.xml")
EXCLUDE_FIELDS = ['Name', 'Valid', 'Response']


class ICD:

    def __init__(self, icd_val):
        self._icd_value = icd_val.strip()
        self._error = False
        self._logger = []
        self._icd_value_new = None
        self._result = {
            'Response': 'False'
        }

    def get_gen_icd(self):
        if not self._icd_value[0].isalpha():
            self._error = True
            self._logger.append("Invalid ICD code")
            return
        if not self._icd_value[1:].replace('.', '').isalnum():
            self._error = True
            self._logger.append("Invalid ICD code")
            return
        if len(self._icd_value.split('.')[0]) > 3:
            self._error = True
            self._logger.append("Invalid ICD code")
            return

    def get_icd_data(self):
        with open('icd_dump.json', 'r') as icd_file:
            icd_dict = json.load(icd_file)
        if self._icd_value in icd_dict.keys():
            self._result["Response"] = 'True'
            self._result["Name"] = self._icd_value
            self._result["Description"] = icd_dict[self._icd_value]['desc']
            self._result["Mode"] = 'data'
            self._result['Details'] = icd_dict[self._icd_value]

    def get_icd_data_dump(self):
        with open('icd10_desc.json', 'r') as icd_file:
            icd_dict = json.load(icd_file)
        self._icd_value_new = self._icd_value.replace('.', '')
        if self._icd_value_new in icd_dict.keys():
            self._result["Response"] = 'True'
            self._result["Name"] = self._icd_value
            self._result["Description"] = icd_dict[self._icd_value_new][1]
            self._result["Mode"] = 'dump'
            self._result['Details'] = {}

    def run_dump(self):
        self.get_gen_icd()
        if not self._error:
            self.get_icd_data()
        if not self._error and self._result.get('Response') == 'False':
            self.get_icd_data_dump()
        return self._result

    def run_api(self):
        new_icd_dict = {}
        if not self._error and self._result.get('Response') == 'False':
            self._result = extractapi(self._icd_value)
            if self._result.get('Response') == 'True':
                new_icd_dict[self._icd_value] = {}
                for key, val in self._result.get('Details').items():
                    if key not in EXCLUDE_FIELDS:
                        if key == 'Description':
                            key = 'desc'
                        new_icd_dict[self._icd_value][key] = val
                with open('icd_dump.json', 'r') as icd_file_read:
                    icd_dict = json.load(icd_file_read)
                icd_dict.update(new_icd_dict)
                with open('icd_dump.json', 'w') as icd_file_write:
                    json.dump(icd_dict, icd_file_write, indent=4)
        return self._result

    @staticmethod
    def export_icd_data():
        icd_dict = {}
        root = tree.getroot()
        names_1 = root.findall('./chapter/section/diag/name')
        for name in names_1:
            icd_dict[name.text] = {}
            for val in name.itersiblings():
                if val.tag == 'diag':
                    continue
                elif val.tag == 'desc':
                    icd_dict[name.text][val.tag] = val.text
                else:
                    icd_dict[name.text][val.tag] = []
                    for elem in val.iterchildren():
                        icd_dict[name.text][val.tag].append(elem.text)
        names_2 = root.findall('./chapter/section/diag/diag/name')
        for name in names_2:
            icd_dict[name.text] = {}
            for val in name.itersiblings():
                if val.tag == 'diag':
                    continue
                elif val.tag == 'desc':
                    icd_dict[name.text][val.tag] = val.text
                else:
                    icd_dict[name.text][val.tag] = []
                    for elem in val.iterchildren():
                        icd_dict[name.text][val.tag].append(elem.text)
        with open('icd_dump.json', 'w') as icd_file:
            json.dump(icd_dict, icd_file, indent=4)
