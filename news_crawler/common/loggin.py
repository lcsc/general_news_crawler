import multiprocessing as mp
import logging

log = logging.getLogger("news_crawler")
console=logging.StreamHandler()

log.setLevel(logging.DEBUG)

console.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
log.addHandler(console)

def initLogger():
    print("Initalizing Loggin")

def updateLogger():
    console.setFormatter(logging.Formatter("[%(processName)s][%(levelname)s]: %(message)s"))
    if mp.current_process().name != "MainProcess":
        file = logging.FileHandler(f"./log/{mp.current_process().name}.log",mode="w")
        file.setFormatter(logging.Formatter("[%(processName)s][%(asctime)s][%(levelname)s]: %(message)s"))
        log.addHandler(file)
   

