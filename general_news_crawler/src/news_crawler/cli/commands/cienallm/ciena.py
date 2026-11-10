

from news_crawler.core.cienallm import CienaConnector, CIENA_TASK_CLASSIFY, CIENA_TASK_DETECT
import yaml

class CienaCommand():
    def __init__(self):
        self.ciena = CienaConnector()
    
    def ls(self):
        baseConfigs = self.ciena.ls_base()
        print("Base configurations:")
        for key,value in baseConfigs.items():
            print(f"{key}: {value}")

    def get_ciena_config(self, task, name, model=None):
        if task not in [CIENA_TASK_DETECT, CIENA_TASK_CLASSIFY]:
            raise ValueError("Invalid task")
        config=self.ciena.get_ciena_config(task, name)
        with open(f"{name}.yaml","w") as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"Base configuration for task {task} and name {name} saved to {name}.yaml")
        