
from ..common import consts
from ..common.tools import get_server_name_from_url, get_short_name_from_server_name
from ..model.newspaper import NewsPaper, NewsPaperRepository ,NewsPaperListerInfo
from typing import List
from pymongo.database import Database


class NewsPaperLister():
    def __init__(self,database:Database):
        self._repo = NewsPaperRepository(database=database)
        pass

    def get_newspapers_ccaa(self,ccaa)->List[NewsPaperListerInfo]:
        pass
    
    def get_newspapers(self)->list[NewsPaperListerInfo]:
        all:list[NewsPaper] =[]
        for ca in consts.ccaa:
            all.extend(self.get_newspapers_ccaa(ca))
        return all

    def _search_newspaper(self,npaper:NewsPaperListerInfo)->NewsPaper:
        short_name = get_short_name_from_server_name(get_server_name_from_url(npaper.url))
        ret:NewsPaper = self._repo.find_one_by({"short_name":short_name})
        if ret is None:
            ret = NewsPaper(id=None,
                            name = npaper.name,
                            ccaa=npaper.ccaa,
                            provincia=npaper.provincia,
                            short_name=short_name,
                            real_url=None,
                            alt_urls=None,
                            lister_info=[])
        ret.lister_info.append(npaper)
        return ret
    '''
        ret:NewsPaper=None
        if npaper is None:
            return None
        
        # si tiene ID se busca por ID
        if npaper.id is not None:
            ret= self._repo.find_one_by_id(npaper.id)
        if ret is not None: return ret
        
        # si tiene url original se busca por url
        if npaper.original_url is not None:
            ret = self._repo.find_one_by({"original_url":npaper.original_url})
            if ret is not None: return ret
            # Sinó se busca por url real
            ret = self._repo.find_one_by({"real_url":npaper.original_url})
            if ret is not None: return ret
            # pendiente buscar en urls alternativas
        
        if npaper.short_name is not None:
            ret = self._repo.find_one_by({"_short_name":npaper.short_name})


        if npaper.name is not None:
            ret = self._repo.find_one_by({"name":npaper.name})
        
        
        return ret
'''
    def _merge_newspaper(self, in_db:NewsPaper):
        if len(in_db.lister_info)>1:
            print(f"WARNING: {in_db.short_name} has more than one lister info:\n{in_db}\n")
        return in_db

    def store_newspapers(self, list:List[NewsPaperListerInfo]):
        for np in list:
            in_db = self._search_newspaper(np)
            merged= self._merge_newspaper(in_db)
            self._repo.save(merged)
        pass