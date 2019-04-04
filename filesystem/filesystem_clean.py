#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import sys
import time
import datetime
import logging
import logging.handlers
#python2 ~ python3  ConfigParser change
import ConfigParser as configparser 

logger = logging.getLogger(__name__)
pwd = os.path.abspath(sys.path[0])
pwdconfig = os.sep.join([pwd,'fileclean.conf'])


#日志
def mylog():
#创建一个logger
#Log等级总开关
    logger.setLevel(logging.DEBUG)
#创建一个handler，用于写入日志文件
    logfile='my_python.log'
#输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
#按天数轮转，保存5份
    rh = logging.handlers.TimedRotatingFileHandler(logfile,when='D',interval=1,backupCount=5)
    rh.setLevel(logging.DEBUG)
#定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(pathname)s %(lineno)d - %(process)d - %(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    rh.setFormatter(formatter)
#将logger添加到handler里面 
    logger.addHandler(ch)
    logger.addHandler(rh)
    return logger

def myconfig(file=None):
    with open(file, 'r') as configfile:
        conf=configparser.ConfigParser()
        conf.readfp(configfile)
        return(conf)


#按时间列出文件
def fileshow(DIR1,tttt_xxx1=30,mydir_empty_clean=False):
    ttt_2=time.time()
    ADIR_1={}
#windows下适应中文目录，linux暂时有问题
    DIR1= unicode(DIR1, "utf-8")
    def _chenyixun(t1_file_path,tttt_xxx1):
        ADIR_2={}
        t1_file_big=os.path.getsize(t1_file_path)/1024/1024
        tt_1=os.stat(t1_file_path)
        ttt_3=tt_1.st_mtime
        tttt_x=(ttt_2-ttt_3)/60/60/24
        if ( tttt_x > tttt_xxx1 ):
                ADIR_2=(tttt_x,t1_file_big)
                return ADIR_2           
    for t1_dirs,t1_subdirs,t1_files in os.walk(DIR1):
        if mydir_empty_clean:
            if not os.listdir(t1_dirs):
                if _chenyixun(t1_dirs,tttt_xxx1):
                    ADIR_1[t1_dirs]=_chenyixun(t1_dirs,tttt_xxx1)
        else:
            for t1_file in t1_files:
                t1_file_path=os.path.join(t1_dirs,t1_file)
                if _chenyixun(t1_file_path,tttt_xxx1):
                    ADIR_1[t1_file_path]=_chenyixun(t1_file_path,tttt_xxx1)
    return ADIR_1

#递归,统计整目录文件大小
def GetPathSize(strPath):    
    if not os.path.exists(strPath):    
        return('No such file or directory.');    
    if os.path.isfile(strPath):    
        return os.path.getsize(strPath);    
    nTotalSize = 0;    
    for strRoot, lsDir, lsFiles in os.walk(strPath):    
                        #get child directory size    
        for strDir in lsDir:    
            nTotalSize = nTotalSize + GetPathSize(os.path.join(strRoot, strDir));    
                        #for child file size    
        for strFile in lsFiles:    
            nTotalSize = nTotalSize + os.path.getsize(os.path.join(strRoot, strFile));    
    return (nTotalSize/1024/1024)

#装饰器
def myfile_clear(mydir_empty_clean=True):
    if mydir_empty_clean:
        def _nightwish(func):
            def wrapper(file_t1,fileall_time1=30):
                try:
                    mygo.debug(func(file_t1))
                    fileclean1=fileshow(file_t1,tttt_xxx1=fileall_time1,mydir_empty_clean=True)
                    for key_fileall in fileclean1.keys():
                        os.rmdir(key_fileall)
                        mygo.debug("%s is delete,already empty" % (key_fileall))
                except Exception,e:
                    mygo.error(e)
            return wrapper
    else:
        def _nightwish(func):
            def wrapper(file_t1,fileall_time1=30):
                try:
                    mygo.debug(func(file_t1))
                    fileclean1=fileshow(file_t1,tttt_xxx1=fileall_time1)
                    for key_fileall in fileclean1.keys():
                        os.remove(key_fileall)
                        mygo.debug("%s is delete,size %s M" % (key_fileall,fileclean1[key_fileall][1]))
                except Exception,e:
                    mygo.error(e)
            return wrapper
    return _nightwish

@myfile_clear(mydir_empty_clean=True)
def my_songdongye(strPath,fileall_time1=30):
    nFileSize = GetPathSize(strPath)
    result = re.findall(r'\d+$', str(nFileSize))
    if result:   
        return('{yy1} is {xx1}m'.format(xx1=nFileSize,yy1=strPath))
    else:
        return('{yy1} {xx1}'.format(xx1=nFileSize,yy1=strPath))
    
@myfile_clear(mydir_empty_clean=False)
def my_friday(strPath,fileall_time1=30):
    nFileSize = GetPathSize(strPath)
    result = re.findall(r'\d+$', str(nFileSize))
    if result:   
        return('{yy1} is {xx1}m'.format(xx1=nFileSize,yy1=strPath))
    else:
        return('{yy1} {xx1}'.format(xx1=nFileSize,yy1=strPath))

if __name__ == '__main__':
#暂时不支持中文，windows调用需要加\\
#确保调用一次日志模块
    mygo=mylog()
    conf = myconfig(pwdconfig)
    for section in my_confsecions:
        my_clean_day=conf.get(section,'clean_time')
        #删除过期文件
        clean_dir = conf.get(section,'clean_dir')
        my_friday(clean_dir,int(my_clean_day))
        #按时间删除空目录    
        # my_songdongye('/evcharge/logs',my_clean_day)

