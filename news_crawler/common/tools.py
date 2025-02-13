import traceback
import requests
import os
import sys

from ..model.newspaper import NewsPaper

from pymongo import MongoClient


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
    traceback.print_exc()
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
       
def save_file(path:str, contents:any):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)
    with open(path, 'w', newline='') as file:
        file.write(contents)

def np_base_path(np:NewsPaper):
    return f"data/{np.ccaa}/{np.short_name}"

def connect_mongo(mongo_url:str=None,
                  username:str=None,
                  password:str=None
                  )->MongoClient:
    if mongo_url is None :
        mongo_url = os.environ.get("MONGODB_URL","mongodb://host.docker.internal:27017")
    if username is None:
        username=os.environ.get("MONGODB_USERNAME","root")
    if password is None:
        password = os.environ.get("MONGODB_PASSWORD","example")

    client = MongoClient(mongo_url,username=username,
                     password=password,)
    return client