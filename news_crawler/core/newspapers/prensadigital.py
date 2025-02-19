from .lister import NewsPaperLister, PRENSA_DIGITAL,getProvId, getIdBasic
from ...common.tools import get_url,print_exception, normalize_url
from ..model.newspaper import NewsPaperListerInfo
from ...common.consts import provincias

from typing import List
from bs4 import BeautifulSoup, element

import logging
LOG = logging.getLogger(__name__)

ccaa_urls={
  'andalucia':{
    'url':'https://prensadigital.com/espana/periodicos-de-andalucia/',
    'almeria':'https://prensadigital.com/espana/periodicos-de-almeria/',
    'cadiz':'https://prensadigital.com/espana/periodicos-de-cadiz/',
    'cordoba':'https://prensadigital.com/espana/periodicos-de-cordoba/',
    'granada':'https://prensadigital.com/espana/periodicos-de-granada/',
    'huelva':'https://prensadigital.com/espana/periodicos-de-huelva/',
    'jaen':'https://prensadigital.com/espana/periodicos-de-jaen/',
    'malaga':'https://prensadigital.com/espana/periodicos-de-malaga/',
    'sevilla':'https://prensadigital.com/espana/periodicos-de-sevilla/',
  },
  'aragon':{
    'url':'https://prensadigital.com/espana/periodicos-de-aragon/',
    'huesca':'https://prensadigital.com/espana/periodicos-de-huesca/',
    'teruel':'https://prensadigital.com/espana/periodicos-de-teruel/',
    'zaragoza':'https://prensadigital.com/espana/periodicos-de-zaragoza/',
  },
  'asturias':{
    'url':'https://prensadigital.com/espana/periodicos-de-asturias/',
  },
  'baleares':{
    'url':'https://prensadigital.com/espana/periodicos-de-baleares/',
  },
  'canarias':{
    'url':'https://prensadigital.com/espana/periodicos-de-canarias/',
    'laspalmas':'https://prensadigital.com/espana/periodicos-de-las-palmas/',
    'santacruz':'https://prensadigital.com/espana/periodicos-de-santa-cruz-de-tenerife/',
  },
  'cantabria':{
    'url':'https://prensadigital.com/espana/periodicos-de-cantabria/',
  },
  'castillamancha':{
    'url':'https://prensadigital.com/espana/periodicos-de-castilla-la-mancha/',
    'albacete':'https://prensadigital.com/espana/periodicos-de-albacete/',
    'ciudadreal':'https://prensadigital.com/espana/periodicos-de-ciudad-real/',
    'cuenca':'https://prensadigital.com/espana/periodicos-de-cuenca/',
    'guadalajara':'https://prensadigital.com/espana/periodicos-de-guadalajara/',
    'toledo':'https://prensadigital.com/espana/periodicos-de-toledo/',
  },
  'castillaleon':{
    'url':'https://prensadigital.com/espana/periodicos-de-castilla-y-leon/',
    'avila':'https://prensadigital.com/espana/periodicos-de-avila/',
    'burgos':'https://prensadigital.com/espana/periodicos-de-burgos/',
    'leon':'https://prensadigital.com/espana/periodicos-de-leon/',
    'palencia':'https://prensadigital.com/espana/periodicos-de-palencia/',
    'salamanca':'https://prensadigital.com/espana/periodicos-de-salamanca/',
    'segovia':'https://prensadigital.com/espana/periodicos-de-segovia/',
    'soria':'https://prensadigital.com/espana/periodicos-de-soria/',
    'valladolid':'https://prensadigital.com/espana/periodicos-de-valladolid/',
    'zamora':'https://prensadigital.com/espana/periodicos-de-zamora/',
  },
  'catalunya':{
    'url':'https://prensadigital.com/espana/periodicos-catalanes/',
    'barcelona':'https://prensadigital.com/espana/periodicos-de-barcelona/',
    'girona':'https://prensadigital.com/espana/periodicos-de-girona/',
    'lleida':'https://prensadigital.com/espana/periodicos-de-lleida/',
    'tarragona':'https://prensadigital.com/espana/periodicos-de-tarragona/',
  },
  'extremadura':{
    'url':'https://prensadigital.com/espana/periodicos-de-extremadura/',
    'badajoz':'https://prensadigital.com/espana/periodicos-de-badajoz/',
    'caceres':'https://prensadigital.com/espana/periodicos-de-caceres/',
  },
  'galicia':{
    'url':'https://prensadigital.com/espana/periodicos-de-galicia/',
    'lacoruña':'https://prensadigital.com/espana/periodicos-de-coruna/',
    'lugo':'https://prensadigital.com/espana/periodicos-de-lugo/',
    'orense':'https://prensadigital.com/espana/periodicos-de-orense/',
    'pontevedra':'https://prensadigital.com/espana/periodicos-de-pontevedra/',
  },
  'rioja':{
    'url':'https://prensadigital.com/espana/periodicos-de-la-rioja/',
  },
  'madrid':{
    'url':'https://prensadigital.com/espana/periodicos-de-madrid/',
  },
  'murcia':{
    'url':'https://prensadigital.com/espana/periodicos-de-murcia/',
  },
  'navarra':{
    'url':'https://prensadigital.com/espana/periodicos-de-navarra/',
  },
  'pvasco':{
    'url':'https://prensadigital.com/espana/periodicos-vascos/',
    'alava':'https://prensadigital.com/espana/periodicos-de-alava/',
    'guipuzcoa':'https://prensadigital.com/espana/periodicos-de-guipuzcoa/',
    'vizcaya':'https://prensadigital.com/espana/periodicos-de-vizcaya/',
  },
  'valencia':{
    'url':'https://prensadigital.com/espana/periodicos-de-comunidad-valenciana/',
    'alicante':'https://prensadigital.com/espana/periodicos-de-alicante/',
    'castellon':'https://prensadigital.com/espana/periodicos-de-castellon/',
    'valencia':'https://prensadigital.com/espana/periodicos-de-valencia/',
  },
}


def getCaID(ca:str)->str:
    ca = getIdBasic(ca)
    nobasic={
        "castilla-lamancha":"castillamancha",
        "castillayleon":"castillaleon",
        "larioja":"rioja",
        "paisvasco":"pvasco",
        "comunidadvalenciana":"valencia",
    }
    if ca in nobasic:
        return nobasic[ca]
    return ca

class PrensaDigitalLister(NewsPaperLister):


    def _parse_one(self, ccaa, idx, idx_p, p,tipo,provincia)->NewsPaperListerInfo:
        if provincia=='url': provincia=None
        pub =p.select_one("h4 a")
        name= pub.text.strip()
        link=pub['href']
        LOG.info(f"   {idx} {idx_p}: {name} {link}")
        return (NewsPaperListerInfo(
                    #id=None,
                    ccaa=ccaa,
                    provincia=provincia,
                    name=name,
                    #short_name=get_short_name_from_server_name(get_server_name_from_url(link)),
                    type=tipo,
                    url=normalize_url(link),
                    #real_url=None,
                    #alt_urls=None,
                    src=PRENSA_DIGITAL))

    def _get_newspapers(self, ccaa, provincia)->List[NewsPaperListerInfo]:
        ret = []
        if ccaa == "ceutamelilla": return ret # no tiene información

        url = ccaa_urls[ccaa][provincia]
        r = get_url(url)

        html = r.content.decode("utf-8")
        #with open(ca+".html", "w") as f:
        #    f.write(html)
        #LOG.info(html)

        doc = BeautifulSoup(html, 'lxml')
        pubList = doc.find_all("div",{"id":"publishers-list"})
        LOG.info (ccaa)
        for idx,l in enumerate(pubList):
            #with open(ca+"."+str(idx)+".html", "w") as f:
            #    f.write(str(l))
            pubs = l.find_all('div',{'class':"stock-card"})
            tipo = l.parent.find("h2").text
            LOG.info(f"  {idx}: {len(pubs)} {tipo}")
            for idx_p,p in enumerate(pubs):
                try:
                    ret.append(self._parse_one(ccaa, idx, idx_p, p, tipo,provincia))
                except Exception as e: 
                    LOG.info_exception(e)

        #LOG.info(t)
        return ret
    
    def get_newspapers_ccaa(self, ccaa, provincia)->List[NewsPaperListerInfo]:
        search=[]
        ret = []
        if provincia is not None:
            search=[provincia]
        else:
            if len(provincias[ccaa])>1:
                search=provincias[ccaa]
            search.append("url")
        for item in search:
            ret.extend(self._get_newspapers(ccaa,item))
        return ret

        
    def listUrls(self):
        allURl='https://prensadigital.com/espana/'
        r = get_url(allURl)
        html = r.content.decode("utf-8")
        doc = BeautifulSoup(html, 'lxml')
        pubList = doc.find("div",{"id":"content"})
        pubList = pubList.find_all("div",{"class":"grid-1-2"})
        ret={}
        for div in pubList:
            sidebar = div.find("div",{"class":"sidebar"})
            if sidebar is not None: continue
            LOG.info("Found div")
            #LOG.debug(div)
            linkList= div.find_all("a")
            ca = None
            for link in linkList:
                lTag:element.Tag = link
                if lTag.parent.name=="h3":
                    ca=getCaID(link.text)
                    if ca not in provincias:
                        LOG.error(f"{ca} Not Found")
                    ret[ca]={"url":link["href"]}
                else:
                    prov = link.text
                    prov = getProvId(prov)
                    if prov not in provincias[ca]:
                        LOG.error(f" {ca}/{prov} ({link.text}) Not Found" )
                    ret[ca][prov]=link["href"]

                    pass
                
        return ret