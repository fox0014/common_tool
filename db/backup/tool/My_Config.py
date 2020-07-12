#!/usr/bin/python  
# -*- coding:utf-8 -*-

import logging
import logging.config
import ConfigParser
import json

#日志

def config(mytype):
    if mytype == "log":
        def myconfig(file="./config/logging.ini"):
            logging.config.fileConfig(file)
            logger = logging.getLogger()
            #返回logger
            return logger
        return myconfig
    elif mytype == "mysql":
        def myconfig(file="./config/mysql.ini"):
            _config=None
            with open(file, 'r') as configfile:
                conf1=ConfigParser.ConfigParser()
                conf1.readfp(configfile)
                #read ojb
                listse=conf1.sections()
                _config={}
                for se in listse:
                    _config[se]={}
                    op=conf1.options(se)
                    for op1 in op:
                        _config[se][op1]=conf1.get(se,op1)
                return json.dumps(_config,indent=4)
            return _config
        return myconfig
    elif mytype == "backup":
        def myconfig(file="./config/backup.ini"):
            _config=None
            with open(file, 'r') as configfile:
                conf1=ConfigParser.ConfigParser()
                conf1.readfp(configfile)
                 #read ojb
                listse=conf1.sections()
                _config={}
                for se in listse:
                    _config[se]={}
                    op=conf1.options(se)
                    for op1 in op:
                        _config[se][op1]=conf1.get(se,op1)
                return json.dumps(_config,indent=4)
            return _config
        return myconfig
    else:
        return None
