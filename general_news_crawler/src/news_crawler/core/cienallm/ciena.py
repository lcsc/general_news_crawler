import os

import importlib.resources
from typing import Optional
import yaml


CIENA_TASK_DETECT="detect"
CIENA_TASK_CLASSIFY="classify"

class CienaConnector:
    def __init__(self):
        pass
    def ls_base(self):
        ret = {CIENA_TASK_DETECT: [],CIENA_TASK_CLASSIFY:[]}
        for f in importlib.resources.contents(__package__):
            if not f.endswith(".yaml"):
                continue
            #print(f" test {f}")
            if f.startswith("detect."):
                #print(f" det {f.split(".")}")
                short_name=f.split(".")[1]
                ret[CIENA_TASK_DETECT].append(short_name) 
            if f.startswith("classify."):
                short_name=f.split(".")[1]
                ret[CIENA_TASK_CLASSIFY].append(short_name)
        return ret

    def get_ciena_config(self, tast:str,name:str, model=None)->Optional[dict]:
        file_name=None
        if tast == CIENA_TASK_DETECT:
            file_name = f"detect.{name}.yaml"
        elif tast == CIENA_TASK_CLASSIFY:
            file_name = f"classify.{name}.yaml"
        else:
            return None

        if file_name is None:
            raise ValueError(f"Invalid task: {tast}")

        file_content=importlib.resources.read_text(__package__, file_name)
        ciena_config=yaml.safe_load(file_content)
        if model is not None:
            ciena_config["llm"]["name"]=model
        return ciena_config    

    
