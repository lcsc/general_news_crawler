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
