from entities_analysis.icd_request import extractapi
from data_ingestion.data_ingest import get_dump_record, insert_dump_record
from dotenv import load_dotenv
import os
import re
load_dotenv()
EXCLUDE_FIELDS = ['Name', 'Valid', 'Response']

data_folder = f"{os.environ.get('CONFIG_FILES', os.curdir)}"
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
        if '.' in self._icd_value and len(self._icd_value.split('.')[0]) > 3:
            self._error = True
            self._logger.append("Invalid ICD code")
            return
        if not re.match('^[a-zA-z]{1}[0-9]{2}(\.)?(?(1)([0-9]{1,3}|[0-9]{1,3}[a-zA-Z]{1,}))$' , self._icd_value):
            self._error = True
            self._logger.append("Invalid ICD code")
            return

    def get_icd_data(self):
        result = get_dump_record(self._icd_value)
        if result:
            self._result["Response"] = 'True'
            self._result["Code"] = self._icd_value
            self._result["Description"] = result
            self._result["Mode"] = 'dump'
            if len(self._icd_value) > 3 and '.' not in self._icd_value:
                self._result["Code"] = self._icd_value[:3] + "." + self._icd_value[3:]

    def run_dump(self):
        self.get_gen_icd()
        if not self._error:
            self.get_icd_data()
        return self._result

    def run_api(self):
        if not self._error and self._result.get('Response') == 'False':
            self._result = extractapi(self._icd_value)
            if self._result.get('Response') == 'True':
                self._result = insert_dump_record(self._result)
        return self._result
