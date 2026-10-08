import os

import importlib.resources
class CienaConnector:
    def __init__(self):
        pass
    def ls_base(self):
        ret = {"detect": [],"classify":[]}
        for f in importlib.resources.contents(__package__):
            if not f.endswith(".yaml"):
                continue
            print(f" test {f}")
            if f.startswith("detect."):
                print(f" det {f.split(".")}")
                short_name=f.split(".")[1]
                ret["detect"].append(short_name) 
            if f.startswith("classify."):
                short_name=f.split(".")[1]
                ret["classify"].append(short_name)
        return ret