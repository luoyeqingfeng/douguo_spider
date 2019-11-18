## 1.项目简介
1. 采用Python3+Fiddler+模拟器的app爬虫
2. 此项目的功能是爬取豆果美食的各个菜谱
3. 采用requests库，数据库是用的mongdb
***
## 2.基本环境

1. 操作系统是windows10

2. 安装Python3.7
```markdown
官网地址：
https://www.python.org/downloads/
```
 3. 安装pip工具
```markdown
官网地址：
https://pypi.org/project/pip/#downloads
```
4. 安装Mongdb数据库
```markdown
官网地址：
https://www.mongodb.com/download-center?jmp=nav#community
```
5. 安装Fiddler抓包工具
```markdown
可以直接百度：fiddler下载
```
6. 安装夜神模拟器
```markdown
官网下载：https://www.yeshen.com/
```
7. 安装requests包
```markdown
#Requests是一个优雅而简单的Python HTTP库
pip install requests
```

***

# 3.代码解释
##### 1.请求模块
1. 写一个请求函数用来发送请求
2. 其中headers需要抓包查看
```python
#发送请求函数
def handler_request(url,data):
    """
    :param url: url地址
    :param data: 请求需要的数据
    :return:
    """
    #伪造请求头
    headers={
        "client":"4",
        "version":"6945.4",
        "device":"SM-G955F",
        "sdk":"22,5.1.1",
        "imei":"866174010208177",
        "channel":"sougousj",
        # "mac":"D0:17:C2:29:0D:19",
        "resolution":"1280*720",
        "dpi":"1.5",
        # "android-id":"d017c2290d199100",
        # "pseudo-id":"2290d199100d017c",
        "brand":"samsung",
        "scale":"1.5",
        "timezone":"28800",
        "language":"zh",
        "cns":"3",
        "carrier":"CHINA+MOBILE",
        # "imsi":"460072081719429",
        "User-Agent":"Mozilla/5.0 (Linux; Android 5.1.1; MI 5  Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36",
        "act-code":"a2443bbbe5b627e5ba69751acbd9ac05",
        "act-timestamp":"1568967265",
        "uuid":"229191c3-1962-40b6-9dee-647a4e9be469",
        "newbie":"0",
        "reach":"10000",
        "Content-Type":"application/x-www-form-urlencoded; charset=utf-8",
        "Accept-Encoding":"gzip, deflate",
        "Connection":"Keep-Alive",
        # "Cookie":"duid=61216869",
        "Host":"api.douguo.net",
        # "Content-Length":"98",
    }
    #向地址法起post请求
    response=requests.post(url=url,headers=headers,data=data)
    # 返回response对象
    return response
```

##### 2. 数据抓取分析模块
1.把Fiddler抓取到的url地址和需要是数据给请求模块
2.把返回的数据加以分析，发现需要的参数中，食材名称是变化的
```python
def handler_index():
    #原始地址，需要抓包分析
    url="http://api.douguo.net/recipe/flatcatalogs"
    #请求数据，这些数据在抓包工具里面查看
    data={
        "client":"4",
        # "_session":"1570779133692866174010208177",
        "v":"1570101227",
        "_vs":"2305",
    }
    #把url和data传递到andel_request函数中
    response=handler_request(url=url,data=data)
    #将返回的数据反序列化
    index_response_dict=json.loads(response.text)
    #循环取出dict的数据
    #json格式的数据，需要循环取出有用的信息
    for index_item in index_response_dict["result"]["cs"]:
        for index_item1 in index_item["cs"]:
            for item in index_item1["cs"]:
                # print(item)
                data_2={
                    "client": "4",
                    # "_session": "1570779133692866174010208177",
                    #食材
                    "keyword": item["name"],
                    # "_vs": "400",
                    "order": "0",
                    "_vs": "11102",
                    "type":"0",

                }
                #把data_2入队列
                quelue_list.put(data_2)
```
##### 3.数据处理入库模块
1.把需要的数据用循环提取出来
2.创建字典类型数据，这样符合mongdb的存储
3.然后调用写好的数据库模块入库
```python
def handler_caipu_list(data):
    print("当前出来的食材是：",data["keyword"])
    #url地址
    caipu_list_url="http://api.douguo.net/recipe/v2/search/0/20"
    #用请求函数发送请求
    caipu_list_response=handler_request(url=caipu_list_url,data=data)
    #把返回对象反序列化
    caipu_list_response_dict=json.loads(caipu_list_response .text)
    #循环取出需要的数据
    for item in caipu_list_response_dict["result"]["list"]:
        #创建一个空字典
        caipu_info={}
        #食材名称
        caipu_info["shicai"]=data["keyword"]
        #判断type是否等于13，
        if item["type"]==13:
            #用户名称
            caipu_info["user_name"]=item["r"]["an"]
            #食材id
            caipu_info["shicai_id"]=item["r"]["id"]
            #描述
            caipu_info["describe"]=item["r"]["cookstory"].replace("\n","").replace(" ","")
            #菜谱名称
            caipu_info["caipu_name"]=item["r"]["n"]
            #佐料
            caipu_info["zuoliao_list"]=item["r"]["major"]
            #制作细节的url
            detail_url="http://api.douguo.net/recipe/detail/"+str(caipu_info["shicai_id"])
            #url需要的数据，这些数据需要抓包查看
            detail_data={
                "client": "4",
                # "_session": "1570784815992866174010208177",
                 "author_id":"0",
                 "_vs": "11101",
                #需要食材满次和食材id
                "_ext": """{"query":{"kw":"%s","src":"11101","idx":"1","type":"13","id":"%s"}}"""%(caipu_info["shicai"],caipu_info["shicai_id"]),
            }
            #用handler_request函数发送请求
            detail_response=handler_request(url=detail_url,data=detail_data)
            #反序列化
            detail_response_dict=json.loads(detail_response.text)
            #制作方法
            caipu_info["tips"]=detail_response_dict["result"]["recipe"]["tips"]
            #制作步骤
            caipu_info["cook_step"]=detail_response_dict["result"]["recipe"]["cookstep"]
            print("当前入库的菜谱是：",caipu_info["caipu_name"])
            # print(caipu_info)
            #把数据存入mongdb数据库
            mongo_info.insert_item(caipu_info)

        #如果不是等于13就跳过
        else:
            continue
```
##### 4.数据库模块
1. 创建连接后插入数据
```python
class Connect_mongo(object):
    def __init__(self):
        #创建数据库连接对象
        self.client=pymongo.MongoClient(host="127.0.0.1",port=27017)
        #生成操作的数据库对象
        self.db_data=self.client["dou_guo_mei_shi"]
    def insert_item(self,item):
        #创建集合集合对象
        myset=self.db_data["dou_guo_mei_shi_item"]
        #插入数据
        myset.insert_one(item)

```



