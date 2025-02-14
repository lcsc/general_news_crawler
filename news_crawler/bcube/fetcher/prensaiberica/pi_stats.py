
from ....core.model.newspaper import NewsPaper, NewsPaperRepository
from ....common.tools import get_short_name_from_server_name
from ...model.prensaiberica import PrensaIbericaStat
from ....core.model.repos import CrawlerRepos
from ...model.prensaiberica import BcubePiMd
from .pi_tools import pi_web_list

def get_Newspaper(repo: NewsPaperRepository, name:str)->NewsPaper:
    shortname= get_short_name_from_server_name(name)




class PiAnalisys():

    def __init__(self):
        self._repos = CrawlerRepos()
        pass

    def get_js_stat(self, name:str)->PrensaIbericaStat:
        ret = self._repos.piStats.find_one_by({"js_name":name})
        if ret is None:
            ret = PrensaIbericaStat(
                id= None,
                ccaa=None,
                short_name=get_short_name_from_server_name (name),
                js_name=name,
                repo_found=False,
                num_cats=0)
        return ret

    def check_one_js(self, name:str)->PrensaIbericaStat:
        ret = self.get_js_stat(name)
        print(f"Testing js newspaper {name} ({ret.short_name})")

        in_repo = self._repos.newspaper.find_by({"short_name":ret.short_name})
        in_repo = list(in_repo)
        if in_repo is None or len(in_repo)==0:
            return ret
        
        if len(in_repo)>1:
            raise Exception("Too much news papers")
        
        in_repo = in_repo[0]
        ret.ccaa=in_repo.ccaa
        ret.repo_found=True

        in_md = self._repos.bCubePiMd.find_one_by({"ccaa":ret.ccaa, "short_name":ret.short_name})
        if in_md is not None:
            ret.num_cats=len(in_md.found_cats)

        return ret
    def check_one_found(self,np:BcubePiMd):
        ret = self._repos.piStats.find_one_by({"ccaa":np.ccaa,"short_name":np.short_name})
        if ret is None:
            ret = PrensaIbericaStat(
                id= None,
                ccaa=np.ccaa,
                short_name=np.short_name,
                js_name=None,
                repo_found=True,
                num_cats=0)
        ret.num_cats=len(np.found_cats)
        pass
    def checkPi(self):
        for name in pi_web_list:
            jsStat = self.check_one_js(name)
            if jsStat is not None:
                self._repos.piStats.save(jsStat)
        found_pi= self._repos.bCubePiMd.find_by({"link_on_foot":True})
        for np in found_pi:
            found = self.check_one_found(np)
            if found is not None:
                self._repos.piStats.save(found)
        pass
