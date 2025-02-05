from bs4 import BeautifulSoup

def pi_has_link_on_footer(doc:BeautifulSoup):
    footer = doc.find_all("footer")
    #print(footer)
    if footer is None:
        return False
    
    for f in footer:
        links = f.find_all("a")
        for l in links:
            if l.has_attr("href"):
                if  "https://www.prensaiberica360.es/" in l["href"]:
                    return True
                if "https://www.prensaiberica.es/" in l["href"]:
                    return True
    return False


# Esta el grupo noticias (www.deia.eus) que es el mismo motor, cambia el footer

def pi_get_head_link_canonical(doc:BeautifulSoup):
    # esto aparece en los de Prensa iberica
    #<link rel="canonical" href="https://www.laopiniondezamora.es/mapaweb/">
    head = doc.find("head")
    if head is None: return None
    link = head.find("link",{"rel":"canonical"})
    if link is None: return None
    if link.has_attr("href"): return link["href"]
    return None

def pi_get_head_meta_ogurl(doc:BeautifulSoup):
    # esto aparece en otros
    #<meta property="og:url" content="https://www.tagoror.es/index.html">
    head = doc.find("head")
    if head is None: return None
    link = head.find("meta",{"property":"og:url"})
    if link is None: return None
    if link.has_attr("content"): return link["content"]
    return None

# Lista extraida de un JS de una de las paginas.
pi_web_list=[
"lne.es",
"diaridegirona.cat",
"diariodeibiza.es",
"diariodemallorca.es",
"levante-emv.com",
"laopinioncoruna.es",
"superdeporte.es",
"laopiniondemalaga.es",
"laopiniondemurcia.es",
"laopiniondezamora.es",
"laprovincia.es",
"regio7.cat",
"eldia.es",
"mallorcazeitung.es",
"emporda.info",
"diariocordoba.com",
"stilo.es",
"codigonuevo.com",
"elperiodicomediterraneo.com",
"elperiodicodearagon.com",
"elperiodicoextremadura.com",
"sport.es",
"elperiodico.com",
"elperiodico.cat",
"epe.es",
"elcorreogallego.es",
"elcorreoweb.es",
"neomotor.com",
]