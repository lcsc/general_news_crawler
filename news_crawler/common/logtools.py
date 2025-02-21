import multiprocessing as mp
import logging
import os

log = logging.getLogger("news_crawler")
console=logging.StreamHandler()

log.setLevel(logging.DEBUG)

console.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
log.addHandler(console)

def initLogger():
    log.info("Initalizing Loggin")

def updateLogger():
    console.setFormatter(logging.Formatter("[%(processName)s][%(levelname)s]: %(message)s"))
    if mp.current_process().name != "MainProcess":
        if not os.path.exists("./log"):
            os.makedirs("log",exist_ok=True)
        file = logging.FileHandler(f"./log/{mp.current_process().name}.log",mode="w")
        file.setFormatter(logging.Formatter("[%(processName)s][%(asctime)s][%(levelname)s]: %(message)s"))
        log.addHandler(file)
   

