#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib,urllib2,json
import sys
import os
import requests
import random
import ConfigParser
import logging
import logging.handlers
reload(sys)
sys.setdefaultencoding( "utf-8" )


class WeChat(object):
    __token_id = ''
        # init attribute
        def __init__(self,url):
                self.__url = url.rstrip('/')
#read config
        self.__myconfig=sys.path[0]+"/"+"config.conf"
        with open(self.__myconfig, 'r') as f:
            self.__conf1=ConfigParser.ConfigParser()
            self.__conf1.read(self.__myconfig)
            self.__corpid=self.__conf1.get("weixin_auth","auth_wx_corpid")
            self.__secret=self.__conf1.get("weixin_auth","auth_wx_secret")

        # Get TokenID
        def authID(self):
                params = {'corpid':self.__corpid, 'corpsecret':self.__secret}
                data = urllib.urlencode(params)
                content = self.getToken(data)
                try:
                        self.__token_id = content['access_token']
                        # print content['access_token']
                except KeyError:
                        raise KeyError

        # Establish a connection
        def getToken(self,data,url_prefix='/'):
                url = self.__url + url_prefix + 'gettoken?'
                try:
                        response = urllib2.Request(url + data)
                except KeyError:
                        raise KeyError
                result = urllib2.urlopen(response)
                content = json.loads(result.read())
                return content

        # Get sendmessage url
        def postData(self,data,url_prefix='/'):
                url = self.__url + url_prefix + 'message/send?access_token=%s' % self.__token_id
                request = urllib2.Request(url,data)
                try:
                        result = urllib2.urlopen(request)
                except urllib2.HTTPError as e:
                        if hasattr(e,'reason'):
                                print 'reason',e.reason
                        elif hasattr(e,'code'):
                                print 'code',e.code
                        return 0
                else:
                        content = json.loads(result.read())
                        result.close()
                return content

        # send message
        def sendMessage(self,touser,subject,message):
                self.authID()
                data = json.dumps({
                        'touser':touser,
                        'toparty':"2",
                        'msgtype':"text",
                        'agentid':"1",
                        'text':{
                                'content':subject + '\n' + message
                        },
                        'safe':"0"
                },ensure_ascii=False).encode('UTF-8')
                response = self.postData(data)
                print response
                somefile02 = open(r'/tmp/zabbix_weixin.log','a')
                try:
                  somefile02.write(data+"\n")
                finally:
                  somefile02.close()
#upload temporary image
    def uploadImage(self):
        self.authID()
        img_url='https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image' % self.__token_id
        file_t1='/tmp/zabbix/image'
        file_t1_list=os.listdir(file_t1)
        file_t1_random=random.sample(file_t1_list,1)
        files={'media':open(file_t1+'/'+''.join(file_t1_random),'rb')}
        myr=requests.post(img_url,files=files)
        go=json.loads(myr.content)['media_id']
        return go
#sed single image
    def sendImage_old(self,touser):
        mr=self.uploadImage()
        data = json.dumps({
                        'touser':touser,
                        'toparty':"2",
                        'msgtype':"image",
                        'agentid':"1",
                        'image':{
                                'media_id': mr
                        },
                        'safe':"0"
        })
        response = self.postData(data)
        return response
#send mpnews
    def sendImage(self,touser,subject,message):
        mr=self.uploadImage()
        mymelog=self.mylog()
                data = json.dumps({
                        'touser':touser,
                        'toparty':"2",
                        'msgtype':"mpnews",
                        'agentid':"1",
                        'mpnews':{
                                "articles":[
                {
                    "title": subject,
                    "thumb_media_id": mr,
                    "author": "fan",
                    "content": subject + '\n' + message,
                    "digest": "zabbix touch",
                    "show_cover_pic": "1"    
                        },]
            },
            'safe':"0"
                },ensure_ascii=False).encode('UTF-8')
                response = self.postData(data)
                mymelog.debug(response)

    def mylog(self):
#创建一个logger
        logger = logging.getLogger('mypython_logger')
#Log等级总开关
        logger.setLevel(logging.DEBUG)
#创建一个handler，用于写入日志文件
        logfile='/tmp/my_python.log'
        fh=logging.FileHandler(logfile, mode='a')
# 输出到file的log等级的开关
        fh.setLevel(logging.DEBUG)
#输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
#按天数轮转，保存5份
        rh = logging.handlers.TimedRotatingFileHandler('/tmp/my_python.log',when='D',interval=1,backupCount=5)
        rh.setLevel(logging.DEBUG)
#定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s - %(pathname)s - %(process)d - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        rh.setFormatter(formatter)
#将logger添加到handler里面 
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.addHandler(rh)
        return logger
    

if __name__ == '__main__':
        a = WeChat('https://qyapi.weixin.qq.com/cgi-bin')
#        a.sendMessage(sys.argv[1],sys.argv[2],sys.argv[3])
    a.sendImage(sys.argv[1],sys.argv[2],sys.argv[3])
