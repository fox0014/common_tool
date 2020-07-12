#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import cookielib
import smtplib  
import ConfigParser
import sys
import os
import re
import glob
import threading
import MySQLdb 
import MySQLdb.cursors
import datetime
import random
import shutil
import base64
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

myconfig=sys.path[0]+"/"+"config.conf"
with open(myconfig, 'r') as f:
    conf1=ConfigParser.ConfigParser()
    conf1.read(myconfig)
    mail_host=conf1.get("smtp_auth","auth_config_host")  #设置服务器
    mail_port=conf1.get("smtp_auth","auth_config_port")
    mail_user=conf1.get("smtp_auth","auth_config_user")    #用户名
    mail_pass=conf1.get("smtp_auth","auth_config_pass")   #口令
    mail_postfix=conf1.get("smtp_auth","auth_config_postfix")  #发件箱的后缀
    zabbix_user=conf1.get("zabbix_auth","auth_config_user")    #用户名
    zabbix_pass=conf1.get("zabbix_auth","auth_config_pass")   #口令
    me="<"+mail_user+">"
    mysql_zabbix_host=conf1.get("mysql_zabbix_auth","auth_config_host")  #设置服务器
    mysql_zabbix_port=conf1.get("mysql_zabbix_auth","auth_config_port")
    mysql_zabbix_user=conf1.get("mysql_zabbix_auth","auth_config_user")    #用户名
    mysql_zabbix_pass=conf1.get("mysql_zabbix_auth","auth_config_pass")   #口令
    mysql_zabbix_db=conf1.get("mysql_zabbix_auth","auth_config_db")   #zabbix db name


class Mypy_mail(object):
  def __init__(self):
      self.mail_host=conf1.get("smtp_auth","auth_config_host")  #设置服务器
      self.mail_port=conf1.get("smtp_auth","auth_config_port")
      self.mail_user=conf1.get("smtp_auth","auth_config_user")    #用户名
      self.mail_pass=conf1.get("smtp_auth","auth_config_pass")   #口令
      self.mail_postfix=conf1.get("smtp_auth","auth_config_postfix")  #发件箱的后缀
      self.zabbix_user=conf1.get("zabbix_auth","auth_config_user")    #用户名
      self.zabbix_pass=conf1.get("zabbix_auth","auth_config_pass")   #口令
      self.me="<"+self.mail_user+">"

  def multiple_targle_list(self,to_list,mass_config=''):
#读取群发配置
    To_list=[]
    if mass_config == '':
      To_list=[to_list]
    else:
      with open(sys.path[0]+"/"+mass_config,'r') as f3:
        for line1 in f3:
          To_list.append(line1.split('\n')[0])
    return To_list
  
  def mail_msg_build(self,to_list,sub,content):
    mail_configure = {}
    mail_configure['mail_encoding'] = 'utf-8'
    msg = MIMEMultipart('alternative')
#HTML和Plain格式以降级方法同时支持，默认html优先
    msg.attach(MIMEText(content,_subtype='plain',_charset='utf-8'))
    msg['Subject'] =  '=?%s?B?%s?=' % (mail_configure['mail_encoding'],base64.b64encode(sub))
    msg['From'] = self.me
    msg['To'] = ','.join(to_list)
#这里的msg相当于发给MTA的文本
    with open(sys.path[0]+"/"+'my_mail.py', 'r') as f1:
    # 设置附件的MIME和文件名，这里是普通文件类型:
      att01 = MIMEText(open(sys.path[0]+"/"+'my_mail.py', 'rb').read(), 'base64', 'utf-8')
    # 加上必要的头信息:
      att01.add_header('Content-Disposition', 'attachment', filename='python.txt')
      att01.add_header('Content-ID', '<0>')
      att01.add_header('X-Attachment-Id', '0')
    # 添加到MIMEMultipart:
      msg.attach(att01)
#匹配文件夹下的图片
    up_im_dir='/tmp/zabbix/image'
    up_im_list=glob.glob(up_im_dir+'/*.png')
    n=0 
    for wei_image in up_im_list:
#确定文件是否存在
      with open(wei_image, 'rb') as fn:
#增加到MIME上面
#让变量名改变
        exec('att0%s = MIMEImage(fn.read())' % n)
    # 加上必要的头信息:
        exec("att0%s.add_header('Content-Disposition', 'attachment', filename='titi%s.png')" %(n,n))
        exec("att0%s.add_header('Content-ID', '<titi%s>')" % (n,n))
        exec("att0%s.add_header('X-Attachment-Id', '0')" % n)
    # 添加到MIMEMultipart:
        exec("msg.attach(att0%d)" % n)
        n+=1
    html_t1 = """\
      <html>
        <head>今年加油干</head>
        <body>
          <p>兄弟们!<br>
           你们好啊<br>
           %s<br>
           点击进入 <a href=" http://www.mykuaiji.com ">hello world</a>
           <br><img src="cid:titi0"></br>
           <br><img src="cid:titi1"></br>
           <br><img src="cid:titi2"></br>
           <br><img src="cid:titi3"></br>
          </p>
        </body>
      </html>
      """ % (content)
#html格式插入
    msg.attach(MIMEText(html_t1,_subtype='html',_charset='utf-8'))
    return msg
    
  def send_mail(self,to_list,sub,content):
    try:
      msg=content 
      server = smtplib.SMTP_SSL(host=self.mail_host,port=self.mail_port,timeout=30)
# debug on
#     server.set_debuglevel(1)
      server.ehlo("cool_server")
      server.login(self.mail_user,self.mail_pass)  
      server.sendmail(self.me, to_list, msg.as_string())  
      server.close()  
      return True  
    except Exception, e:  
      print str(e)  
      return False

  def filter_go(self,filter_s1):
#匹配过滤邮件内容
    if filter_s1:
      if len(filter_s1)>30:
        pipi2=re.compile(r'Trigger host')
        s_B1=filter_s1.split('Trigger ip')[0].split('Trigger host')[1].split(':')[1].split('\r\n')[0]
        return s_B1
      else:
        return filter_s1
    try:
      somefile02 = open(r'/tmp/zabbix_test.log','a')
      somefile02.write(s_B1)
    finally:
      somefile02.close()

  def send_mail_main(self,to_list,sub,content,mass_config=''):
    To_u=self.multiple_targle_list(to_list,mass_config='')
    mail_msg_result=self.mail_msg_build(To_u,sub,content) 
    mail_result=self.send_mail(To_u,sub,mail_msg_result)
    return mail_result

class Zabbix_graph(Mypy_mail):
  def __init__(self,url,cookiefile):
    self.zabbix_http=url
    self.zabbix_cookiefile=cookiefile
    Mypy_mail.__init__(self)
  def zabbix_Cookie_new(self):
     #声明一个CookieJar对象实例来保存cookie
    #cookie = cookielib.CookieJar()
    cookie = cookielib.MozillaCookieJar(self.zabbix_cookiefile)
     #利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    values={"name":self.zabbix_user,"password":self.zabbix_pass,"autologin":1,"enter":'Sign in'}
     #格式化成a=1&b=2这样的字符串
    data=urllib.urlencode(values)
     #将data参数传到Request对象
    request=urllib2.Request(self.zabbix_http,data)
     #进行请求
    response=opener.open(request,timeout=10)
    cookie.save(ignore_discard=True, ignore_expires=True)
    return opener
  def zabbix_Cookie_old(self):
     #声明一个CookieJar对象实例来保存cookie
    #cookie = cookielib.CookieJar()
    cookie = cookielib.MozillaCookieJar(self.zabbix_cookiefile)
    cookie.load(self.zabbix_cookiefile, ignore_discard=True, ignore_expires=True)
     #利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    values={"name":self.zabbix_user,"password":self.zabbix_pass,"autologin":1,"enter":'Sign in'}
     #格式化成a=1&b=2这样的字符串
    data=urllib.urlencode(values)
     #将data参数传到Request对象
    request=urllib2.Request(self.zabbix_http,data)
     #进行请求
    response=opener.open(request,timeout=10)
    return opener
  def zabbix_iamge(self,graphid):
#毫秒
    Tt_1=datetime.datetime.now().microsecond
#随机1~20
    Tt_2=random.randint(1,20)
    Tt_x=Tt_1+Tt_2   
    image_dir='/tmp/zabbix/image'
    values_t1={"graphid":graphid,"period":3600,"width":1772}
    data_t1=urllib.urlencode(values_t1)
    request_imag=urllib2.Request(self.zabbix_http+'chart2.php',data_t1)
    #以保存下来的cookie，使用组装的image的连接去访问zabbix，先以持久化的cookie优化
    try:
        opener=self.zabbix_Cookie_old()
        response_imag=opener.open(request_imag,timeout=10)
    except Exception, e:
        opener=self.zabbix_Cookie_new()
        response_imag=opener.open(request_imag,timeout=10)
    finally:
        pass
    #读取返回信息
    the_message=response_imag.read()
    imagename="%s/%s_%s.png"%(image_dir,"Server_go",Tt_x)
#生成随机数+毫秒的图片名称
    with open(imagename,"w") as f:
        f.write(the_message)

class my_Mysql(object):
  def __init__(self,host1,user1,password1,db1,port1):
    self.conn=MySQLdb.connect(host=host1, user=user1, passwd=password1, db=db1,port=port1, charset='utf8',cursorclass=MySQLdb.cursors.DictCursor);  
    self.cur=self.conn.cursor();  
    
  def exeUpdate(self,sql):                #更新或插入操作  
    sta=self.cur.execute(sql);  
    self.conn.commit();  
    return (sta);  
  
  def exeDelete(self,IDs):                #删除操作  
    sta=0;  
    for eachID in IDs.split(' '):  
        sta+=self.cur.execute("delete from students where Id=%d"%(int(eachID)));  
    self.conn.commit();  
    return (sta);  
          
  def exeQuery(self,sql):                      #查找操作  
    cur=self.cur
    cur.execute(sql);
    data=cur.fetchall()
    return (data);  
      
  def __del__(self):                    #关闭连接，释放资源  
    self.cur.close(); 
    self.conn.close();


if __name__ == '__main__':
  if len(sys.argv) < 4:
    print "USE DEFAULT"
    print "argv format should be:  you want to send email, title, content, mass mail but no must input"
    print "you just input %s" %(len(sys.argv))
    print """
    for example:
    python xxxx.py 'huangyf@ev-link.com.cn' '2017Hello 新年好!' 'hello world 新年好!!'
    """
    exit(1)

  #清理文件夹下的图片
  shutil.rmtree('/tmp/zabbix/image')
  os.mkdir('/tmp/zabbix/image')

  Gogo=Mypy_mail()
  if len(sys.argv) == 4:
    Down_ip=Gogo.filter_go(sys.argv[3])
    Today_zabbix=Zabbix_graph('http://10.62.11.53/zabbix/','/tmp/zabbix/cookie/10621153zabbix')
    Today_mysql=my_Mysql(mysql_zabbix_host,mysql_zabbix_user,mysql_zabbix_pass,mysql_zabbix_db,int(mysql_zabbix_port))
    Amysql_go=Today_mysql.exeQuery(("select c.graphid from hosts a LEFT JOIN items b on a.hostid=b.hostid left join graphs_items c on b.itemid=c.itemid where a.host='%s' and c.graphid is not null and b.key_ in ('vfs.fs.size[/,free]','net.if.in[eth0]','system.cpu.util[,idle]','vm.memory.size[available]') group by graphid ") % (Down_ip))
#多线程开启，多线程去下载目标图片
    threads = []
    for Amysql_go1 in Amysql_go:
      Amysql_go2=Amysql_go1['graphid']
      thread_t1=threading.Thread(target=Today_zabbix.zabbix_iamge,args=(Amysql_go2,))
      threads.append(thread_t1)
    for thr_tt in threads:
      thr_tt.start()
    for thr_tt in threads:
      thr_tt.join()
    if Gogo.send_mail_main(sys.argv[1],sys.argv[2],sys.argv[3]):
      print "%s 发送成功 argv3" % (sys.argv[0]) 
    else:
      print "%s 发送失败 argv3" % (sys.argv[0])
  else:
    if Gogo.send_mail_main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]):
      print "%s 发送成功 argv4" % (sys.argv[0])
    else:
      print "%s 发送失败 argv4" % (sys.argv[0])
