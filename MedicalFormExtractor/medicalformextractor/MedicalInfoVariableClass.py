# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:46:50 2022

@author: DK
"""

class MedicalInfoVariableClass(object):

    def __init__(self):
        
        
        
        
        self._patientName = ""
        self._patientFirstName = None
        self._patientMiddleName = None
        self._patientLastName = None
        self._patientDOB = None
        self._patientMRN = None
        self._patientGender = None
        
        self._patientAddress = None
        self._patientPhone = None
        self._patientCity = None
        self._patientStZip = None
        self._patientState = None
        
        self._refToName = ""
        self._refToDate = None
        self._refToAddress = None
        self._refToCity = None
        self._refToPhone = None
        self._refToFax = None 
        self._refToStZip = None
        self._refToState = None

        self._refByName = ""
        self._refByAddress = None
        self._refByCity = None
        self._refByStZip = None
        self._refByPhone = None
        self._refByFax = None
        self._refByState = None
         
        self._refReason = None
        self._diagnosis = None
        self._icdCode = None 
        self._icdInfo = None
        self._icdDesc = None
        self._speciality = None