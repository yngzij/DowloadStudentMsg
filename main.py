import  re
import requests

url = "http://jiuye.csmu.edu.cn/jy/login"

payload = "user_name=12015050801001&pass_word=123456"


headers = {
    'content-type': "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

session=requests.sessions.session()
res=session.get(url)
response = session.request("POST", url, data=payload, headers=headers)
res=session.request("GET",'http://jiuye.csmu.edu.cn/jy/desktop/index?note=true',headers=headers)

html=res.text
print(html)

institutes=re.search(r'important; \" value=\"(.*?)\"\/\>',res.text)
print(institutes)
jobs=re.search('name=\"yxdw1\" value=\"(.*?)\"',html)
print(jobs)



