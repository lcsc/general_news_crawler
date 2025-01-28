
import requests

def get_url(api_url):
    headers = { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(api_url , timeout=(3,60), headers=headers) # 3s connection, 60s download)
    print(f"{api_url} {response.status_code}")
    while response.status_code==521 or response.status_code==521:
        response = requests.get(api_url, timeout=(3,60)) # 3s connection, 60s download)
        print(f"{api_url} {response.status_code}")
    return response

def print_exception(e:Exception):
    print("##### ERROR #####")
    print(e)
    print("##### ERROR #####")

def get_server_name_from_url(url:str):
    url = url.replace("http://","")
    url = url.replace("https://","")
    url = url.split("/")
    return url[0]


def get_short_name_from_server_name(server_name:str):
    #print(server_name)
    ret = server_name.removeprefix("www.")
    ret = ret.split(".")
    return ret[0]

def normalize_url(url:str):
    if url.startswith("http://"):
        url=url.replace("http://","https://")
    if not url.endswith("/"):
        url = url + "/"
    return url
       
