'''
python 2
'''
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_command(pwd, cmd, status=0, exit=False, append_message=''):
    logger.info('run command dir=%s : cmd=%s' % (pwd, cmd))
    p = subprocess.Popen(cmd,
                         cwd=pwd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT
                         )
    returncode = p.poll()
    while returncode is None:
        line = p.stdout.readline()
        returncode = p.poll()
        line = line.strip()
        if append_message:
            logger.info('%s', append_message, line)
        logger.info('%s', line)
    _stauts = p.wait()
    if _stauts != status:
        logger.error('run command dir=%s : cmd=%s return %d, Error happen' % (pwd, cmd, _stauts))
        if exit:
            sys.exit(_stauts)
    return _stauts