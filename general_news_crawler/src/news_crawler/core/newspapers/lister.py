
from ...common import consts
from ...common.tools import get_server_name_from_url, get_short_name_from_server_name
from ..model.newspaper import NewsPaper, NewsPaperRepository ,NewsPaperListerInfo
from typing import List
from pymongo.database import Database

PRENSA_DIGITAL='https://www.prensadigital.com/'
PRENSA_ESCRITA='https://www.prensaescrita.com/'


PRENSA_DIGITAL_ID='PrensaDigital'
PRENSA_ESCRITA_ID='PrensaEscrita'

# Traducciones de como estan en la web a un nombre corto mas sencillo
provs_map={
'Sevilla':'sevilla',
'Málaga':'malaga',
'Cádiz':'cadiz',
'Granada':'granada',
'Córdoba':'cordoba',
'Almería':'almeria',
'Jaén':'jaen',
'Huelva':'huelva',
'Zaragoza':'zaragoza',
'Huesca':'huesca',
'Teruel':'teruel',
'Las Palmas':'laspalmas',
'Santa Cruz de Tenerife':'santacruz',
'Toledo':'toledo',
'Ciudad Real':'ciudadreal',
'Albacete':'albacete',
'Guadalajara':'guadalajara',
'Cuenca':'cuenca',
'Valladolid':'valladolid',
'León':'leon',
'Burgos':'burgos',
'Salamanca':'salamanca',
'Zamora':'zamora',
'Segovia':'segovia',
'Palencia':'palencia',
'Ávila':'avila',
'Soria':'soria',
'Barcelona':'barcelona',
'Tarragona':'tarragona',
'Girona':'girona',
'Lleida':'lleida',
'Valencia':'valencia',
'Alicante':'alicante',
'Castellón':'castellon',
'Badajoz':'badajoz',
'Cáceres':'caceres',
'A Coruña/La Coruña':'lacoruña',
'Coruña':'lacoruña',
'Pontevedra':'pontevedra',
'Lugo':'lugo',
'Ourense/Orense':'orense',
'Vizcaya - Bizkaia':'vizcaya',
'Guipúzcoa - Gipuzkoa':'guipuzcoa',
'Álava - Araba':'alava',
'Ceuta':'ceuta',
'Melilla':'melilla'
}

def getIdBasic(name:str)->str:
    name=name.lower()
    name=name.replace("á","a")
    name=name.replace("é","e")
    name=name.replace("í","i")
    name=name.replace("ó","o")
    name=name.replace("ú","u")

    if "/" in name:
        name =name.split("/")[1].removeprefix(" ")
    if " - " in name:
        name =name.split("-")[0].removesuffix(" ")
    name = name.replace(" ","")
    
    return name

def getProvId(prov:str)->str:
    if prov in provs_map:
        return provs_map[prov]
    
    prov = getIdBasic(prov)
    return prov


class NewsPaperLister():
    def __init__(self,repo:NewsPaperRepository):
        self._repo = repo
        pass

    def get_newspapers_ccaa(self,ca:str, prov:str=None)->List[NewsPaperListerInfo]:
        pass
    
    def get_newspapers(self, in_ca:str=None, in_prov:str=None)->list[NewsPaperListerInfo]:
        all:list[NewsPaper] =[]
        ccaa=consts.ccaa
        if in_ca is not None: 
            ccaa=[in_ca]
        for ca in ccaa:
            ca_list = self.get_newspapers_ccaa(ca,in_prov)
            if ca_list is not None:
                all.extend(ca_list)
        return all

    def _insert_lister_info(self,news:NewsPaper, npaper:NewsPaperListerInfo)->bool:
        for np in news.lister_info:
            if np.compare(npaper) == {}:
                return False
        return True


    def _search_newspaper(self,npaper:NewsPaperListerInfo)->NewsPaper:
        short_name = get_short_name_from_server_name(get_server_name_from_url(npaper.url))
        ret:NewsPaper = self._repo.find_one_by({"ccaa":npaper.ccaa,"short_name":short_name})
        if ret is None:
            ret = NewsPaper(id=None,
                            name = npaper.name,
                            ccaa=npaper.ccaa,
                            provincia=npaper.provincia,
                            short_name=short_name,
                            real_url=None,
                            alt_urls=None,
                            lister_info=[])
        if self._insert_lister_info(ret,npaper):
            ret.lister_info.append(npaper) 
            
        return ret
    def _get_field(self,field:str, in_db:NewsPaper):
        ret = {}

        for np in in_db.lister_info:
            if np.__getattribute__(field) is not None:
                val = np.__getattribute__(field)
                if val not in ret:
                    ret[val]=[np.src]
                else:
                    if np.src not in ret[val]:
                        ret[val].append(np.src)
        return ret
    
    def _select_field(self, found, priority):
        vals = found.keys()
        # Decisiones rapidas
        if len  (vals) == 1:
            return list(found.keys())[0]    
        if len(vals) == 0:
            return None
        # Decisiones con prioridad
        prior = []
        for k in vals:
            if priority in found[k]:
                prior.append(k)
        if len(prior)>0:
            return prior[0]
        # En el resto de casos, elijo el primero
        return list(vals)[0]    
    

    def _merge_newspaper(self, in_db:NewsPaper):
        #if len(in_db.lister_info)>1:
        #    Log.info(f"WARNING: {in_db.short_name} has more than one lister info:\n{in_db}\n")
        in_db.name = self._select_field(self._get_field("name",in_db),PRENSA_DIGITAL)
        in_db.provincia = self._select_field(self._get_field("provincia",in_db),PRENSA_ESCRITA)
        in_db.city = self._select_field(self._get_field("city",in_db),PRENSA_ESCRITA)
        in_db.type = self._select_field(self._get_field("type",in_db),PRENSA_DIGITAL)

        urls = self._get_field("url",in_db)
        if in_db.alt_urls is None:
            in_db.alt_urls = []
        for k in urls.keys():
            if k not in in_db.alt_urls:
                in_db.alt_urls.append(k)
        
        return in_db

    def store_newspapers(self, list:List[NewsPaperListerInfo]):
        for np in list:
            in_db = self._search_newspaper(np)
            merged= self._merge_newspaper(in_db)
            self._repo.save(merged)
        pass