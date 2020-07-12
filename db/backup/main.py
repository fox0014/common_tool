#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ConfigParser,sys,os,subprocess
import tool.My_Config as My_Config
import tool.My_File,tool.fileclean,tool.My_Compress
import logging
import json,time

reload(sys)
sys.setdefaultencoding('utf-8')

#pwd dir
pwddir=os.path.dirname(sys.argv[0])

#log config
logger = logging.getLogger(__name__)
logger=My_Config.config("log")
logger=logger(file=os.path.join(pwddir+"/config"+"/logging.ini"))

#mysql config
mysql=My_Config.config("mysql")
mysqlAconfig=os.path.join(pwddir+"/config"+"/mysql.ini")
mysqlAinfo=json.loads(mysql(mysqlAconfig))

#backup config
backupA=My_Config.config("backup")
backupAconfig=os.path.join(pwddir+"/config"+"/backup.ini")
backupAinfo=json.loads(backupA(backupAconfig))
backfile1=backupAinfo['backup']['dir']
backtimeformat=backupAinfo['backup']['timeformat']

#file sure
now = time.strftime(backtimeformat)
nowfile=os.path.join(backfile1,now)
filelog1=os.path.join(pwddir+"/logs")
iswhat=tool.My_File.cdm(filelog1)
iswhat1=tool.My_File.cdm(nowfile)
iswhat.FileCreate()
iswhat1.FileCreate()

def dbbackup():
#mysqlbackup info
    for info1 in mysqlAinfo:
        t1=mysqlAinfo[info1]
#watch dblist
        dblist=t1['dblist'].split(' ')
        for dbt1 in dblist:
#cmd
            sql1="mysqldump -h {0} -u{2} -p{3} {4}> {1}/{0}-{4}.sql".format(t1['host'],nowfile,t1['auth_user'],t1['auth_pass'],dbt1)
            try:
                p = subprocess.Popen(sql1, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                p.wait()
                result_lines = p.stdout.readlines()
                logger.info("%s %s is done,result : %s" % (t1['host'],dbt1,result_lines))
            except Exception as e:
                logger.error("%s %s is done,result : %s" % (t1['host'],dbt1,e))

def main():
    logger.info("begin")
    dbbackup()
    my_clean_day=2
    tool.fileclean.my_friday('/tmp/logs',my_clean_day)

if __name__=='__main__':
    main()
    tool.My_Compress.MyFilE_compress.md5filesum('/etc/passwd')
