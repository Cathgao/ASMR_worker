from asyncio.windows_events import NULL
from encodings import utf_8
import json
from tkinter import N
from turtle import title
import requests
import os
import urllib
from urllib.parse import urlparse
from tqdm import tqdm


token = NULL
RJ_number = NULL
user_info = {
    "name" : NULL,
    "password" : NULL
}
UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'

#######使用账户名密码登录######
def login():
    global user_info
    #账户名密码表单
    if ((user_info["name"] == NULL) or (user_info["password"] == NULL)):
        user_info = {
            "name" : input("输入账户名"),
            "password" : input("输入密码")
        }
    #headers信息
    loggin_headers = {
        "User-Agent" : UserAgent,
        "Uontent-Type" : "application/json"
    }
    #检查登录状态
    print("正在登录...")
    print("账户名： " + user_info["name"])
    print("密码： " + user_info["password"])
    res = requests.post(url='https://api.asmr.one/api/auth/me',data=user_info,headers=loggin_headers)
    if res.status_code != 200: 
        return -1
    else:#登录成功返回200，记录token
        token_raw = res.content
        global token
        token = json.loads(token_raw)["token"]
        print("获取token成功")
        return 0

#######下载实现########
def download(url: str, fname: str):
    # 用流stream的方式获取url的数据
    resp = requests.get(url, stream=True)
    # 拿到文件的长度，并把total初始化为0
    total = int(resp.headers.get('content-length', 0))
    if os.path.exists(fname):
        if os.path.getsize(fname) == total: #文件存在且大小相符
            print(fname + " 已下载，跳过")
            return
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


######查询作品号########
def check(RJnumber: str):
    if (RJnumber == NULL):
        return 0
    check_headers = {
        "User-Agent": UserAgent,
        "Authorization": "Bearer " + token,
    }
    res = requests.get(url='https://api.asmr.one/api/search/' +
                       RJnumber, headers=check_headers)
    aaa = json.loads(res.content)["works"]
    if(aaa == []):
        return 0
    else:
        return 1

#######检查配置文件######
if os.path.exists("user.json"):
    with open("user.json","r") as f:
        user_info = json.load(f)
    print("读取到已有账号")
    while(login() == -1):
        print("账户名或密码错误！")
        user_info = {
        "name" : NULL,
        "password" : NULL
        }
else:   
    while(login() == -1):
        print("账户名或密码错误！")
        user_info = {
        "name" : NULL,
        "password" : NULL
        }
with open("user.json","w")as f:
    f.write(json.dumps(user_info))


###########文件下载###########
while(RJ_number == NULL):
    RJ_number = input("输入作品编号（不包括前缀如“RJ”）： ")
if (not check(RJ_number)):  # 先检查作品是否存在
    print("作品不存在")
else:
    # 指定下载url
    url = 'https://api.asmr.one/api/tracks/' + RJ_number + '?token=' + token
    # 进行UA伪装
    headers = {
        'User-Agent': UserAgent
    }
    # 调用requests.get方法对url进行访问，和持久化存储数据
    audio_content = requests.get(url=url, headers=headers).content
    jdata = json.loads(audio_content)
    for i in range(len(jdata)):
        if "children" in jdata[i]:
            for base in jdata[i]["children"]:
                baseUrl = base["mediaDownloadUrl"]
                raw_path = os.path.split(urlparse(baseUrl).path.split("/", 5)[-1])  # 获取url中的目录结构
                file_path = urllib.parse.unquote(raw_path[0])  # 转码
                if os.path.exists(file_path): #检查目录结构是否存在
                    download(baseUrl,file_path + "/" + base["title"]) #下载文件
                else:
                    #创建文件夹
                    os.makedirs(file_path)
                    download(baseUrl,file_path + "/" + base["title"]) #下载文件
        else:  # 处理没有children的根目录url
            baseUrl = jdata[i]["mediaDownloadUrl"]
            a = urlparse(baseUrl).path.split("/", 5)
            raw_path = os.path.split(
                urlparse(baseUrl).path.split("/", 5)[-1])  # 获取url中的目录结构
            file_path = urllib.parse.unquote(raw_path[0])  # 转码
            if os.path.exists(file_path):  # 检查目录结构是否存在
                download(baseUrl,file_path + "/" + jdata[i]["title"]) #下载文件
            else:
                # 创建文件夹
                os.makedirs(file_path)
                download(baseUrl,file_path + "/" + jdata[i]["title"]) #下载文件
    print('下载完毕')
    print('等待修改根目录名')

    ###########修改根目录名###########
    # 指定作品url
    work_url = 'https://api.asmr.one/api/work/' + RJ_number + '?token=' + token
    work_content = requests.get(url=work_url, headers=headers).content
    work_data = json.loads(work_content)
    root_path = "RJ" + str(work_data["id"])
    if os.path.exists(root_path):
        os.rename(root_path,root_path + " " + work_data["title"])
    print('RJ' + RJ_number + "下载完毕")
    os.system("pause")