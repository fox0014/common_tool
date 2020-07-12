#!/usr/bin/python  
# -*- coding:utf-8 -*-

import os,json

class cdm(object):
    def __init__(self,Path):
        self.__Path=Path
    def FileEX(self,Path=None):
        if not Path:
            Path=self.__Path
        _file1={
            "path":None,
            "type":None
           }
        if os.path.exists(Path):
            _filedir=_file1
            if os.path.isdir(Path):
                if os.access(Path,os.R_OK):
                    _filedir['path'], _filedir['type']='dir','wr'
                else:
                    _filedir['path'],_filedir['type']='dir','reject'
                return json.dumps(_filedir)
            elif os.path.isfile(Path):
                if os.access(Path,os.R_OK):
                    _filedir['path'], _filedir['type']='file','wr'
                else:
                    _filedir['path'],_filedir['type']='dir','reject'
                return json.dumps(_filedir)
            else:
                return json.dumps(_file1)
        else:
            return json.dumps(_file1)
    def FileCreate(self,Path=None):
        if not Path:
            Path=self.__Path
        _file1=json.loads(self.FileEX(Path))
        if _file1['path'] == None and  _file1['type'] == None :
            return os.makedirs(Path)
