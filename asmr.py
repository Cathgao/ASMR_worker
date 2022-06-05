import json
from turtle import title
import requests
import os
import urllib.parse
from urllib.parse import urlparse
from tqdm import tqdm


# 指定token
#此处替换你获得的下载token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FzbXIub25lIiwic3ViIjoiQ2F0aDEyMzQiLCJhdWQiOiJodHRwczovL2FzbXIub25lL2FwaSIsIm5hbWUiOiJDYXRoMTIzNCIsImdyb3VwIjoidXNlciIsImlhdCI6MTY1NDQzODMzMSwiZXhwIjoxNjU1NjQ3OTMxfQ.z4-ZjdzjMXEBuMRBuoI6WoKDZHHegSV9p_doqAwrO0E'
# 指定作品RJ号
#此处替换要下载的作品RJ号，不包括RJ前缀
RJ_number = "390697"


def download(url: str, fname: str):
    # 用流stream的方式获取url的数据
    resp = requests.get(url, stream=True)
    # 拿到文件的长度，并把total初始化为0
    total = int(resp.headers.get('content-length', 0))
    if os.path.exists(fname):
        if os.path.getsize(fname) == total: #文件存在且大小相符
            print(fname + " 已下载，跳过")
            return
    # 打开当前目录的fname文件(名字你来传入)
    # 初始化tqdm，传入总数，文件名等数据，接着就是写入，更新等操作了
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


# 进行UA伪装
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
}


###########文件下载###########
# 指定下载url
url = 'https://api.asmr.one/api/tracks/' + RJ_number + '?token=' + token
# 调用requests.get方法对url进行访问，和持久化存储数据
audio_content = requests.get(url=url, headers=headers).content
jdata = json.loads(audio_content)

# for base in jdata["children"]:
for i in range(len(jdata)):
    if "children" in jdata[i]:
        for base in jdata[i]["children"]:
            print("url: " + base["mediaDownloadUrl"])
            baseUrl = base["mediaDownloadUrl"]
            raw_path = os.path.split(urlparse(baseUrl).path.split("/", 5)[-1])  # 获取url中的目录结构
            file_path = urllib.parse.unquote(raw_path[0])  # 转码
            print("path: " + file_path)
            if os.path.exists(file_path): #检查目录结构是否存在
                download(baseUrl,file_path + "/" + base["title"]) #下载文件
            else:
                #创建文件夹
                os.makedirs(file_path)
                download(baseUrl,file_path + "/" + base["title"]) #下载文件
    else:  # 处理没有children的根目录url
        print("url: " + jdata[i]["mediaDownloadUrl"])
        baseUrl = jdata[i]["mediaDownloadUrl"]
        a = urlparse(baseUrl).path.split("/", 5)
        raw_path = os.path.split(
            urlparse(baseUrl).path.split("/", 5)[-1])  # 获取url中的目录结构
        file_path = urllib.parse.unquote(raw_path[0])  # 转码
        print("path: " + file_path)
        if os.path.exists(file_path):  # 检查目录结构是否存在
            download(baseUrl,file_path + "/" + jdata[i]["title"]) #下载文件
        else:
            # 创建文件夹
            os.makedirs(file_path)
            download(baseUrl,file_path + "/" + jdata[i]["title"]) #下载文件
print('下载完毕')

###########创建根目录###########
# 指定作品url
work_url = 'https://api.asmr.one/api/work/' + RJ_number + '?token=' + token
work_content = requests.get(url=work_url, headers=headers).content
work_data = json.loads(work_content)
root_path = "RJ" + str(work_data["id"])
#urllib.parse.unquote(os.path.split(urlparse(jdata[i]["mediaDownloadUrl"]).path.split("/", 5)[-1])[0])
if os.path.exists(root_path):
    os.rename(root_path,root_path + " " + work_data["title"])
print('所有工作完成')
