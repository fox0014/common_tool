#!/usr/bin/env python
# encoding: utf-8

import subprocess
import os
import logging

logger = logging.getLogger(__file__)

CUR_DIR = os.path.dirname(os.path.realpath(__file__))


class AnsibleTask:
    def __init__(self, task_name, private_key, remote_user, inventory, playbook, cluster_id=None, action=None,
                 work_dir=CUR_DIR):
        self.task_name = task_name
        self.action = action
        self.playbook = playbook
        self.remote_user = remote_user
        self.inventory = inventory
        self.cluster_id = cluster_id
        self.private_key = private_key
        self.work_dir = work_dir

    def check_params(self):
        if self.task_name in ['zabbix_server', 'zabbix_proxy']:
                logger.info('gogogo')
                return True

        if self.task_name == 'zabbix':
                logger.error('Please input a valid name')
                return False
        return True

    def execute(self):
        extra_vars = ''
        check_params = self.check_params()
        if check_params:
            if self.task_name:
                extra_vars += 'host=%s ' % self.task_name
            else:
                extra_vars += 'host= '
        cmd = 'ansible-playbook -i %s %s --private-key %s -u %s --extra-vars="%s"' % (
        self.inventory, self.playbook, self.private_key, self.remote_user, extra_vars)
        self.run_command(cmd)

    def run_command(self, cmd):
        logger.info('run command: dir=%s cmd=%s', self.work_dir, cmd)
        p = subprocess.Popen(cmd,
                             cwd=self.work_dir,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT
                             )

        returncode = p.poll()
        while returncode is None:
            line = p.stdout.readline()
            returncode = p.poll()
            line = line.strip()
            logger.info(line)


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(filename)s-[line:%(lineno)d]'
                                  '-%(levelname)s-[日志信息]: %(message)s',
                                  datefmt='%a, %d %b %Y %H:%M:%S')
    ch.setFormatter(formatter)
    # 给logger添加handler
    logger.addHandler(ch)
    client = AnsibleTask('zabbix_server', '/home/console/.ssh/zabbix-server', 'centos',
                            '/home/1/1/1/zabbix_hosts',
                            '/home/1/1/1/1.yaml')
    client.execute()