import json
from dotenv import load_dotenv
from data_ingestion.data_ingest import get_dump_record, insert_dump_record, get_dump_record_all
import os
load_dotenv()

from entities_analysis.xml_parse import ICD
from entities_analysis.icd_analyzer import ICDMatcher
from entities_analysis.icd_transform import ICDTransform
from entities_analysis.medcomp import get_icd_medcomp, check_medcomp

data_folder = f"{os.environ.get('CONFIG_FILES', os.curdir)}"
class MedTransformation:

    def __init__(self):
        self. medInfoJson = {}
        self._icd_code = None
        self._icd_desc = None
        self._icd_info = None
        self._icd_list = []
        self._icd_code_list = []
        self._icd_code_group = []
        self._icd_desc_list = []

    def remove_duplicates(self):
        icd_names = []
        new_icd_list = []
        if self._icd_code_group:
            for val in self._icd_code_group:
                if val.get('Code'):
                    if val['Code'] in icd_names:
                        continue
                    else:
                        icd_names.append(val['Code'])
                        new_icd_list.append(val)
        return new_icd_list

    def mapMedInfo(self, extractInfo):
        self._icd_code_group = self.remove_duplicates()
        self._icd_code_list = [code for code in self._icd_code_list if code is not None]
        self._icd_desc_list = [desc for desc in self._icd_desc_list if desc is not None]

        with open(f"{data_folder}/MedInfoMapping.json", 'r') as jf:
            med_load_data = json.load(jf)
        med_json_map = med_load_data["MedInfoJsonMap"]
        for key, value in med_json_map.items():
            self.medInfoJson[key] = getattr(extractInfo, value)
        icd_json_map = med_load_data["ICDInfoJsonMap"]
        for key, value in icd_json_map.items():
            self.medInfoJson[key] = getattr(self, value)

        try:
            all_icd_data = get_dump_record_all()
            all_icd_keys = [key[0] for key in all_icd_data]
            for i in range(len(self._icd_code_list)):
                if self._icd_code_list[i]:
                    if self._icd_code_list[i] not in all_icd_keys and self._icd_desc_list[i]:
                        insert_dump_record(
                            {
                                    "Code": self._icd_code_list[i],
                                    "Description": self._icd_desc_list[i]
                            }
                        )
            for i in range(len(self._icd_code_group)):
                if self._icd_code_group[i]:
                    val = self._icd_code_group[i]
                    if val['Code'] not in all_icd_keys:
                        insert_dump_record(
                            {
                                    "Code": val['Code'],
                                    "Description": val['Description']
                            }
                        )
        except Exception:
            pass
        return self.medInfoJson
    
    def extract_icd(self, parsed_icd_code):
        icdObj = ICD(parsed_icd_code)
        icdResponse = icdObj.run_dump()
        if icdResponse.get('Response') == 'False':
            icdResponse = icdObj.run_api()
        if icdResponse.get('Response') == 'True':
            self._icd_code = icdResponse.get('Code')
            self._icd_desc = icdResponse.get('Description')
            self._icd_list = None
        if icdResponse.get('Response') == 'False' and icdObj._logger[0] == 'Invalid ICD code':
            icdObj2 = ICDTransform(parsed_icd_code)
            icdResponse2 = icdObj2.tranform_gen_icd()
            if icdResponse2 and icdResponse2.get('Response') == 'True' and len(icdResponse2.get('_icd_value_list')) == 1:
                self._icd_code = icdResponse2.get('Code')
                self._icd_desc = icdResponse2.get('Description')
                self._icd_list = None
            elif icdResponse2 and icdResponse2.get('Response') == 'True' and len(icdResponse2.get('_icd_value_list')) > 1:
                self._icd_code = None
                self._icd_desc = None
                self._icd_list = icdResponse2.get('_icd_value_list')
                         
    def run(self, extractInfo):
        
        parsed_icd_code = extractInfo._icdCode
        parsed_icd_desc = extractInfo._icdDesc
        self._icd_info = extractInfo._icdInfo

        for i in range(len(parsed_icd_code)):
            self._icd_code = None
            self._icd_desc = None
            self._icd_list = []
            if not parsed_icd_desc[i] and parsed_icd_code[i]:          
                # ICD Code is given/invalid and No ICD desc
                self.extract_icd(parsed_icd_code[i])
                
            if parsed_icd_desc[i] and not parsed_icd_code[i]:
                # ICD Desc is given and No ICD Code - Match >= 40%
                icd_key, icd_value, icd_key_list = None, None, []
                myobj = ICDMatcher(parsed_icd_desc[i])
                icd_key, icd_value, icd_key_list = get_icd_medcomp(parsed_icd_desc[i])
                if not icd_key and not icd_key_list:
                    # ICD Desc is given and No ICD Code - Match >= 70%
                    icd_key, icd_value, icd_key_list = myobj.get_icd_data_fuzz()
                self._icd_code = icd_key
                self._icd_desc = icd_value
                self._icd_list = icd_key_list

            if parsed_icd_desc[i] and parsed_icd_code[i]:
                # ICD Code is given and ICD desc is given
                # Verify fetch desc on medcomp api - match >= 40%
                # Else fetch ICD Code based on desc on dump - match >= 70%
                icd_key, icd_value, icd_key_list = None, None, []
                icd_key, icd_value, icd_key_list = get_icd_medcomp(parsed_icd_desc[i])
                icd_key, icd_value, icd_key_list = check_medcomp(icd_key_list, parsed_icd_code[i])
                if not icd_key and not icd_key_list:
                    myobj = ICDMatcher(parsed_icd_desc[i])
                    icd_key, icd_value, icd_key_list = myobj.get_icd_data_fuzz()
                    icd_key, icd_value, icd_key_list = myobj.check_datadump(icd_key_list, parsed_icd_code[i])
                if icd_key or icd_key_list:
                    self._icd_code = icd_key
                    self._icd_desc = icd_value
                    self._icd_list = icd_key_list
                if not icd_key and not icd_key_list:
                    self.extract_icd(parsed_icd_code[i])

            self._icd_code_list.append(self._icd_code)
            self._icd_desc_list.append(self._icd_desc)
            if self._icd_list:
                self._icd_code_group.extend(self._icd_list)

        if not any(parsed_icd_desc) and not any(parsed_icd_code):
            # NO ICD Code is given and ICD No desc is given
            # Fetch ICD Code based on data from extract - match >= 40%
            icd_key, icd_value, icd_key_list = get_icd_medcomp(self._icd_info)
            if not icd_key_list:
                myobj = ICDMatcher(self._icd_info)
                icd_key, icd_value, icd_key_list = myobj.get_icd_data_fuzz()
            self._icd_code_list = [icd_key]
            self._icd_desc_list = [icd_value]
            if icd_key_list:
                self._icd_code_group = icd_key_list
