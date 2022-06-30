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
        self.mobileno_validation()
        self.zip_validation()
        self.name_validation()
        self.icd_group_validation()
        self.finaljson['fallouts'] = self.fallouts
        del self.finaljson['icd_code_group']
        return self.finaljson

    def mobileno_validation(self):
        column_keys = ['patient_phone', 'ref_to_phone', 'ref_by_phone']
        for key in column_keys:
            if self.finaljson[key] is not None:
                if re.match("^\\+?[1-9][0-9]{8,14}$", str(self.finaljson[key])):
                    logger.info(f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.error = True
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})

    def zip_validation(self):
        column_keys = ['patient_st_zip', 'ref_to_st_zip', 'ref_by_st_zip']
        for key in column_keys:
            if self.finaljson[key] is not None:
                if re.match("^[0-9]{5}(?:-[0-9]{4})?$", str(self.finaljson[key])):
                    logger.info(
                        f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})
                    self.error = True

    def name_validation(self):
        column_keys = ['patient_name', 'ref_to_name', 'ref_by_name']
        for key in column_keys:
            if self.finaljson[key] is not None and len(self.finaljson[key]) > 0:
                if re.match('[\s\w]+$', str(self.finaljson[key])):
                    logger.info(
                        f'{key} validation succesfull', extra={'foo': 'Prime Checks'})
                else:
                    self.error = True
                    self.fallouts.append(f'{key} validation failed ')
                    logger.warning(f'{key} validation failed ', extra={'foo': 'Prime Checks'})

    def icd_group_validation(self):
        if self.finaljson['icd_code_group']:
            logger.warning(f' multiple icd codes matched', extra={'foo': 'Prime Checks'})
            self.error = True
            self.fallouts.append(f'multiple icd codes matched  {self.finaljson["icd_code_group"]}')