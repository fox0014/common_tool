#!/usr/bin/env python
#coding:utf-8
import os,sys
import cPickle as cPicklep
import hashlib
import zipfile
import logging

'''
zip file
'''

class MyFilE_compress(object):
    logger = logging.getLogger(__name__)
    def __init__(self):
        self.md5Dict = {}
        self.fileList =[]
        
    @staticmethod
    def md5filesum(fname):
        m = hashlib.md5()
        with file(fname) as f:
            while True:
                data = f.read(4096)
                if len(data) == 0:
                    break
                m.update(data)
        logging.info(m.hexdigest())
        return m.hexdigest()

    @staticmethod
    def FileBackup(self,srcfile,dstDir,fullName):
        md5Dict = self.md5Dict
        fileList = self.fileList
        srcfile=os.path.join(srcfile)
        with zipfile.ZipFile(r'%s' % os.path.join(dstDir,fullName) ,'w',zipfile.zlib.DEFLATED) as azip:
            azip.write(srcfile)

    def DirBackup(self,srcDir,dstDir,fullName,temdir,md5file):
        md5Dict = self.md5Dict
        fileList = self.fileList
        for dirpath,dirnames,filenames in os.walk(srcDir):
            for filename in filenames:
                fileList.append(os.path.join(dirpath,filename))
        with zipfile.ZipFile(r'%s' % os.path.join(dstDir,fullName) ,'w',zipfile.zlib.DEFLATED) as azip:
            for eachFile in fileList:
                md5Dict[eachFile] = self.md5filesum(eachFile)
                azip.write(eachFile)
        with file(r'%s' % os.path.join(temdir,md5file),'w') as f:
            cPicklep.dump(md5Dict,f)        
            
    def DirincrBackup(self,srcDir,dstDir,incrName,temdir,md5file):
        newmd5 = self.md5Dict
        fileList = self.fileList
        for dirpath,dirnames,filenames in os.walk(srcDir):  
            for filename in filenames:  
                fileList.append(os.path.join(dirpath,filename))
        for eachFile in fileList:
            newmd5[eachFile] = self.md5filesum(eachFile)
        with file(r'%s' % os.path.join(temdir,md5file)) as f:
            storedmd5 = cPicklep.load(f)
        with zipfile.ZipFile(r'%s' % os.path.join(dstDir,incrName) ,'w',zipfile.zlib.DEFLATED) as azip:    
            for eachKey in newmd5:
                if (eachKey not in storedmd5) or (newmd5[eachKey] != storedmd5[eachKey]):
                    azip.write(os.path.join(srcDir,eachKey))
#不继续进行MD5对值，就是差异备份了,否则就是增量备份
        with file(r'%s' % os.path.join(temdir,md5file),'w') as f:
            cPicklep.dump(newmd5,f)
    
  
                 
if __name__ == '__main__':
    jiaoben=os.path.abspath(__file__)
    print(MyFilE_compress.md5filesum(jiaoben))
