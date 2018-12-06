import requests

url='http://jiuye.csmu.edu.cn/jy/login'
res=requests.get(url,allow_redirects=False)
print(res.headers)


header={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
'Connection': 'keep-alive',
'Cookie': 'JSESSIONID=15BF1B14D7D55566B25D38DD98861136',
'Host': 'jiuye.csmu.edu.cn',
'Referer': 'http://jiuye.csmu.edu.cn/jy/desktop/main',
'Upgrade-Insecure-Requests': '1',
',User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}


#res=requests.get(url,headers=header)





