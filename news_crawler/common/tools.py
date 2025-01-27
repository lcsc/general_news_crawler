
import requests

def get_url(api_url):
    response = requests.get(api_url , timeout=(3,60)) # 3s connection, 60s download)
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


#dominios regionales, por ahora solo cat y gal
regional_ccaa = ["cat","gal"]

def get_short_name_from_server_name(server_name:str):
    #print(server_name)
    ret = server_name.removeprefix("www.")
    ret = ret.split(".")
    #print(ret)
    if ret[-1] in regional_ccaa:
        return f"{ret[0]}.{ret[-1]}"
    return ret[0]