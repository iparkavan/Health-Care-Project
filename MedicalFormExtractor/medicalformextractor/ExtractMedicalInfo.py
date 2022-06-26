# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:46:50 2022

@author: DK
"""

from pprint import pprint

class ExtractMedicalInfo(object):

    def __init__(self, keyValuePairs , tableContents , lineContents):
        
        self._keyValuePairs = keyValuePairs
        self._tableContents = tableContents
        self._lineContents = lineContents
        
        self._patientName = ""
        self._patientDOB = None
        self._patientMRN = None
        self._patientGender = None
        
        self._patientAddress = None
        self._patientPhone = None
        self._patientCity = None
        
        self._refToName = ""
        self._refToDate = None
        self._refToAddress = None
        self._refToCity = None
        self._refToPhone = None
        self._refToFax = None 

        self._refByName = ""
        self._refByAddress = None
        self._refByCity = None
        self._refByPhone = None
        self._refByFax = None
         
        self._refReason = None
        self._diagnosis = None
        
        self._icd_code = None
        self._icd_desc = None
        self._icd_info = None
    
    def get_extracted_record(self):
        return {
            "Patient Name": self._patientName,
            "Patient DOB": self._patientDOB,
            "Patient MRN": self._patientMRN,
            "Patient Gender": self._patientGender,
            "Patient Address": self._patientAddress,
            "Patient Phone": self._patientPhone,
            "Patient City": self._patientCity,
            "Ref To Name": self._refToName,
            "Ref To Date": self._refToDate,
            "Ref To Address": self._refToAddress,
            "Ref To City": self._refToCity,
            "Ref To Phone": self._refToPhone,
            "Ref By Name": self._refByName,
            "Ref By Address": self._refByAddress,
            "Ref By City": self._refByCity,
            "Ref By Phone": self._refByPhone,
            "Ref By Fax": self._refByFax,
            "Ref reason": self._refReason,
            "Diagnosis": self._diagnosis,
        }
        
    def extract(self):
        
        self.extractDefaultKeyValuePairs()
        
        self.extractInfoFromTable()
        
        self.extractMissingInfoByLine()


    def extractInfoFromTable(self):
        
        pTop , pHeight , pTableName = self.getPatientInfoTable()
        if pTableName :           
            keyValueContent = self.extractKeyValueFromTable(pTop, pHeight)
            self.extractOtherPatientContent(keyValueContent)
        
        referTop , referHeight , refTableName = self.getReferInfoTable(pTableName)
        if refTableName:
            keyValueContent = self.extractKeyValueFromTable(referTop, referHeight)
            self.extractOtherReferalContent(keyValueContent)


    def extractDefaultKeyValuePairs(self):

        for content in self._keyValuePairs :
            if "patient" in content[0].lower() :
                if "name" in content[0].lower():
                    self._patientName = self._patientName + ' ' + content[1]
                   
            if ("dob" in content[0].lower()) or ("birth" in content[0].lower()) :    
                self._patientDOB = content[1]
                
            if "mrn" in content[0].lower():
                self._patientMRN = content[1]
               
            if ("gender" in content[0].lower()) or ("sex" in content[0].lower()):
                
                self._patientGender = content[1]

            if "refer" in content[0].lower() :
                if ("name" in content[0].lower()) or ("to" in content[0].lower()):
                    self._refToName = self._refToName + "" + content[1]
            
            if ("refer" in content[0].lower()) and ("reason" in content[0].lower()):
                self._refReason = content[1]
             
            if ("diagnosis" in content[0].lower()):
                self._diagnosis = content[1]
    
    def getPatientInfoTable(self):
        
        pateintInformationTable = False
        top , height , tableName = None , None , None
        for tableContent in self._tableContents :
            if pateintInformationTable :
                continue 
            
            for content in tableContent[2]:
                
                if "patient" in content.lower():
                    
                    width = tableContent[1][0]
                    height = tableContent[1][1]
                    top = tableContent[1][2]
                    left = tableContent[1][3]
                    
                    height = height + top
                    
                    newTop = (round(top,2)) - 0.03
                    
                    for line in self._lineContents : 
                        if round(line[1][2],2) >= newTop:
                            if round(line[1][2],2) <= (round(top,2)) :
                                if ("information" in line[0].lower()) or (("patient") in line[0].lower() ):                                       
                                    print(line[0])    
                                    pateintInformationTable = True
                                    
                                    return top , height , tableContent[0]
        
        return top , height , tableName
    
    def extractKeyValueFromTable(self,top , height):
        
        keyValueContent = []
        
        for kvp in self._keyValuePairs :                               
            if round((kvp[4]),2) >= round((top),2) :                                   
                if round(kvp[4],2) <= round((height),2):                   
                    keyValueContent.append([kvp[0] , kvp[1]])
        
        return keyValueContent
    
    def extractOtherPatientContent(self,patientContent):
        
        if not self._patientName:
            for info in patientContent :
                if "name" in info[0].lower():
                    self._patientName = self._patientName + ' ' + info[1]
        
        for info in patientContent :
            if "address" in info[0].lower():
                self._patientAddress = info[1]
            if ("phone" in info[0].lower()) or ("mobile" in info[0].lower()):
                self._patientPhone = info[1]
            if ("city" in info[0].lower()) or ("zip" in info[0].lower()):
                self._patientCity = info[1]
                
    def getReferInfoTable(self,pTableName):

        referalInformationTable = False 
        top , height , tableName = None , None , None

        for tableContent in self._tableContents :
            if pTableName == tableContent[0]:
                continue
            if referalInformationTable:
                continue
            
            for content in tableContent[2]:
                
                if "refer" in content.lower():
                    
                    width = tableContent[1][0]
                    height = tableContent[1][1]
                    top = tableContent[1][2]
                    left = tableContent[1][3]
                    
                    height = height + top
                    
                    newTop = (round(top,2)) - 0.03
                    
                    for line in self._lineContents : 
                        if round(line[1][2],2) >= newTop:
                            if round(line[1][2],2) <= (round(top,2)) :
                                if ("information" in line[0].lower()) or (("refer") in line[0].lower() ):                                       
                                    print(line[0])    
                                    referalInformationTable = True
                                    
                                    return top , height , tableContent[0]
     
        return top , height , tableName 
    
    def extractOtherReferalContent(self, referalContent):

        if not self._refToName:
            for info in referalContent :
                if ("name" in info[0].lower()) or ("to" in info[0].lower()):
                    self._patientName = self._refToName + ' ' + info[1]
        
        for info in referalContent :
            if "address" in info[0].lower():
                self._refToAddress = info[1]
            if ("phone" in info[0].lower()) or ("mobile" in info[0].lower()):
                self._refToPhone = info[1]
            if ("city" in info[0].lower()) or ("zip" in info[0].lower()):
                self._refToCity = info[1]
            if ("date" in info[0].lower()) or (" on" in info[0].lower()):
                self._refToDate = info[1]
            if ("fax" in info[0].lower()):
                self._refToFax = info[1]
                
    def extractMissingInfoByLine(self):
        
        
        
        for line in self._lineContents :
            
            if not self._patientName :
                height , top = None , None
                if ("patient" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if "name" in info[0].lower():
                            self._patientName = info[1]
                            break

            if not self._patientDOB :
                height , top = None , None
                if ("patient" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if ("dob" in info[0].lower()) or ("birth" in info[0].lower()) : 
                            self._patientDOB = info[1]
                            break

            if not self._patientMRN :
                height , top = None , None
                if ("patient" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if ("mrn" in info[0].lower()) : 
                            self._patientMRN = info[1]
                            break

            if not self._patientGender :
                height , top = None , None
                if ("patient" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if ("gender" in info[0].lower()) or ("sex" in info[0].lower()) : 
                            self._patientGender = info[1]
                            break

            if not self._patientAddress :
                height , top = None , None
                if ("patient" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if ("address" in info[0].lower()): 
                            self._patientAddress = info[1]
                            break
                            
            if not self._patientPhone :
                height , top = None , None
                if ("patient" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if ("phone" in info[0].lower()): 
                            self._patientPhone = info[1]
                            break
                            
            if not self._patientCity :
                height , top = None , None
                if ("patient" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if ("city" in info[0].lower()): 
                            self._patientCity = info[1]
                            break

            if not self._refToName:
                height , top = None , None
                if ("refer" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()  or  "physician" in line[0].lower()):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                 
                    for info in kvContent :
                        if ("name" in info[0].lower()) or ("physician" in info[0].lower()) or ("referring" in info[0].lower()):
                      
                            if info[1] != self._patientName :
                                
                                self._refToName = info[1]
                                break
                                
            if not self._refToDate:
                height , top = None , None
             
                if ("refer" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if ("date" in info[0].lower()) or  (("on" in info[0].lower()) and ("refer" in info[0].lower())):
                            if info[1] != self._patientDOB :
                                self._refToDate = info[1]
                                break
                            
                            
            if not self._refToAddress:
                height , top = None , None
                if ("refer" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if "address" in info[0].lower():
                            self._refToAddress = info[1]
                            break
                            
            if not self._refToCity:
                height , top = None , None
                if ("refer" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if "city" in info[0].lower():
                            self._refToCity = info[1]
                            break

            if not self._refToPhone:
                height , top = None , None
                if ("refer" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if "phone" in info[0].lower():
                            self._refToPhone = info[1]
                            break
                            
            if not self._refToFax:
                height , top = None , None
                if ("refer" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if "fax" in info[0].lower():
                            self._refToFax = info[1]
                            break
                        
            
            if not self._refByName:
                height , top = None , None
                if ("by" in line[0].lower() ) and  (("refer" in line[0].lower()) or "diagnos" in line[0].lower()):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        
                        if not self._refByName:
                            if "by" in info[0].lower():
                                if info[1] != self._patientName :
                                    if info[1] != self._refToName:
                                        self._refByName = info[1]
                        
                        if not self._refByAddress:
                            if "address" in info[0].lower():
                                if info[1] != self._patientAddress :
                                    if info[1] != self._refToAddress:
                                        self._refByAddress = info[1]

                        if not self._refByCity:
                            if "city" in info[0].lower():
                                if info[1] != self._patientCity :
                                    if info[1] != self._refToCity:
                                        self._refByCity = info[1]

                        if not self._refByPhone:
                            if "phone" in info[0].lower():
                                if info[1] != self._patientPhone :
                                    if info[1] != self._refToPhone:
                                        self._refByPhone = info[1]
                            
                                    
                        if not self._refByFax:
                            if "fax" in info[0].lower():
                                if info[1] != self._refToFax :
                                        self._refByFax = info[1]
                                          

            if not self._refReason:
                height , top = None , None
                if ("reason" in line[0].lower() ) :
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if "reason" in info[0].lower():
                            self._refReason = info[1]
                            break      
            
            if not self._diagnosis:
                height , top = None , None
                if ("diagnosis" in line[0].lower() ) :
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.50
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if "description" in info[0].lower():
                            self._diagnosis = info[1]
                            break 
                
                    
                
                    