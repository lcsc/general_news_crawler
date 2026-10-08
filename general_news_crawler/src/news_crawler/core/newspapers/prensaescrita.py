from .lister import NewsPaperLister, PRENSA_ESCRITA, getProvId
from ...common.tools import get_url,normalize_url
from ..model.newspaper import NewsPaperListerInfo

from typing import List
from bs4 import BeautifulSoup

import logging
LOG = logging.getLogger(__name__)

ccaa_urls={
    'andalucia':'https://www.prensaescrita.com/andalucia.php',
    'aragon':'https://www.prensaescrita.com/aragon.php',
    'canarias': 'https://www.prensaescrita.com/canarias.php',
    'cantabria': 'https://www.prensaescrita.com/cantabria.php',
    'castillamancha': 'https://www.prensaescrita.com/castillam.php',
    'castillaleon': 'https://www.prensaescrita.com/castillal.php',
    'catalunya':'https://www.prensaescrita.com/catalunya.php',
    'madrid':'https://www.prensaescrita.com/madrid.php',
    'navarra':'https://www.prensaescrita.com/navarra.php',
    'valencia':'https://www.prensaescrita.com/valenciana.php',
    'extremadura':'https://www.prensaescrita.com/extremadura.php',
    'galicia':'https://www.prensaescrita.com/galicia.php',
    'baleares':'https://www.prensaescrita.com/baleares.php',
    'rioja':'https://www.prensaescrita.com/rioja.php',
    'pvasco':'https://www.prensaescrita.com/euskadi.php',
    'asturias':'https://www.prensaescrita.com/asturias.php',
    'murcia':'https://www.prensaescrita.com/murcia.php',
    'ceutamelilla':'https://www.prensaescrita.com/ceutaym.php'
}


class PrensaEscritaLister(NewsPaperLister):
    
    def get_newspapers_ccaa(self, ccaa:str, in_prov:str=None)->List[NewsPaperListerInfo]:
        LOG.info(f"Buscando Periodicos de {ccaa}/{in_prov}")
        ret = []
        r = get_url(ccaa_urls[ccaa])
        if r.status_code != 200:
            LOG.warning(f"{r.status_code} {ccaa_urls[ccaa]}")
            return None
        #html = r.content.decode("utf-8")

        doc = BeautifulSoup(r.content, 'lxml')
        tables = doc.find_all("table",{"width":"100%","height":"160","bgcolor":"#ffffff"})
        #for t in tables:
        if len(tables)>1:
            LOG.warning ("Warn: Found serveral candidates")
        t =tables[0]
        LOG.info('found '+str(len(tables)))

        tables = t.find_all("table",{"width":"100%","cellpadding":"2","bgcolor":"#ffffff"})
        LOG.info('   sub_tables '+str(len(tables)))
        t =tables[0]
        #with open(ca+".0.html", "w") as f:
        #    f.write(str(t))
        rows = t.find_all('tr',recursive=False)
        prov=None
        for i_row, row in enumerate(rows):
            cells =row.find_all('td',recursive=False)
            if len(cells) == 1:
                prov_tag=cells[0].find("h2")
                if prov_tag is not None:
                    prov= getProvId(prov_tag.text)

                LOG.info(f"   {i_row}: {len(cells)} {prov}")
            if len(cells) == 4:
                name= cells[1].text.strip()
                ciudad= cells[2].text.strip()
                link=cells[3].find('a')['href']
                LOG.info(f"   {i_row}: {len(cells)} {name} {ciudad} {link}")
                
                if in_prov is None or prov == in_prov:
                    ret.append(NewsPaperListerInfo(
                        #id=None,
                        ccaa=ccaa,
                        provincia=prov,
                        name=name,
                        #short_name=get_short_name_from_server_name(get_server_name_from_url(link)),
                        type=None,
                        url=normalize_url(link),
                        city=ciudad,
                        #real_url=None,
                        #alt_urls=None,
                        src=PRENSA_ESCRITA))
        return ret