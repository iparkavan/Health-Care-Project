# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:32:28 2022

@author: DK
"""
import trp , json

class Extract(object):
    
    def __init__(self, response):
        
        self._response = response 
        
    
    def extractContent(self):
        
        content = self.getContent()
        keyValuePairs = self.getKeyValuePair(self._response)
        tableContents = self.getTableContent(content)
        lineContents = self.getLineContent(content)
        
        return keyValuePairs , tableContents , lineContents
       
        
    def getContent(self):
        content = trp.Document(self._response)
        return content
    
    
    
    def getKeyValuePair(self, content):
        kvs = self.get_kv_map(content)
        #kvs = self.get_kv_relationship(key_map, value_map, block_map)
        return kvs



    def get_kv_map(self, content):
        kvcontent = []
        i = 0
        for page in content:
            key_map = {}
            value_map = {}
            block_map = {}
            blocks = page['Blocks']
            # get key and value maps

            for block in blocks:
                block_id = block['Id']
                block_map[block_id] = block
                if block['BlockType'] == "KEY_VALUE_SET":
                    if 'KEY' in block['EntityTypes']:
                        key_map[block_id] = block
                    else:
                        value_map[block_id] = block
            keyValueContent = self.get_kv_relationship(key_map, value_map, block_map, i)
            kvcontent.extend(keyValueContent)
            i = i + 1
        return kvcontent



    def get_kv_relationship(self,key_map, value_map, block_map, page):
        kvs = []
        for block_id, key_block in key_map.items():
            value_block = self.find_value_block(key_block, value_map)
            key , width , height , top , left = self.get_text(key_block, block_map , "key", page)
            val = self.get_text(value_block, block_map , "value", 0)
            kvs.append([key , val , width , height , top , left])
        return kvs
    
    
    
    def find_value_block(self,key_block, value_map):
        for relationship in key_block['Relationships']:
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = value_map[value_id]
        return value_block
    
    
    
    def getTableContent(self,doc):
        
        pages = len(doc.pages)
        
        index = "table"
        tblcntnt = []
        for page in range(pages):
            tbl = len(doc.pages[page].tables)
            for tb in range(tbl):
                ttt = []
                content = (doc.pages[page].tables[tb])
                for row in content.rows:
                    for cell in row.cells:
                        ttt.append(cell.text)
                width = doc.pages[page].tables[tb].geometry.boundingBox.width.real
                height = doc.pages[page].tables[tb].geometry.boundingBox.height.real
                left = doc.pages[page].tables[tb].geometry.boundingBox.left.real
                top = doc.pages[page].tables[tb].geometry.boundingBox.top.real
                tblcntnt.append([index + '_'  + str(page) + '_' + str(tb),
                                [page + width , page + height , page + top ,  page + left],
                                ttt])
            
        return tblcntnt
    
    def getLineContent(self,content):

        lineContent = []
        pages = len(content.pages)
        
        for page in range(pages):
            
            for line in content.pages[page].lines:
                width = ((line.geometry.boundingBox.width.real))
                height = ((line.geometry.boundingBox.height.real))
                top = ((line.geometry.boundingBox.top.real))
                left = ((line.geometry.boundingBox.left.real))
                width = page + width
                height = page + height
                top = page + top
                left = page + left
                lineContent.append([line.text , [width , height , top , left]])
                
        return lineContent

    def get_text(self, result, blocks_map , extype , page ):
        text = ''
        width = ''
        height = ''
        top = ''
        left = ''
        if 'Relationships' in result:
            for relationship in result['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            text += word['Text'] + ' '
                       
                            width = word['Geometry']['BoundingBox']['Width']
                            height = word['Geometry']['BoundingBox']['Height']
                            top = word['Geometry']['BoundingBox']['Top']
                            left = word['Geometry']['BoundingBox']['Left']
                            
                            width = page + width
                            height = page + height
                            top = page + top
                            left = page + left
                        if word['BlockType'] == 'SELECTION_ELEMENT':
                            if word['SelectionStatus'] == 'SELECTED':
                                text += 'X '
        if extype == "key":
            return text , width , height , top , left
        else :
            return text     
