import logging

log = logging.getLogger("news_api")
console=logging.StreamHandler()

log.setLevel(logging.DEBUG)

console.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
log.addHandler(console)

def init_log():
    pass