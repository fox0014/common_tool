#coding=utf-8
import random
import records
from functools import wraps
import time


db = records.Database('mysql+pymysql://root:123456@192.168.11.144:3306/just_test')


def func_timer(function):
    '''
    用装饰器实现函数计时
    :param function: 需要计时的函数
    :return: None
    '''
    @wraps(function)
    def function_timer(*args, **kwargs):
        print('[Function: {name} start...]'.format(name = function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print('[Function: {name} finished, spent time: {time:.2f}s]'.format(name = function.__name__,time = t1 - t0))
        return result
    return function_timer


def get_userNameAndPassword():
    # 8位用户名及6位密码
    userName = ''.join(random.sample("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-><:}{?/",8))
    userPassword = ''.join(random.sample("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.1234567890",6))
    return userName, userPassword

@func_timer
def exec(data):
    db.bulk_query('INSERT INTO students(name,nickname,in_time) values (:name, :nickname, now())', data)

if __name__ == "__main__":
    try:
        users = []
        for i in range(5000):
            userName, userPassword = get_userNameAndPassword()
            users.append({"name":userName, "nickname": userPassword})
        exec(users)
    except Exception as e:
        print(e.reason)

