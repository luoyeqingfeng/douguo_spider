import  requests
import json
from multiprocessing import Queue
from handel_pymongo import mongo_info
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
#创建队列
quelue_list=Queue()

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

#处理菜谱数据
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

if __name__ == '__main__':
    #调用函数
    handler_index()
    #开启20个线程
    pool=ThreadPoolExecutor(max_workers=20)
    #判断队列中的个数是否大于0
    while quelue_list.qsize()>0:
        #提交到线程池，handler_caipu_list是函数，quelue_list.get()是从队列取出的数据
        pool.submit(handler_caipu_list,quelue_list.get())
    # handler_caipu_list(quelue_list.get())
