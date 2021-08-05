#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################
#
# This python script is used for mysql database backup
# using mysqldump and tar utility.
#
# Written by : fanfanfan
# Created date: 2021/08/03
# Last modified: 2021/08/03
# Tested with : Python 2.7.5 & Python 3.6.8
# Script Revision: 0.1
#
##########################################################

# Import required python libraries

import subprocess
import os
import sys
import datetime
import string
import errno
import getopt
import tempfile
import json
import logging
import logging.handlers
import threading
import time



logger = logging.getLogger(__name__)
#Log等级总开关
logger.setLevel(logging.DEBUG)
#创建一个handler，用于写入日志文件
logfile = 'mysql_backup.log'
#输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
#按天数轮转，保存5份
rh = logging.handlers.TimedRotatingFileHandler(logfile,when='D',interval=1,backupCount=5)
rh.setLevel(logging.DEBUG)
#定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(pathname)s - %(process)d - %(levelname)s: %(message)s")
ch.setFormatter(formatter)
rh.setFormatter(formatter)
#将logger添加到handler里面
logger.addHandler(ch)
logger.addHandler(rh)

skip = ["information_schema", "performance_schema", "test", 'sys']
version = 0.1


class MysqlBackup(object):

    def __init__(self, keep=90, databases=None, store=None, user="root",
                 password=None, host=None):
        self.host = host
        self.keep = keep
        self.databases = databases
        self.store = store
        self.user = user
        self.password = password
        self.host = host
        self.before_backup_hock_list = []
        self.after_backup_hock_list = []

    def run_command(self, command=None, shell=False, ignore_errors=False,
                    ignore_codes=None, get_output=False, path="."):
        p = os_cmd(command)
        code, result, err = p['code'], p['messages'], p['error']

        if code and not ignore_errors and (not ignore_codes or code in set(ignore_codes)):
            logger.error(str(command) + " " + str(code) + str(err))
            raise BaseException(str(command) + " " + str(code) + str(err))
        if not code and not ignore_errors and err:
            logger.error(str(command) + " " + str(err))
            raise BaseException(str(command) + " " + str(err))
        return result

    def get_databases(self):
        list_cmd = "mysql"

        if self.databases:
            return [s.strip() for s in self.databases.strip().split(",")]
        if self.user:
            list_cmd += " -u " + self.user
        if self.host:
            list_cmd += " -h " + self.host
        if self.password:
            list_cmd += " -p" + self.password

        list_cmd += " --silent -N -e 'show databases'"
        databases = self.run_command(list_cmd)
        return [s.strip() for s in databases]

    def cleanup(self):
        # remove files older than keep days
        cut_date = datetime.datetime.now() - datetime.timedelta(days=self.keep)
        try:
            for backup_file in os.listdir(self.store):
                bparts = backup_file.split(".")
                if bparts[0].isdigit():
                    dumpdate = datetime.datetime.strptime(bparts[0], "%Y%m%d%H%M%S")
                    if dumpdate < cut_date:
                        logger.info("Reomve db, %s %s." % (self.store, backup_file))
                        os.remove(os.path.join(self.store, backup_file))
        except Exception as msg:
            logger.error(msg)

    def backup(self):
        # get the current date and timestamp and the zero backup name
        self.cleanup()
        stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dbs = self.get_databases()
        for db in dbs:
            if db in skip:
                continue
            backup_name = '.'.join([stamp, db, "sql"])
            backup_path = self.store + os.sep + backup_name
            dump_cmd = "mysqldump --single-transaction -u " + self.user
            if self.host:
                dump_cmd += " -h " + "'" + self.host + "'"
            if self.password:
                dump_cmd += " -p" + self.password
            dump_cmd += " -e --opt -c " + db + " | gzip > " + backup_path + ".gz"
            logger.debug("Backup Cmd: %s" % dump_cmd)
            self.before_backup_hock(db, backup_path, sync=False)
            self.run_command(dump_cmd)
            self.after_backup_hock(db, backup_path)

    def register_method_hook(self, hock_list, method):
        """
        register hock_list
        Args:
            hock_list: list
            method: function
        Returns:
        """
        hock_list.append(method)

    @staticmethod
    def print_backup_info(message):
        logger.info(message)

    def before_backup_hock(self, db, backup_path, sync=True):
        _result = []
        _thread_list = []
        message = "Begin dump db, %s to %s.gz" % (db, backup_path)
        t = MyThread(target=self.print_backup_info, kwargs=({'message': message}))
        _thread_list.append(t)
        t.start()
        for t in _thread_list:
            if sync:
                t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果
            _result.append(t.get_result())
        return _result

    def after_backup_hock(self, db, backup_path, sync=True):
        _result = []
        _thread_list = []
        message = "Finish dump db, %s to %s.gz" % (db, backup_path)
        t = MyThread(target=self.print_backup_info, kwargs=({'message': message}))
        _thread_list.append(t)
        t.start()
        for t in _thread_list:
            if sync:
                t.join()  # 一定要join，不然主线程比子线程跑的快，会拿不到结果
            _result.append(t.get_result())
        return _result


class MyThread(threading.Thread):

    def __init__(self, target, args=(), kwargs={}):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args
        self.kwargs = kwargs
        self.result = ''

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception as msg:
            return msg


def os_cmd(cmd):
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         bufsize=0
                         )
    _messages = []
    _errors = []
    _code = ''
    for line in iter(p.stdout.readline, 'b'):
        if line:
            try:
                _result = line.decode('gbk').strip('\r\n')
                _messages.append(_result)
                print(line)  # 处理GBK编码的输出，去掉结尾换行
            except Exception:
                _result = line.decode('utf-8').strip('\r\n')
                _messages.append(_result)
                print(line)  # 如果GBK解码失败再尝试UTF-8解码
        if not (subprocess.Popen.poll(p) is None):
            if not line:
                _code = subprocess.Popen.poll(p)
                break

    for line in iter(p.stderr.readline, 'b'):
        if line:
            try:
                _result = line.decode('gbk').strip('\r\n')
                _errors.append(_result)
                print(line)  # 处理GBK编码的输出，去掉结尾换行
            except Exception:
                _result = line.decode('utf-8').strip('\r\n')
                _errors.append(_result)
                print(line)  # 如果GBK解码失败再尝试UTF-8解码
        if not (subprocess.Popen.poll(p) is None):
        #    if line == "":
            if not line:
                _code = subprocess.Popen.poll(p)
                break

    p.stdout.close()
    return {'code': _code, 'messages': _messages, 'error': _errors}


"""
Prints out the usage for the command line.
"""


def usage():
    usage = ["mysqlbackup.py [-hkdbups]\n"]
    usage.append("  [-h | --help] prints this help and usage message\n")
    usage.append("  [-k | --keep] number of days to keep backups before deleting\n")
    usage.append("  [-d | --databases] a comma separated list of databases\n")
    usage.append("  [-t | --store] directory locally to store the backups\n")
    usage.append("  [-u | --user] the database user\n")
    usage.append("  [-p | --password] the database password\n")
    usage.append("  [-s | --host] the database server hostname\n")
    usage.append("  [-o | --options] the json file to load the options from instead of using command line\n")
    usage.append("  [-r | --restore] enables restore mode\n")
    usage.append("  [-v | --version] get version\n")
    message = ''.join(usage)
    print(message)


"""
Main method that starts up the backup.  
"""


def main(argv):
    # set the default values
    pid_file = tempfile.gettempdir() + os.sep + "mysql_backup.pid"
    keep = 90
    databases = None
    user = None
    password = None
    host = None
    store = None
    options = None
    restore = False

    try:

        # process the command line options
        st = "hn:k:d:t:u:p:s:o:r:v"
        lt = ["help", "keep=", "databases=", "store=", "user=", "password=",
              "host=", "options=", "restore", "version"]
        opts, args = getopt.getopt(argv, st, lt)

        # if no arguments print usage
        if len(argv) == 0:
            usage()
            sys.exit()

        # detect if loading options from file and load the json
        vals = {}
        fopts = None
        for opt, arg in opts:
            vals[opt] = arg
        if ("-o" in vals.keys()) or ("--options" in vals.keys()):
            opt = "-o" if "-o" in vals.keys() else "--options"
            with open(vals[opt], 'r') as content_file:
                fopts = json.load(content_file)

        # merge with opts
        opts_keys = map(lambda val: val[0], opts)
        if fopts:
            for key in fopts.keys():
                prefix = ""
                if key in st.split(":"):
                    prefix = "-"
                elif key in map(lambda t: t[:-1] if t[-1] == "=" else t, lt):
                    prefix = "--"
                else:
                    continue
                if prefix + key not in opts_keys:
                    opts.append((prefix + key, fopts[key]))

        # loop through all of the command line options and set the appropriate
        # values, overriding defaults
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-k", "--keep"):
                keep = int(arg)
            elif opt in ("-d", "--databases"):
                databases = arg
            elif opt in ("-t", "--store"):
                store = arg
            elif opt in ("-u", "--user"):
                user = arg
            elif opt in ("-p", "--password"):
                password = arg
            elif opt in ("-s", "--host"):
                host = arg
            elif opt in ("-r", "--restore"):
                restore = True
            elif opt in ("-v", "--version"):
                version_info = {'version': version}
                print(version_info)
                sys.exit()

    except getopt.GetoptError as msg:
        logger.warning(msg)
        # if an error happens print the usage and exit with an error
        usage()
        sys.exit(errno.EIO)

    # check options are set correctly
    if user is None or store is None:
        logger.warning("Backup store directory (-t) and user (-u) are required")
        usage()
        sys.exit(errno.EPERM)

    # process backup, catch any errors, and perform cleanup
    try:

        # another backup can't already be running, if pid file doesn't exist, then
        # create it
        if os.path.exists(pid_file):
            logger.warning("Backup running, %s pid exists, exiting." % pid_file)
            sys.exit(errno.EBUSY)
        else:
            pid = str(os.getpid())
            f = open(pid_file, "w")
            f.write("%s\n" % pid)
            f.close()

        # create the backup object and call its backup method
        mysql_backup = MysqlBackup(keep, databases, store, user, password, host)
        if restore:
            raise BaseException('Not support')
        else:
            mysql_backup.backup()

    except Exception as msg:
        logger.exception("Mysql backups failed. %s" % msg)
    finally:
        os.remove(pid_file)


# if we are running the script from the command line, run the main function

if __name__ == "__main__":
    main(sys.argv[1:])