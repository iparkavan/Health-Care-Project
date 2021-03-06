# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:46:50 2022

@author: DK
"""
import re
import yaml
import json
from dotenv import load_dotenv
import os
load_dotenv()


class ExtractMedicalInfo():

   

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

        

        

        
        
    def extract(self,keyValuePairs, tableContents, lineContents):
        
        self._keyValuePairs = keyValuePairs
        self._tableContents = tableContents
        self._lineContents = lineContents
        self._controlStatement = {}        
        
        self.loadYamlConfig()
              
        self.extractDefaultKeyValuePairs()
        
        self.extractInfoFromTable()
        
        self.extractMissingPatientInfoByLine()
        
        self.extractMissingReferalToInfoByLine()
        
        self.extractMissingReferalByInfoByLine()
        
        self.extractCityZipIcdInfo()
        
        #jsonMessage = self.generateJsonMessage()
        
        if not self._refReason:
            self.extractReferalReasonFromTable()
        
        self.removeLeadingTrailingSpaces()
        

       
        print("-----------------------")
        print("Patient Name :" ,self._patientName ,'\n',
              "FirstName :", self._patientFirstName , '\n',
              "Middle Name : ", self._patientMiddleName , '\n',
              "Last Name : ", self._patientLastName , '\n',
              "Patient DOB :" , self._patientDOB ,'\n',
              "Patient MRN :" ,self._patientMRN ,'\n',
              "Patient Gender :" , self._patientGender ,'\n',
              "Patient Address: " ,self._patientAddress ,'\n',
              "Patient Phone : " ,self._patientPhone ,'\n',
              "Patient City : " ,  self._patientCity ,'\n',
              "Patient State Zip", self._patientStZip , '\n',
              "Patient State", self._patientState , '\n',
              "Rfereal To Name: " , self._refToName, '\n' , 
              "Ref To Date :" , self._refToDate , '\n' , 
              "Ref To Address :" , self._refToAddress , '\n',
              "Ref To City:" , self._refToCity , '\n', 
              "Ref To St Zip" , self._refToStZip , '\n' ,
              "Ref State", self._refToState , '\n',
              "Ref To Phone:" , self._refToPhone , '\n',
              "Ref To Fax", self._refToFax, '\n',
              "Ref By Name" , self._refByName , '\n',
              "Ref By Address" ,  self._refByAddress, '\n',
              "Ref By City" , self._refByCity , '\n',
              "Ref By Zip" , self._refByStZip , '\n',
              "Ref By State", self._refByState , '\n',
              "Ref By Phone" , self._refByPhone, '\n',
              "Ref By Fax" ,  self._refByFax, '\n',
              "Ref reason " , self._refReason, '\n',
              "Diagnosis", self._diagnosis, '\n',
              "icd code" ,  self._icdCode,'\n',
              "icd desc" , self._icdDesc, '\n',
              "icd info" ,  self._icdInfo, '\n',
              "speciality : " , self._speciality)
        
        #return jsonMessage

        
    def extractInfoFromTable(self):
        
        pTop , pHeight , pTableName = self.getPatientInfoTable()
        if pTableName :           
            keyValueContent = self.extractKeyValueFromTable(pTop, pHeight)
            self.extractPatientContentInTable(keyValueContent)
        
        referTop , referHeight , refTableName = self.getReferInfoTable(pTableName)
        if refTableName:
            keyValueContent = self.extractKeyValueFromTable(referTop, referHeight)
            
            self.extractReferalContentInTable(keyValueContent)


    def extractDefaultKeyValuePairs(self):
                
         
        for content in self._keyValuePairs :
            
            if eval(self.generateIfCond(self._controlStatement.get("patientname"),'content[0].lower()' )):
                if content[1] : 
                    if not self._patientName:
                        self._patientName = self._patientName + ' ' + content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("patientdob"),'content[0].lower()' )):
            #if eval(self._controlStatement.get("patientdob")) in content[0].lower():    
                if content[1]:
                    if not self._patientDOB:
                        self._patientDOB = content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("patientmrn"),'content[0].lower()' )):
            #if eval(self._controlStatement.get("patientmrn")) in content[0].lower():
                if content[1]:
                    if not self._patientMRN:
                        self._patientMRN = content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("patientgender"),'content[0].lower()' )):
            #if eval(self._controlStatement.get("patientgender")) in content[0].lower():
                if content[1]:
                    if not self._patientGender :
                        self._patientGender = content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("refertotname"),'content[0].lower()' )):

                if content[1]:
                    if not self._refToName:
                        self._refToName = self._refToName + " " + content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("referreason"),'content[0].lower()' )):
            #if eval(self._controlStatement.get("referreason")) in content[0].lower():
                if content[1]:
                    if not self._refReason:
                        self._refReason = content[1]
                    
            if eval(self.generateIfCond(self._controlStatement.get("diagnosis"),'content[0].lower()' )): 
            #if eval(self._controlStatement.get("diagnosis")) in content[0].lower():
                if content[1]:
                    if not self._diagnosis:
                        self._diagnosis = content[1]
                    else :
                        self._diagnosis = self._diagnosis + '&&&' + content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("refertodate"),'content[0].lower()' )):
            #if eval(self._controlStatement.get("refertodate")) in content[0].lower():
               
                if content[1]:
                    if not self._refToDate:
                        
                        if re.search("\D", content[1]) and (len(content[1].split(' ')) <= 3):
                             
                            self._refToDate = content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("referbyname"),'content[0].lower()' )):     
            #if eval(self._controlStatement.get("referbyname")) in content[0].lower():
                if content[1]:
                    if not self._refByName:
                        self._refByName = self._refByName + " " + content[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("icd"),'content[0].lower()' )):  
            #if eval(self._controlStatement.get("icd")) in content[0].lower():
                if content[1]:
                    content[1] = content[1].strip()
                    if re.search('^[a-zA-Z0-9\.]+$', content[1]):
                        if not self._icdCode:
                            self._icdCode = content[1]
                        else : 
                            self._icdCode = self._icdCode + "&&&" + content[1]

            if eval(self.generateIfCond(self._controlStatement.get("female"),'content[0].lower()' )):
                if "x" in content[1].lower():
                    if not self._patientGender :
                        self._patientGender = "female"
                        
            if eval(self.generateIfCond(self._controlStatement.get("male"),'content[0].lower()' )):
                if "x" in content[1].lower():
                    if not self._patientGender :
                        self._patientGender = "male"
                        
            if eval(self.generateIfCond(self._controlStatement.get("speciality"),'content[0].lower()' )):
            #if eval(self._controlStatement.get("patientgender")) in content[0].lower():
                if content[1]:
                    if not self._speciality :
                        self._speciality = content[1]                       
    
    def getPatientInfoTable(self):
        
        pateintInformationTable = False
        top , height , tableName = None , None , None
        for tableContent in self._tableContents :
            if pateintInformationTable :
                continue 
            
            for content in tableContent[2]:

                if eval(self.generateIfCond(self._controlStatement.get("patient"),'content.lower()' )):
                    
                    width = tableContent[1][0]
                    height = tableContent[1][1]
                    top = tableContent[1][2]
                    left = tableContent[1][3]
                    
                    height = height + top
                    
                    newTop = (round(top,2)) - 0.03
                    
                    for line in self._lineContents : 
                        if round(line[1][2],2) >= newTop:
                            if round(line[1][2],2) <= (round(top,2)) :
                                if eval(self.generateIfCond(self._controlStatement.get("patienttable"),'line[0].lower()' )):                                   
                                      
                                    pateintInformationTable = True
                                    
                                    return top , height , tableContent[0]
        
        return top , height , tableName

    def getReferInfoTable(self,pTableName):

        referalInformationTable = False 
        top , height , tableName = None , None , None

        for tableContent in self._tableContents :
            if pTableName == tableContent[0]:
                continue
            if referalInformationTable:
                continue
            
            for content in tableContent[2]:
                
                if eval(self.generateIfCond(self._controlStatement.get("refer"),'content.lower()' )):
                    
                    width = tableContent[1][0]
                    height = tableContent[1][1]
                    top = tableContent[1][2]
                    left = tableContent[1][3]
                    
                    height = height + top
                    
                    newTop = (round(top,2)) - 0.03
                    
                    for line in self._lineContents : 
                        if round(line[1][2],2) >= newTop:
                            if round(line[1][2],2) <= (round(top,2)) :
                                
                                if eval(self.generateIfCond(self._controlStatement.get("refertable"),'line[0].lower()' )):                                        
                                     
                                    referalInformationTable = True
                                    
                                    return top , height , tableContent[0]
     
        return top , height , tableName 

   
    def extractKeyValueFromTable(self,top , height , left = None ,  width = None):
      
        keyValueContent = []
        
        for kvp in self._keyValuePairs : 
            
            if str(kvp[4]).lstrip().rstrip():                        
                if round(float(kvp[4]),2) >= round((top),2) :                                   
                    if round(float(kvp[4]),2) <= round((height),2):  
                        if left :
                            if round(float(kvp[5]),2) <= round((width),2):  
                                if round(float(kvp[5]),2) >= round((left),2):  
                                    keyValueContent.append(kvp)
                        else :
                            keyValueContent.append(kvp)
        
        if keyValueContent:
            keyValueContent = self._sortKeyValue(keyValueContent)
        
        return keyValueContent
    
    def extractPatientContentInTable(self,patientContent):
        
        
        if not self._patientName:
            fname , mname , lname, name  = '' , '' , '' , ''
            for info in patientContent :
                if "name" in info[0].lower():
                    info[1] = info[1].lstrip().rstrip()
                    if ("first" in info[0].lower()) and ("last" in info[0].lower()) and ("middle" in info[0].lower()) :
                        
                        if "," in info[1]:
                            nm = info[1].split(',')
                        else :
                            nm = info[1].split(' ')
                        
                        self._patientFirstName = nm[0]
                        self._patientLastName = nm[-1]
                        if len(nm) == 3 :
                            self._patientMiddleName = nm[1]
                            
                    elif ("first" in info[0].lower()) and ("last"  in info[0].lower()):
                        if "," in info[1]:
                            nm = info[1].split(',')
                        else :
                            nm = info[1].split(' ')
                        self._patientFirstName = nm[0]
                        self._patientLastName = nm[-1]

                    if "first" in info[0].lower() :
                        fname = info[1]
                        if not self._patientFirstName:
                            self._patientFirstName = info[1]
                    elif "middle" in info[0].lower() :
                        mname = info[1]
                        if not self._patientMiddleName:
                            self._patientMiddleName = info[1]
                    elif "last" in info[0].lower() :
                        if not self._patientLastName:
                            self._patientLastName = info[1]
                        lname = info[1]
                    else :
                        name = info[1]
            if name.lstrip().rstrip():
                self._patientName = name
            elif fname.lstrip().rstrip():
                self._patientName = fname + ' ' + mname + ' ' + lname
 
        
        for info in patientContent :
            if eval(self.generateIfCond(self._controlStatement.get("patientAddressInTable"),'info[0].lower()' )): 
                if not self._patientAddress:
                    self._patientAddress = info[1]
                
            if eval(self.generateIfCond(self._controlStatement.get("patientPhoneInTable"),'info[0].lower()' )):   
                if not self._patientPhone:
                    self._patientPhone = info[1]
                
            if eval(self.generateIfCond(self._controlStatement.get("patientCityAndZipInTable"),'info[0].lower()' )):   
                if ',' in info[1]:
                    city , stzip = info[1].split(',')
                    if not self._patientCity:
                        self._patientCity = city
                    if not self._patientStZip:
                        self._patientStZip = stzip
                else :
                    info[1] = info[1].lstrip().rstrip()
                    if not self._patientCity:
                        self._patientCity = ' '.join(info[1].split(' ')[0:-2])
                    if not self._patientStZip:
                        self._patientStZip = ' '.join(info[1].split(' ')[-2:])
                    
            if eval(self.generateIfCond(self._controlStatement.get("patientCityInTable"),'info[0].lower()' )):   
                if not self._patientCity:
                    self._patientCity = info[1]
                
            if eval(self.generateIfCond(self._controlStatement.get("patientZipInTable"),'info[0].lower()' )):   
                if info[1].lstrip().rstrip(): 
                    if not self._patientStZip:
                        self._patientStZip = info[1]
            
            if eval(self.generateIfCond(self._controlStatement.get("patientStateInTable"),'info[0].lower()' )):     
                if info[1].lstrip().rstrip():
                    if not self._patientState:
                        self._patientState = info[1]
                
    
    def extractReferalContentInTable(self, referalContent):
        
        self.removeLeadingTrailingSpaces()
        
        if not self._refToName:
            for info in referalContent :
                if ("name" in info[0].lower()) or ("to" in info[0].lower()):
                    if self._patientName  != info[1].lstrip().rstrip() :
                        if not  self._refToName:
                            self._refToName = self._refToName + ' ' + info[1]
        
        for info in referalContent :
            if eval(self.generateIfCond(self._controlStatement.get("referToAddressInTable"),'info[0].lower()' )): 
                if self._patientAddress  != info[1].lstrip().rstrip():
                    if not self._refToAddress:
                        self._refToAddress = info[1]
                
            if eval(self.generateIfCond(self._controlStatement.get("referToPhoneInTable"),'info[0].lower()' )):   
                if self._patientPhone  != info[1].lstrip().rstrip():
                    if not self._refToPhone:
                        self._refToPhone = info[1]
                

            if eval(self.generateIfCond(self._controlStatement.get("referToCityAndZipInTable"),'info[0].lower()' )):
                if ',' in info[1]:
                    city , stzip = info[1].split(',')
                    if self._patientCity  != city.lstrip().rstrip():
                        if not self._refToCity:
                            self._refToCity   =  city
                    if self._patientStZip  != stzip.lstrip().rstrip():
                        if not self._refToStZip:
                            self._refToStZip = stzip                    

                else :
                    info[1] = info[1].lstrip().rstrip()
                    stzip = ' '.join(info[1].split(' ')[-2:])
                    city =  ' '.join(info[1].split(' ')[0:-2])
                    if self._patientCity  != city.lstrip().rstrip():
                        if not self._refToCity:
                            self._refToCity   =  city
                    if self._patientStZip  != stzip.lstrip().rstrip():
                        if not self._refToStZip:
                            self._refToStZip = stzip  
                        
                   
            if eval(self.generateIfCond(self._controlStatement.get("referToCityInTable"),'info[0].lower()' )):
                if self._patientCity  != info[1].lstrip().rstrip():
                    if not self._refToCity:
                        self._refToCity   =  city
                
            if eval(self.generateIfCond(self._controlStatement.get("referToZipInTable"),'info[0].lower()' )):
                    if self._patientStZip  != info[1].lstrip().rstrip():
                        if not self._refToStZip:
                            self._refToStZip = stzip 
            
            if eval(self.generateIfCond(self._controlStatement.get("referToStateInTable"),'info[0].lower()' )):   
                if self._patientState != info[1].lstrip().rstrip():
                    if not self._refToState:
                        self._refToState = info[1].lstrip().rstrip()
                
            if eval(self.generateIfCond(self._controlStatement.get("referToDateInTable"),'info[0].lower()' )):
                if not self._refToDate:
                    if re.search("\D", info[1]) and (len(info[1].split(' ')) <= 3):
                             
                        self._refToDate = info[1]
                     
                
            if eval(self.generateIfCond(self._controlStatement.get("referToFaxInTable"),'info[0].lower()' )):
                if not self._refToFax:
                    self._refToFax = info[1]
                
    def extractMissingPatientInfoByLine(self):
        
        self.removeLeadingTrailingSpaces()
        
         
        for line in self._lineContents :
            if eval(self.generateIfCond(self._controlStatement.get("patientInfoInLine"),'line[0].lower()' )):
                height , top , left , width = None , None, None, None
                
                addWidth = self.checkPateintReferInfoInSameLine(current = "patient" , check = "refer")

                height , top , left , width = None , None, None, None
                height = round(line[1][1],2)
                top = round(line[1][2],2) 
                left = round(line[1][3],2)  
                width = round(line[1][0],2)                   
                height = height + top                
                height = height + 0.30
                width = width + left
                width = width + 0.10
                left = left - 0.10
                
                if not addWidth:
                    width = None
                    left = None
                kvContent = self.extractKeyValueFromTable(top , height, left , width)
                 
                if not self._patientName  :
                     
                    fname , mname , lname, name  = '' , '' , '' , ''
                    
                    for info in kvContent :
                         
                        if "name" in info[0].lower():
                            info[1] = info[1].lstrip().rstrip()
                            if ("first" in info[0].lower()) and ("last" in info[0].lower()) and ("middle" in info[0].lower()) :
                                if "," in info[1]:
                                    nm = info[1].split(',')
                                else :
                                    nm = info[1].split(' ')
                                self._patientFirstName = nm[0]
                                self._patientLastName = nm[-1]
                                if len(nm) == 3 :
                                    self._patientMiddleName = nm[1]
                                    
                            elif ("first" in info[0].lower()) and ("last" in info[0].lower()):
                                if "," in info[1]:
                                    nm = info[1].split(',')
                                else :
                                    nm = info[1].split(' ')
                                self._patientFirstName = nm[0]
                                self._patientLastName = nm[-1]
                            
                            if "first" in info[0].lower() :
                                fname = info[1]
                                if not self._patientFirstName:
                                    self._patientFirstName = info[1]
                                continue
                            elif "middle" in info[0].lower() :
                                mname = info[1]
                                if not self._patientMiddleName:
                                    self._patientMiddleName = info[1]
                                continue
                            elif "last" in info[0].lower() :
                                lname = info[1]
                                if not self._patientLastName:
                                    self._patientLastName = info[1]
                                continue
                            else :
                                if info[1].lstrip().rstrip() :
                                     
                                     
                                    name = info[1]
                        if name:
                            if not self._patientName:
                              
                                self._patientName = name
                             
                        elif fname:
                            self._patientName = str(fname) + ' ' + str(mname) + ' ' + str(lname)                            
                         
 

                if not self._patientDOB :
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("patientDOBInLine"),'info[0].lower()' )):
                                if info[1].lstrip().rstrip():
                                    if not self._patientDOB:
                                        self._patientDOB = info[1].lstrip().rstrip()
                                 
                if not self._patientMRN :
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("patientMRNInLine"),'info[0].lower()' )):
                                if info[1].lstrip().rstrip():
                                    if not self._patientMRN:
                                        self._patientMRN = info[1].lstrip().rstrip()
                                 

                if not self._patientGender :
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("patientGenderInLine"),'info[0].lower()' )): 
                                if info[1].lstrip().rstrip():
                                    if not self._patientGender:
                                        self._patientGender = info[1].lstrip().rstrip()
                                 
                
                if not self._patientAddress :
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("patientAddressInLine"),'info[0].lower()' )):
                                        
                                    if not self._patientAddress: 
                                        if info[1].lstrip().rstrip():
                                            self._patientAddress = info[1].lstrip().rstrip()
                                     
                                
                if not self._patientPhone : 
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("patientPhoneInLine"),'info[0].lower()' )):
                                if len(info[1].lstrip().rstrip()) > 4:
                                    self._patientPhone = info[1].lstrip().rstrip()
                                 
                            
                if not self._patientCity :
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("patientCityAndZipInLine"),'info[0].lower()' )):
                                if info[1].lstrip().rstrip():
                                    if ',' in info[1]:
                                        city , stzip = info[1].split(',')
                                        if not self._patientCity:
                                            self._patientCity = city.lstrip().rstrip()
                                        if not self._patientStZip:
                                            self._patientStZip = stzip.lstrip().rstrip()
                                         
                                    else :
                                        info[1] = info[1].lstrip().rstrip()
                                        if not self._patientCity:
                                            self._patientCity =  ' '.join(info[1].split(' ')[0:-2]).lstrip().rstrip()
                                        if not self._patientStZip:
                                            self._patientStZip = ' '.join(info[1].split(' ')[-2:]).lstrip().rstrip()
                                         
                            elif eval(self.generateIfCond(self._controlStatement.get("patientCityInLine"),'info[0].lower()' )):
                                if info[1].lstrip().rstrip():
                                    if not self._patientCity:
                                        self._patientCity = info[1].lstrip().rstrip()
                                     

                if not self._patientStZip :
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("patientZipInLine"),'info[0].lower()' )):
                                if info[1].lstrip().rstrip():
                                    if not  self._patientStZip:
                                        self._patientStZip = info[1].lstrip().rstrip()
                
                if not self._patientState:
                    for info in kvContent :
                        if eval(self.generateIfCond(self._controlStatement.get("patientStateInLine"),'info[0].lower()' )):
                            if not self._patientState:
                                self._patientState = info[1]  
                                
    def extractMissingReferalToInfoByLine(self):                               
         
        self.removeLeadingTrailingSpaces()
                  
        for line in self._lineContents : 
            if eval(self.generateIfCond(self._controlStatement.get("referToInfoInLine"),'line[0].lower()' )):
            #if ("refer" in line[0].lower() ) and  (("information" in line[0].lower()) or "name" in line[0].lower()  or  "physician" in line[0].lower() or  "detail" in line[0].lower()):
                height , top , left , width = None , None, None, None
                addWidth = self.checkPateintReferInfoInSameLine(current = "refer" ,  check = "patient")
                
                height = round(line[1][1],2)
                top = round(line[1][2],2) 
                left = round(line[1][3],2)  
                width = round(line[1][0],2)                   
                height = height + top                
                height = height + 0.20
                width = width + left
                width = width + 0.10
                left = left - 0.10
                
                if not addWidth:
                    width = None
                    left = None
                kvContent = self.extractKeyValueFromTable(top , height, left , width)
                 
                if not self._refToName:

                     for info in kvContent:
                         
                         if eval(self.generateIfCond(self._controlStatement.get("referToNameInLine"),'info[0].lower()' )):
                         #if (("name" in info[0].lower()) or ("physician" in info[0].lower()) or ("referring" in info[0].lower())) :
                             #if (("provider" not in info[0].lower())) :
                            
                            if info[1].lstrip().rstrip() not in  self._patientName :
                                if info[1].lstrip().rstrip():
                                    if not self._refToName:
                                         
                                        self._refToName = info[1]
                                              
                            
                if not self._refToDate:
                        for info in kvContent :
                            
                            if eval(self.generateIfCond(self._controlStatement.get("referToDateInLine"),'info[0].lower()' )):
                            #if ("date " in info[0].lower()) or  (("on " in info[0].lower()) and ("refer" in info[0].lower())):
                                if info[1].lstrip().rstrip():
                                    if info[1] != self._patientDOB :
                                        if not self._refToDate:
                                             
                                            if re.search("\D", info[1]) and (len(info[1].split(' ')) <= 3):
                             
                                                self._refToDate = info[1] 
                                             

                                
                            
                if not self._refToAddress:
                        for info in kvContent :
                            #print(info)
                            if eval(self.generateIfCond(self._controlStatement.get("referToAddressInLine"),'info[0].lower()' )):
                            #if ("address" in info[0].lower()) and ("symptom" not in info[0].lower()):
                                if info[1].lstrip().rstrip():                                 
                                    if info[1].lstrip().rstrip() !=  self._patientAddress:
                                        if not self._refToAddress:
                                            self._refToAddress = info[1]

                                    
                            
                if not self._refToCity:
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("referToCityAndZipInLine"),'info[0].lower()' )):
                            #if ("city" in info[0].lower()) and ("zip" in info[0].lower()) :
                                if info[1].lstrip().rstrip():
                                    if ',' in info[1]:
                                        city , stzip = info[1].split(',')
                                        
                                        if self._patientCity != city.lstrip().rstrip():
                                            if not self._refToCity:
                                                self._refToCity = city
                                        if self._patientStZip  != stzip.lstrip().rstrip():
                                            if not self._refToStZip:
                                                self._refToStZip = stzip
                                         
                                    else :
                                        info[1] = info[1].lstrip().rstrip()
                                        city = ' '.join(info[1].split(' ')[-2:])
                                        stzip = ' '.join(info[1].split(' ')[0:-2])
                                        if self._patientCity  != city.lstrip().rstrip():
                                            if not self._refToStZip:
                                                self._refToStZip   =  city
                                        if self._patientStZip  != stzip.lstrip().rstrip():
                                            if not self._refToStZip:
                                                self._refToStZip = stzip
                            
                            elif eval(self.generateIfCond(self._controlStatement.get("referToCityInLine"),'info[0].lower()' )):
                            #elif  ("city" in info[0].lower())  :
                                if info[1].lstrip().rstrip():
                                    if self._patientCity  != info[1].lstrip().rstrip():
                                        if not self._refToCity:
                                            self._refToCity = info[1]
                                     
                            
                            
                if not self._refToStZip :
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("referToZipInLine"),'info[0].lower()' )):
                            #if ("city" not in info[0].lower()) and ("zip" in info[0].lower()): 
                                if info[1].lstrip().rstrip():
                                    if self._patientStZip != info[1].lstrip().rstrip():
                                        if not self._refToStZip:
                                            self._refToStZip = info[1]

                if not self._refToState:
                    for info in kvContent :
                        if eval(self.generateIfCond(self._controlStatement.get("referToStateInLine"),'info[0].lower()' )):
                        #if "state" in info[0].lower():
                            if not self._refToState:
                                self._refToState = info[1].lstrip().rstrip()


                                
                if not self._refToPhone:                    
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("referToPhoneInLine"),'info[0].lower()' )):
                             if ("phone" in info[0].lower()) or ("mobile" in info[0].lower()) or (("contact" in info[0].lower() and "number" in info[0].lower())): 
                                if len(info[1].lstrip().rstrip()) > 4 :
                                    if self._patientPhone  != info[1].lstrip().rstrip():
                                        if not self._refToPhone:
                                            self._refToPhone = info[1]
                                   
                            
                if not self._refToFax:
                        for info in kvContent :
                            if eval(self.generateIfCond(self._controlStatement.get("referToFaxInLine"),'info[0].lower()' )):
                            #if "fax" in info[0].lower():
                                if info[1].lstrip().rstrip():
                                    if not self._refToFax:
                                        self._refToFax = info[1]
                                 
            if not self._refReason:
                height , top = None , None
                if eval(self.generateIfCond(self._controlStatement.get("referralReason"),'line[0].lower()' )):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.30
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        
                        if eval(self.generateIfCond(self._controlStatement.get("referralReason"),'info[0].lower()' )):
                             
                            if info[1].lstrip().rstrip():
                                if not self._refReason:
                                    self._refReason = info[1]
                               
            
            if not self._diagnosis:
                height , top = None , None
                if eval(self.generateIfCond(self._controlStatement.get("diagnosis"),'line[0].lower()' )):
                  
                    height = round(line[1][1],2)
                    top = round(line[1][2],2)                      
                    height = height + top                
                    height = height + 0.30
                    kvContent = self.extractKeyValueFromTable(top , height)
                    for info in kvContent :
                        if eval(self.generateIfCond(self._controlStatement.get("description"),'info[0].lower()' )):
                            if info[1].lstrip().rstrip():
                                if not self._diagnosis:
                                    self._diagnosis = info[1]
                                else :
                                    self._diagnosis = self._diagnosis + '&&&' + info[1]
                                            
                            
    def extractMissingReferalByInfoByLine(self):                          
        
        self.removeLeadingTrailingSpaces()
        
        for line in self._lineContents :             
           
            height , top = None , None
            if eval(self.generateIfCond(self._controlStatement.get("referByInfoInLine"),'line[0].lower()' )):
            #if (("by" in line[0].lower() ) and  (("refer" in line[0].lower()) or "diagnos" in line[0].lower())) or (("from" in line[0].lower() ) and  (("refer" in line[0].lower()) or "diagnos" in line[0].lower())):
              
                height , top , left , width = None , None, None, None
                addWidth = self.checkPateintReferInfoInSameLine(current = "refer" ,  check = "patient")
                
                height = round(line[1][1],2)
                top = round(line[1][2],2) 
                left = round(line[1][3],2)  
                width = round(line[1][0],2)                   
                height = height + top                
                height = height + 0.20
                width = width + left
                width = width + 0.10
                left = left - 0.10
                
                if not addWidth:
                    width = None
                    left = None
                kvContent = self.extractKeyValueFromTable(top , height, left , width)
                
                 
                for info in kvContent :
                    
                    if not self._refByName:
                        #if ("by" in info[0].lower()) or ("from" in info[0].lower()) or ("name" in info[0].lower()):
                        if eval(self.generateIfCond(self._controlStatement.get("referByNameInLine"),'info[0].lower()' )):  
                            if info[1] != self._patientName :
                                if info[1] != self._refToName:
                                    if info[1].lstrip().rstrip():
                                        if not self._refByName:
                                            self._refByName = info[1]
                        
                    if not self._refByAddress:
                        #if ("address" in info[0].lower()) and ("symptom" not in info[0].lower()):
                        if eval(self.generateIfCond(self._controlStatement.get("referByAddressInLine"),'info[0].lower()' )):    
                            if info[1] != self._patientAddress :
                                if info[1] != self._refToAddress:
                                    if info[1].lstrip().rstrip():
                                        if not self._refByAddress:
                                            self._refByAddress = info[1]

                    if not self._refByCity:
                        #if "city" in info[0].lower() and "zip" in info[0].lower():
                        if eval(self.generateIfCond(self._controlStatement.get("referByCityAndZipInLine"),'info[0].lower()' )): 
                            if info[1] != self._patientCity :
                                if info[1] != self._refToCity:
                                    if info[1].lstrip().rstrip():
                                        if ',' in info[1]:
                                            city , stzip = info[1].split(',')
                                            if not self._refByCity:
                                                self._refByCity = city
                                            if not self._refByStZip:
                                                self._refByStZip = stzip
                                            
                                        else :
                                            info[1] = info[1].lstrip().rstrip()
                                            if not self._refByStZip:
                                                self._refByStZip  = ' '.join(info[1].split(' ')[-2:])
                                            if not self._refByCity:
                                                self._refByCity  = ' '.join(info[1].split(' ')[0:-2])
                        
                        if eval(self.generateIfCond(self._controlStatement.get("referByCityInLine"),'info[0].lower()' )):
                        #if "city" in info[0].lower() and "zip" not in info[0].lower():
                            
                            if info[1] != self._patientCity :
                                if info[1] != self._refToCity:
                                    if not self._refByCity:
                                        self._refByCity = info[1]
                            
                            
                    if not self._refByStZip:
                        if eval(self.generateIfCond(self._controlStatement.get("referByZipInLine"),'info[0].lower()' )):
                        #if "zip" in info[0].lower():
                            if info[1] != self._patientStZip :
                                if info[1] != self._refToStZip:
                                    if not self._refByStZip:
                                        self._refByStZip = info[1]

                    if not self._refByState:
                        if eval(self.generateIfCond(self._controlStatement.get("referByStateInLine"),'info[0].lower()' )):
                        #if "state" in info[0].lower():
                            if not self._refByState:
                                self._refByState = info[1].lstrip().rstrip()


                    if not self._refByPhone:
                        if eval(self.generateIfCond(self._controlStatement.get("referByPhoneInLine"),'info[0].lower()' )):
                        #if "phone" in info[0].lower():
                            if info[1] != self._patientPhone :
                                if info[1] != self._refToPhone:
                                    if len(info[1].lstrip().rstrip()) > 4 :
                                        if not self._refByPhone:
                                            self._refByPhone = info[1]
                        
                                
                    if not self._refByFax:
                        if eval(self.generateIfCond(self._controlStatement.get("referByFaxInLine"),'info[0].lower()' )):
                        #if "fax" in info[0].lower():
                            if info[1] != self._refToFax :
                                if info[1].lstrip().rstrip():
                                    if not self._refByFax:
                                        self._refByFax = info[1]
                                      

    def removeLeadingTrailingSpaces(self) :
        
        if self._patientName :
            self._patientName = self._patientName.lstrip().rstrip()
        if self._patientFirstName:
            self._patientFirstName = self._patientFirstName.lstrip().rstrip()
        if self._patientMiddleName:
            self._patientMiddleName = self._patientMiddleName.lstrip().rstrip()
        if self._patientLastName:
            self._patientLastName = self._patientLastName.lstrip().rstrip()
        if self._patientDOB :
            self._patientDOB = self._patientDOB.lstrip().rstrip()
        if self._patientMRN:
            self._patientMRN = self._patientMRN.lstrip().rstrip()
        if self._patientGender:
            self._patientGender = self._patientGender.lstrip().rstrip()
        if self._patientAddress:
            self._patientAddress = self._patientAddress.lstrip().rstrip()
        if self._patientPhone:
            self._patientPhone = self._patientPhone.lstrip().rstrip()
        if self._patientCity:
            self._patientCity = self._patientCity.lstrip().rstrip()
        if self._patientStZip:
            self._patientStZip = self._patientStZip.lstrip().rstrip()
        if self._refToName:
            self._refToName = self._refToName.lstrip().rstrip()
        if self._refToDate:
            self._refToDate = self._refToDate.lstrip().rstrip()
        if self._refToAddress:
            self._refToAddress = self._refToAddress.lstrip().rstrip()
        if self._refToCity:
            self._refToCity = self._refToCity.lstrip().rstrip()
        if self._refToPhone:
            self._refToPhone = self._refToPhone.lstrip().rstrip()
        if self._refToFax:
            self._refToFax = self._refToFax.lstrip().rstrip()
        if self._refToStZip:
            self._refToStZip = self._refToStZip.lstrip().rstrip()
        if self._refByName:
            self._refByName = self._refByName.lstrip().rstrip()
        if self._refByAddress:
            self._refByAddress  = self._refByAddress.lstrip().rstrip()
        if self._refByCity:
            self._refByCity = self._refByCity.lstrip().rstrip()
        if self._refByStZip:
            self._refByStZip = self._refByStZip.lstrip().rstrip()
        if self._refByPhone:
            self._refByPhone = self._refByPhone.lstrip().rstrip()
        if self._refByFax:
            self._refByFax = self._refByFax.lstrip().rstrip()
        if self._refReason:
            self._refReason = self._refReason.lstrip().rstrip()
        if self._diagnosis:
            self._diagnosis = self._diagnosis.lstrip().rstrip()
        if self._speciality:
            self._speciality = self._speciality.lstrip().rstrip()
         
        if self._patientState:
            self._patientState = self._patientState.lstrip().rstrip()
        if self._refToState:
            self._refToState = self._refToState.lstrip().rstrip()
        if self._refByState:
            self._refByState = self._refByState.lstrip().rstrip()


    def generateJsonMessage(self):
        
            
        jsonMessage = {
            "MedInfoJsonMap": {
                "patient_name": self._patientName,
                "patient_firstname:": self._patientFirstName,
                "patient_middleName:" : self._patientMiddleName ,
                "patient_lastname:" : self._patientLastName,
                "patient_dob": self._patientDOB,
                "patient_mrn": self._patientMRN,
                "patient_gender": self._patientGender,
                "patient_address": self._patientAddress,
                "patient_phone": self._patientPhone,
                "patient_city": self._patientCity,
                "patient_st_zip": self._patientStZip,
                "patient_state": self._patientState,
                "ref_to_name": self._refToName,
                "ref_date": self._refToDate,
                "ref_to_address": self._refToAddress,
                "ref_to_city": self._refToCity,
                "ref_to_st_zip": self._refToStZip,
                "ref_to_state": self._refToState,
                "ref_to_phone": self._refToPhone,
                "ref_to_fax": self._refToFax,
                "ref_by_name": self._refByName,
                "ref_by_address": self._refByAddress,
                "ref_by_city": self._refByCity,
                "ref_by_st_zip": self._refByStZip,
                "ref_by_state": self._refByState,
                "ref_by_phone": self._refByPhone,
                "ref_by_fax": self._refByFax,
                "ref_reason": self._refReason,
                "primary_billing_diagnosis": self._diagnosis
            },
            "ICDInfoJsonMap": {
                "icd_code": self._icdCode,
                "icd_code_list": "_icd_list",
                "icd_description": self._diagnosis,
                "icd_info": self._icdInfo,
                "speciality:": self._speciality
            }
        }           
    
    
        jsonMessage = json.dumps(jsonMessage)

        return jsonMessage    



    def loadYamlConfig(self):

        with open(f"{os.environ.get('CONFIG_FILES', os.curdir)}/config.yml") as file:
            try:
                conf = yaml.safe_load(file)   
                
            except yaml.YAMLError as exc:
                print(exc)
        
        self.getControlStatement(conf)

    def getControlStatement(self,conf):

      
        def generateOrCond(v):
            
            v = v.split('&')
            innercond = ''
            for i in v :
                if not innercond:
                    innercond = '{}'.format(str(i).lstrip().rstrip())
                    continue
                innercond = innercond + ' and ' + '{}'.format(str(i).lstrip().rstrip())
            if innercond :
                
                innercond  = "{}".format(innercond)
            return innercond                   
                                
        for k,v in conf.items():
           
            cond = ''
            if isinstance(v,dict):
                self.getControlStatement(v)
            elif isinstance(v,list):
                
                if len(v) > 1 :
                    for i in v :
                        innercond = ''
                    
                        if '&' in i :
                            innercond = generateOrCond(i)

                        if not cond:
                            if innercond:
                                cond = '{}'.format(str(innercond).lstrip().rstrip())
                            else :
                                cond = '{}'.format(str(i).lstrip().rstrip())
                            
                            continue
                        if innercond:
                            cond = cond + ' or ' + '{}'.format(str(innercond).lstrip().rstrip())
                        else : 
                            cond = cond + ' or ' + '{}'.format(str(i).lstrip().rstrip())
                         
                else : 
                    v = ' '.join(v)
                    if '&' in v :
                        cond = generateOrCond(v)
                            
                    else :
                        cond = '{}'.format(str(v).lstrip().rstrip())
               
            self._controlStatement[k] = cond  

    def generateIfCond(self, argument , condition):
        listString = []
        for i in argument.split(' '):
        
            if i != "and ":
                if i != "or ":
                    j = '"{}"'.format(i)
            if i == "and":
                j = "-and-"
            if i == "or":
                j = "-or-"
            
            listString.append(j)
            
        string = (' '.join(listString))
        
        result = self.generateCondition(string, condition)
        result = result.replace("$", " ")
        return result   

    def generateCondition(self,string, condition) :
        finalstring = ''
        andString = ''
        inClause = " in "
        notinClause = " not in "
        if ("-or-" in string) and ("-and-" in string) :
            c = string.split("-or-")
            for d in c :
                if "-and-" in d :
                    andString = ''
                    e = d.split("-and-")
                    for f in e :
                        
                        if '~' in f:
                            f = f.replace('~', '')
                            clause = notinClause
                        else :
                            clause = inClause
                        if  not andString:
                            andString = andString + "({})".format(' ' + f + ' ' + clause + condition)
                        else :
                            andString = andString + ' and  ' + "({})".format(' ' + f + ' ' + clause + condition)
                    andString = "({})".format(andString)
                    
                    if not finalstring :
                        finalstring = andString
                    else :
                        finalstring = finalstring + ' or ' + andString  
                else :
                    if '~' in d:
                        d = d.replace('~', '')
                        clause = notinClause
                    else :
                        clause = inClause
                    if not finalstring:
                        finalstring = finalstring + "({})".format(' ' + d + ' ' + clause + condition)
        
                    else :
                        finalstring = finalstring + ' or  ' + "({})".format(' ' + d + ' ' + clause + condition)

                
        elif "-and-" in string :
                e = string.split("-and-")
                for f in e :
                        if '~' in f:
                            f = f.replace('~', '')
                            clause = notinClause
                        else :
                            clause = inClause
                        if  not finalstring:
                            finalstring = finalstring + "({})".format(' ' + f + ' ' + clause + condition)
                        else :
                            finalstring = finalstring + ' and  ' + "({})".format(' ' + f + ' ' + clause + condition)
                finalstring = "({})".format(finalstring)
        elif "-or-" in string :
                e = string.split("-or-")
                for f in e :
                        if '~' in f:
                            f = f.replace('~', '')
                            clause = notinClause
                        else :
                            clause = inClause
                        if  not finalstring:
                            finalstring = finalstring + "({})".format(' ' + f + ' ' + clause + condition)
                        else :
                            finalstring = finalstring + ' or  ' + "({})".format(' ' + f + ' ' + clause + condition)
                finalstring = "({})".format(finalstring)
        else :
            if '~' in string:
                string = string.replace('~', '')
                clause = notinClause
            else :
                clause = inClause
            finalstring = string + ' ' + clause  + condition

        finalstring = "({})".format(finalstring)
        return finalstring
    
    def checkPateintReferInfoInSameLine(self, current = None , check = None):
        
        lineCheck = []
        
        
        for line in self._lineContents :
            
            if current == "patient":
                checkcond = self.generateIfCond(self._controlStatement.get("patientInfoInLine"),'line[0].lower()' )
            elif current == "refer":
                checkcond = self.generateIfCond(self._controlStatement.get("referToInfoInLine"),'line[0].lower()' )
            
            if eval(checkcond):
                height = round(line[1][1],3)
                top = round(line[1][2],3) 
                left = round(line[1][3],3)  
                width = round(line[1][0],3)   
                 
                height = height + top 
                width = left + width
                height  = height + 0.01
        
                left = None
                for line in self._lineContents : 
                    
                    if str(line[0]).lstrip().rstrip():                        
                        if round(float(line[1][2]),3) >= top :                                   
                            if round(float(line[1][2]),3) <= height:  
                                if left :
                                    if round(float(line[1][3]),3) <=    width:  
                                        if round(float(line[1][3]),3) >= left:  
                                             
                                            lineCheck.append([line[0] , line[1]])
                                else : 
                                     lineCheck.append([line[0] , line[1]])
          
            
         
        if check == "refer":
            condition = self.generateIfCond(self._controlStatement.get("referToInfoInLine"),'line[0].lower()' )
        elif check == "patient":
            condition = self.generateIfCond(self._controlStatement.get("patientInfoInLine"),'line[0].lower()' )            
        
        if lineCheck:
            for line in lineCheck:
                if eval(condition):
                    
                    return True
        return False


    def _sortKeyValue(self, keyValueContent):
        
        kvpContent = []
        keyValueContent.sort(key = lambda x: x[4])
        for kvp in keyValueContent :
            kvpContent.append([kvp[0] , kvp[1]])
        return kvpContent     
    

    def getIcdInfo(self):
        
        icdInfoList = []
        for content in self._keyValuePairs :  
            
            if eval(self.generateIfCond(self._controlStatement.get("icdInfo"),'content[0].lower()' )):
                icdInfoList.append(content[1])
        
        return ' '.join(icdInfoList)
    
    
    
    def extractCityZipIcdInfo(self):
        
        if not self._diagnosis:
            for content in self._keyValuePairs :
                if eval(self.generateIfCond(self._controlStatement.get("diagnosischecklist"),'content[0].lower()' )):                    
                    if content[1].lower().strip() == "x":
                        if not self._diagnosis:
                           self._diagnosis = content[0]   
                        
        self.removeLeadingTrailingSpaces()

        self._icdDesc = self._diagnosis
        if self._icdCode and self._icdDesc:
            self._icdCode = self._icdCode.split("&&&")
            self._icdDesc = self._icdDesc.split("&&&")
            self._icdInfo = None
        else:
            self._icdInfo = self.getIcdInfo()
            if self._icdCode and not self._icdDesc :
                self._icdCode = self._icdCode.split("&&&")
                self._icdDesc = []
            if self._icdDesc and not self._icdCode :
                self._icdDesc = self._icdDesc.split("&&&")
                self._icdCode = []
        
        if not self._icdCode:
            self._icdCode = []
        if not self._icdDesc:
            self._icdDesc = []
        if not (self._icdCode) :
            self._icdCode = []
            for line in self._lineContents :
                if eval(self.generateIfCond(self._controlStatement.get("icd"),'line[0].lower()' )):  
                    
                    height , top , left , width = None , None, None, None
                    height = round(line[1][1],4)
                    top = round(line[1][2],4)                   
                    height = height + top                
                    height = height + 0.0700
                     
                    lineContent = []
                    
                    for line in self._lineContents :
                        
                        if str(line[1]).lstrip().rstrip():                        
                            if round(float(line[1][2]),4) >= round((top),4) :                                   
                                if round(float(line[1][2]),4) <= round((height),4):  
                                    lineContent.append(line)
                    lineContent.sort(key = lambda x: x[1][2])
                    finalLineContent = []
                    for line in lineContent:
                        finalLineContent.append(line[0])
                    for line in finalLineContent :
                        if "icd" in line.lower():
                            for line in finalLineContent :
                                 
                                
                                if re.search('^[a-zA-Z0-9\.]+$', line) and ('.' in line):
                                    
                                    self._icdCode.append(line)        
                            
            
        if not self._patientState:
            if self._patientStZip  :
                if ((len(self._patientStZip.split(' '))) > 1 ):
                    self._patientState = self._patientStZip.split(' ')[0]
                    self._patientStZip = self._patientStZip.split(' ')[1]
        if not self._refToState:
            if self._refToStZip  :
                if ((len(self._refToStZip.split(' '))) > 1 ):
                    self._refToState = self._refToStZip.split(' ')[0]
                    self._refToStZip = self._refToStZip.split(' ')[1]
        if not self._refByState:
            if self._refByStZip :
                if ((len(self._refByStZip.split(' '))) > 1 ):
                    self._refByState = self._refByStZip.split(' ')[0]
                    self._refByStZip = self._refByStZip.split(' ')[1]
                    

            
        if len(self._icdCode) > len(self._icdDesc):
            diff = len(self._icdCode) - len(self._icdDesc)
            for i in range(diff):
                self._icdDesc.append(None)
        if len(self._icdDesc) > len(self._icdCode):
            diff =  len(self._icdDesc) - len(self._icdCode)
            for i in range(diff):
                self._icdCode.append(None)
        
        
        if not self._speciality :
            header = self._lineContents[0:5]
            #print(header)
            for line in header:


                specialityList = (self._controlStatement.get("specialityInfo")).split("or")
                 
                for speciality in specialityList:
                   
                    if speciality.strip() in line[0].lower().strip():
                        self._speciality = speciality
                        continue
         
        self._diagnosis = self._diagnosis.replace("&" , "")                  
        
    def extractReferalReasonFromTable(self):
        
        referalReasonTable = False
        top , height , tableName = None , None , None
        for tableContent in self._tableContents :
            if referalReasonTable :
                continue 
            
            for content in tableContent[2]:

                if eval(self.generateIfCond(self._controlStatement.get("reasonForReferalTable"),'content.lower()' )):
                    
                    Twidth = tableContent[1][0]
                    Theight = tableContent[1][1]
                    Ttop = tableContent[1][2]
                    Tleft = tableContent[1][3]
                    
                    Twidth = round(Twidth,2)
                    Theight = round(Theight,2)
                    Ttop = round(Ttop,2)
                    Tleft = round(Tleft,2)
                    
                    Theight = Theight + Ttop
                    Twidth = Twidth + Tleft
                            
                    pateintInformationTable = True   
                    
                    #print(tableContent[2])
                    
                    for line in self._lineContents : 
                        
                        
                        if round(line[1][2],2) >=  Ttop:
                            if round(line[1][2],2) <= Theight :
                                if round(line[1][3],2) >= Tleft :
                                    if round(line[1][3],2) <= Twidth:
                                        if eval(self.generateIfCond(self._controlStatement.get("reasonForReferalTable"),'line[0].lower()' )):
                        
                                            Lwidth = line[1][0]
                                            Lheight = line[1][1]
                                            Ltop = line[1][2]
                                            Lleft = line[1][3]
                                            
                                            Lwidth = round(Lwidth,2)
                                            Lheight = round(Lheight,2)
                                            Ltop = round(Ltop,2)
                                            Lleft = round(Lleft,2)
                                            
                                            Lheight = Lheight + Ltop
                                            Lwidth = Lwidth + Lleft
                    
                    refLineFound = False
                    refLineCount = 0
                    if Lheight and Lwidth :
                        for line in self._lineContents : 
                            
                            
                            if round(line[1][2],2) >=  Ltop:
                                if round(line[1][2],2) <= Theight :   
                                    if round(line[1][3],2) >= Lleft :
                                        if round(line[1][3],2) <= Lwidth:
                                            if eval(self.generateIfCond(self._controlStatement.get("reasonForReferalTable"),'line[0].lower()' )):
                                                refLineFound = True
                                            if refLineFound:
                                                refLineCount = refLineCount + 1
                                            if refLineFound and refLineCount == 2:
                                                refLineFound = False
                                                self._refReason = line[0]