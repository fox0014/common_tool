#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import time
import datetime
import logging
import logging.handlers

#日志
logger = logging.getLogger(__name__)

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
                    logger.debug(func(file_t1))
                    fileclean1=fileshow(file_t1,tttt_xxx1=fileall_time1,mydir_empty_clean=True)
                    for key_fileall in fileclean1.keys():
                        os.rmdir(key_fileall)
                        logger.debug("%s is delete,already empty" % (key_fileall))
                except Exception,e:
                    logger.error(e)
            return wrapper
    else:
        def _nightwish(func):
            def wrapper(file_t1,fileall_time1=30):
                try:
                    logger.debug(func(file_t1))
                    fileclean1=fileshow(file_t1,tttt_xxx1=fileall_time1)
                    for key_fileall in fileclean1.keys():
                        os.remove(key_fileall)
                        logger.debug("%s is delete,size %s M" % (key_fileall,fileclean1[key_fileall][1]))
                except Exception,e:
                    logger.error(e)
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
    my_clean_day=2
#删除过期文件
    my_friday('/tmp/logs',my_clean_day)
#按时间删除空目录    
    my_songdongye('/evcharge/logs',my_clean_day)
