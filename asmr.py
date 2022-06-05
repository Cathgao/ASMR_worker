import json
import requests
import os
import urllib.parse
from urllib.parse import urlparse

#指定token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FzbXIub25lIiwic3ViIjoiQ2F0aDEyMzQiLCJhdWQiOiJodHRwczovL2FzbXIub25lL2FwaSIsIm5hbWUiOiJDYXRoMTIzNCIsImdyb3VwIjoidXNlciIsImlhdCI6MTY1NDQzODMzMSwiZXhwIjoxNjU1NjQ3OTMxfQ.z4-ZjdzjMXEBuMRBuoI6WoKDZHHegSV9p_doqAwrO0E'
#指定作品RJ号
RJ_number = "388081"

# 进行UA伪装
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
}

# 指定作品url
work_url = 'https://api.asmr.one/api/work/' + RJ_number +  '?token=' + token

# 指定下载url
url = 'https://api.asmr.one/api/tracks/' + RJ_number +  '?token=' + token
# 调用requests.get方法对url进行访问，和持久化存储数据
audio_content = requests.get(url=url, headers=headers).content
jdata = json.loads(audio_content)
print(jdata)

# for base in jdata["children"]:
for i in range(len(jdata)):
    for base in jdata[i]["children"]:
        print("url: " + base["mediaDownloadUrl"])
        baseUrl = base["mediaDownloadUrl"]
        raw_path = os.path.split(urlparse(baseUrl).path.split("/",5)[-1])#获取url中的目录结构
        file_path = urllib.parse.unquote(raw_path[0])#转码
        print("path: " + file_path)
        if os.path.exists(file_path): #检查目录结构是否存在
            asmr = requests.get(baseUrl, headers=headers).content
            with open(file_path + "/" + base["title"], 'wb') as f:
                f.write(asmr)
        
        else:
            #创建文件夹
            os.makedirs(file_path)

print('下完了') 