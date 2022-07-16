import logging
import re

logging.basicConfig(level=logging.NOTSET, format=' %(levelname)s - %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


class Checkups:
    """ checkups for checks"""

    def __init__(self) -> None:
        self.error = False
        self.finaljson = ''
        self.fallouts = []

    def __str__(self) -> str:
        return 'method for checkups'

    def prime_checks(self, finaljson):

        self.finaljson = finaljson
        self.name_validation()
        self.dob_validation()
        self.mobileno_validation()
        self.zip_validation()
        self.icd_group_validation()
        self.finaljson['fallouts'] = self.fallouts
        del self.finaljson['icd_code_group']
        return self.finaljson

    def mobileno_validation(self):
        column_keys = ['patient_phone', 'ref_to_phone', 'ref_by_phone']
        for key in column_keys:
            if self.finaljson[key] is not None:
                number = ''.join(filter(str.isdigit, str(self.finaljson[key])))
                if number and 8 >= (len(number) <= 12) and re.match('^[\\d ()+-]+$', str(self.finaljson[key])):
                    logger.info(f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.error = True
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})

    def zip_validation(self):
        column_keys = ['patient_st_zip', 'ref_to_st_zip', 'ref_by_st_zip']
        for key in column_keys:
            if self.finaljson[key] is not None:
                if re.match('^[\\d]{5}(?:-[\\d]{0,})?$', str(self.finaljson[key])):
                    logger.info(
                        f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})
                    self.error = True

    def dob_validation(self):
        column_keys = ['patient_dob']
        for key in column_keys:
            if self.finaljson[key] is not None:
                if re.match('^[\\d]{1,2}[/-][\\d]{1,2}[/-](?:\d{4}|\d{2})$', str(self.finaljson[key])):
                    logger.info(
                        f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})
                    self.error = True

    def name_validation(self):
        column_keys = ['ref_to_name', 'ref_by_name']
        for key in column_keys:
            if len(self.finaljson[key].strip()) > 0:
                if re.match("^[a-zA-Z ,.'-]+$", str(self.finaljson[key])):
                    logger.info(
                        f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.error = True
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})
                    
        name_keys = ['patient_first_name','patient_middle_name','patient_last_name']
        for key in name_keys:
            if self.finaljson[key] is not None:
                if re.match("^[a-zA-Z ,.'-]+$", str(self.finaljson[key])):
                    logger.info(
                        f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.error = True
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})
                    
        compulsory_keys = ['patient_name']
        for key in compulsory_keys:
            if len(self.finaljson[key].strip()) > 0:
                if re.match("^[a-zA-Z ,.'-]+$", str(self.finaljson[key])):
                    logger.info(
                        f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.error = True
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})
                    
            if len(self.finaljson[key].strip()) == 0:
                self.error = True
                self.fallouts.append(f'{key} validation failed ')
                logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})
                    

    def icd_group_validation(self):
        if self.finaljson['icd_code_group']:
            try:
                self.finaljson["icd_code_group"] = sorted(
                    self.finaljson["icd_code_group"], key=lambda d : d['Score'] , reverse= True
                )
                for i in self.finaljson["icd_code_group"]:
                    i['Score'] = round(i['Score'] , 2)                   
            except:
                pass
            logger.warning(f' multiple icd codes matched', extra={'foo': 'Prime Checks'})
            self.error = True
            self.fallouts.append(f'multiple icd codes matched  {self.finaljson["icd_code_group"]}')
