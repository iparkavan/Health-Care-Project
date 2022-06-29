import json

from entities_analysis.xml_parse import ICD
from entities_analysis.icd_analyzer import ICDMatcher
from entities_analysis.icd_transform import ICDTransform
from entities_analysis.medcomp import get_icd_medcomp, check_medcomp


class MedTransformation:

    def __init__(self):
        self. medInfoJson = {}
        self._icd_code = None
        self._icd_desc = None
        self._icd_info = None
        self._icd_list = []

    def mapMedInfo(self, extractInfo):
        with open('MedInfoMapping.json', 'r') as jf:
            med_load_data = json.load(jf)
        med_json_map = med_load_data["MedInfoJsonMap"]
        for key, value in med_json_map.items():
            self.medInfoJson[key] = getattr(extractInfo, value)
        icd_json_map = med_load_data["ICDInfoJsonMap"]
        for key, value in icd_json_map.items():
            if key == 'icd_code_list' and value:
                self.medInfoJson[key] = json.dumps(getattr(self, value))
                continue
            self.medInfoJson[key] = getattr(self, value)
            
        try:
            with open('icd_dump.json', 'r') as icd_file_read:
                icd_dict = json.load(icd_file_read)  
            new_icd_dict = {}
            if self._icd_code:
                if self._icd_code not in icd_dict.keys() and self._icd_desc:
                    new_icd_dict = {
                        self._icd_code : {
                            "desc" : self._icd_desc
                        }
                    }
                    icd_dict.update(new_icd_dict)
                    with open('icd_dump.json', 'w') as icd_file_write:
                        json.dump(icd_dict, icd_file_write, indent=4)       
            elif self._icd_list:
                for val in self._icd_list:
                    if val['Code'] not in icd_dict.keys():
                        new_icd_dict = {
                            val['Code'] : {
                                "desc" : val['Description']
                            }
                        }
                        icd_dict.update(new_icd_dict)
                with open('icd_dump.json', 'w') as icd_file_write:
                    json.dump(icd_dict, icd_file_write, indent=4)
        except Exception:
            pass
        
        return self.medInfoJson

    def run(self, extractInfo):

        parsed_icd_code = extractInfo._icdCode
        parsed_icd_desc = extractInfo._icdDesc
        self._icd_info = extractInfo._icdInfo


        if not parsed_icd_desc and parsed_icd_code:
            # ICD Code is given/invalid and No ICD desc
            icdObj = ICD(parsed_icd_code)
            icdResponse = icdObj.run_dump()
            if icdResponse.get('Response') == 'False':
                icdResponse = icdObj.run_api()
            if icdResponse.get('Response') == 'True':
                self._icd_code = icdResponse.get('Name')
                self._icd_desc = icdResponse.get('Description')
                self._icd_list = None
            if icdResponse.get('Response') == 'False' and icdObj._logger[0] == 'Invalid ICD code':
                icdObj2 = ICDTransform(parsed_icd_code)
                icdResponse2 = icdObj2.tranform_gen_icd()
                if icdResponse2 and icdResponse2.get('Response') == 'True' and len(icdResponse2.get('_icd_value_list')) == 1:
                    self._icd_code = icdResponse2.get('Name')
                    self._icd_desc = icdResponse2.get('Description')
                    self._icd_list = None
                elif icdResponse2 and icdResponse2.get('Response') == 'True' and len(icdResponse2.get('_icd_value_list')) > 1:
                    self._icd_code = None
                    self._icd_desc = None
                    self._icd_list = icdResponse2.get('_icd_value_list')

        if parsed_icd_desc and not parsed_icd_code:
            # ICD Desc is given and No ICD Code - Match >= 60%
            icd_key, icd_value, icd_key_list = None, None, []
            myobj = ICDMatcher(parsed_icd_desc)
            icd_key, icd_value, icd_key_list = get_icd_medcomp(parsed_icd_desc)
            if not icd_key and not icd_key_list:
                # ICD Desc is given and No ICD Code - Match >= 80%
                icd_key, icd_value, icd_key_list = myobj.get_icd_data_fuzz()
            self._icd_code = icd_key
            self._icd_desc = icd_value
            self._icd_list = icd_key_list

        if parsed_icd_desc and parsed_icd_code:
            # ICD Code is given and ICD desc is given
            # Verify fetch desc on medcomp api - match >= 60%
            # Else fetch ICD Code based on desc on dump - match >= 80%
            icd_key, icd_value, icd_key_list = None, None, []
            icd_key, icd_value, icd_key_list = get_icd_medcomp(parsed_icd_desc)
            icd_key, icd_value, icd_key_list = check_medcomp(icd_key_list, parsed_icd_code)
            if not icd_key and not icd_key_list:
                myobj = ICDMatcher(parsed_icd_desc)
                icd_key, icd_value, icd_key_list = myobj.get_icd_data_fuzz()
                icd_key, icd_value, icd_key_list = myobj.check_datadump(icd_key_list, parsed_icd_code)
            if icd_key or icd_key_list:
                self._icd_code = icd_key
                self._icd_desc = icd_value
                self._icd_list = icd_key_list

        if not parsed_icd_desc and not parsed_icd_code:
            # NO ICD Code is given and ICD No desc is given
            # Fetch ICD Code based on data from extract - match >= 65%
            icd_key, icd_value, icd_key_list = get_icd_medcomp(self._icd_info)
            self._icd_code = icd_key
            self._icd_desc = icd_value
            self._icd_list = icd_key_list
