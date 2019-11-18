#代理
import requests
url="http://ip.hahado.cn/ip"
proxy={"http":"http://"}
response=requests.get(url=url,proxies=proxy)
print(response.text)