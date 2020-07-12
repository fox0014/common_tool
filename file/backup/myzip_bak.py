#!/usr/bin/env python
#coding:utf-8
import random, threading, time
import Queue
import time
import os,sys
import cPickle as cPicklep
import hashlib
import zipfile,ConfigParser

'''
备份666666
'''

my_config_file=''

def md5sum(fname):
    m = hashlib.md5()
    m.update(fname)
    return m.hexdigest()

def md5filesum(fname):
    m = hashlib.md5()
    with file(fname) as f:
        while True:
            data = f.read(4096)
            if len(data) == 0:
                break
            m.update(data)
    return m.hexdigest()

#进度条
def view_bar(num=1, sum=100, bar_word=":"):  
    rate = float(num) / float(sum)  
    rate_num = int(rate * 100)  
    print '\r%d%% :' %(rate_num), 
    for i in range(0, num):  
        os.write(1, bar_word)  
    sys.stdout.flush()  

#返回配置信息    
def my_config(file):
    config = ConfigParser.ConfigParser()
    config.read(file)
    return config
    
#增量or全量  
def incrfull(srcDir,dstDir,fullName,temdir,md5file,full=0):
    if full == 0:
        a=MyFilE_compress()
        a.fullBackup(srcDir,dstDir,fullName,temdir,md5file)
    else:
        a=MyFilE_compress()
        a.incrBackup(srcDir,dstDir,fullName,temdir,md5file)

#判断配置文件部分内容，调用信息
def judgecore(my_config,now,mychose):
    if my_config.has_option(mychose,'temDir'):
        temdir = my_config.get(mychose,'temDir')
    else:
        temdir = my_config.get('global_backup','defaulttemDir')
    if my_config.has_option(mychose,'fullName'):
        fullName = my_config.get(mychose,'fullName')
    else:
        fullName = my_config.get('global_backup','defaultfullName')
    if my_config.has_option(mychose,'dstDir'):
        dstDir = my_config.get(mychose,'dstDir')               
    else:
        dstDir = my_config.get('global_backup','defaultdstDir')  
    md5file = md5sum(mychose)
    srcDir= my_config.get(mychose,'srcDir')
    fullName = "full_%s_%s.zip" % (fullName, now)
    incrName = "incr_%s_%s.zip" % (fullName, now)
    incrfull(srcDir,dstDir,fullName,temdir,md5file,full=0)

#生产    
class producer(threading.Thread):
    def __init__(self,t_name,queue):
        threading.Thread.__init__(self,name=t_name)
        self.data = queue
        self.my_config=my_config(my_config_file)
        self.now = time.strftime('%Y%m%d%H%M')
    def run(self):
        pro_list=self.my_config.sections()
        random.shuffle(pro_list)
        for con1 in pro_list:
            if con1 != "global_backup":
                condata=cPicklep.dumps(con1)
                datacon={condata:self.my_config}
                self.data.put(datacon,5)
        print "生产线程完成！！"
        
#消费   
class consumer(threading.Thread):
    def __init__(self,t_name,queue):
        threading.Thread.__init__(self,name=t_name)
        self.data = queue
        self.now = time.strftime('%Y%m%d%H%M')    
    def run(self):
        while True:
            try:
                tmp_num = self.data.get(1,5) #定义超时时间5秒
                keys1=tmp_num.keys()            
                __my_config=tmp_num[keys1[0]]
                condata=cPicklep.loads(keys1[0])
                judgecore(__my_config,self.now,condata)
                print "\r\n",self.getName(),condata,"finish！！"
            except:
                print "\r\n",self.getName(),"消费线程完成！！" #一旦到达超时时间5秒，会抛异常，break退出循环
                break

class MyFilE_compress(object):
    def __init__(self):
        self.md5Dict = {}
        self.fileList =[]
    def fullBackup(self,srcDir,dstDir,fullName,temdir,md5file):
        md5Dict = self.md5Dict
        fileList = self.fileList
        for dirpath,dirnames,filenames in os.walk(srcDir):  
            for filename in filenames:  
                fileList.append(os.path.join(dirpath,filename))
        os.chdir(r'%s' % dstDir)        
        azip = zipfile.ZipFile(r'%s' % os.path.join(dstDir,fullName) ,'w',zipfile.zlib.DEFLATED) 
        for eachFile in fileList:
            md5Dict[eachFile] = md5filesum(eachFile)
            azip.write(eachFile)     
        with file(r'%s' % os.path.join(temdir,md5file),'w') as f:
            cPicklep.dump(md5Dict,f)        
        azip.close()           
    def incrBackup(self,srcDir,dstDir,incrName,temdir,md5file):
        newmd5 = self.md5Dict
        fileList = self.fileList
        for dirpath,dirnames,filenames in os.walk(srcDir):  
            for filename in filenames:  
                fileList.append(os.path.join(dirpath,filename))
        for eachFile in fileList:
            newmd5[eachFile] = md5filesum(eachFile)
        with file(r'%s' % os.path.join(temdir,md5file)) as f:
            storedmd5 = cPicklep.load(f)
        azip = zipfile.ZipFile(r'%s' % os.path.join(dstDir,incrName) ,'w',zipfile.zlib.DEFLATED)
        os.chdir(r'%s' % dstDir)
        for eachKey in newmd5:
            if (eachKey not in storedmd5) or (newmd5[eachKey] != storedmd5[eachKey]):
                azip.write(os.path.join(srcDir,eachKey))
        azip.close()
#不继续进行MD5对值，就是差异备份了,否则就是增量备份
        with file(r'%s' % os.path.join(temdir,md5file),'w') as f:
            cPicklep.dump(newmd5,f)
      
def Mythreading():
    queue = Queue.Queue()
    threads = []
    consumerList = ['Con1','Con2']
    producerlist= ['Pro']
    view_bar_n=0
    for proName in producerlist:
        thread = producer(proName, queue)
        thread.start()
        threads.append(thread)        
    for conName in consumerList:
        thread = consumer(conName, queue)
        thread.start()
        threads.append(thread)
    for t in threads:
        view_bar_n=view_bar_n+1 
        t.join()
        view_bar(view_bar_n,len(threads)) 
    print 'All threads complete!!!'
 

if __name__ == '__main__':
    my_config_file = "/evcharge/down/jiaoben/config/backup.conf"
    Mythreading()

