from ..model.engine import NewsPaperEngine
from ..model.newspaper import NewsPaper 
import json

from requests import Response
from bs4 import BeautifulSoup


class DetectionState():
    def __init__(self, newsPaper:NewsPaper):
        self._newsPaper = newsPaper
        self._reponse:Response = None
        self._doc: BeautifulSoup = None
        pass

    def get_headers(self):
        return self._reponse.headers
    
    def get_doc(self):
        if self._doc is None: 
            self._doc = BeautifulSoup(self._reponse.content, 'lxml')
        return self._doc

class EngineDetector():
    def __init__(self ):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        pass

class WPDetector(EngineDetector):
    def __init__(self):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        ret = NewsPaperEngine(engine="wordpress", sub_engine="wp-json")
        respHdrs = state.get_headers()
        if "link" in respHdrs and "wp-json" in respHdrs["link"]: 
            ret.evidence = {"type":"header",
                            "link":respHdrs["link"]}
            return ret
    
        doc = state.get_doc()

        head = doc.find("head")
        if head is None: return None
        links = head.find_all("link",{"rel":"https://api.w.org/"})
        for m in links:
            if "wp-json" in m["href"]: 
                ret.evidence = {"type":"html head link",
                                "link":m["href"]}
                return ret

        return None
    


class BcubeDetector(EngineDetector):
    def __init__(self):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        
        doc = state.get_doc()
        head = doc.find("head")
        if head is None: return None
        
        meta = head.find_all("meta",{"name":"generator"})
        for m in meta:
            if 'bCube' in m["content"]:
                return NewsPaperEngine(engine="bCube", sub_engine=None, evidence={"type":"html head meta","name":m["name"],"content":m["content"]})
    
        return None



class JoomlaDetector(EngineDetector):
    def __init__(self):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        ret = NewsPaperEngine(engine="Joomla", sub_engine=None)
        respHdrs = state.get_headers()

        if "X-content-encoded-by" in respHdrs and respHdrs["X-content-encoded-by"].startswith("Joomla"):
            ret.evidence = {"type":"header",
                            "X-content-encoded-by":respHdrs["X-content-encoded-by"]}
            return ret

        return None

class DrupalDetector(EngineDetector):
    def __init__(self):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        ret = NewsPaperEngine(engine="Drupal", sub_engine=None)
        respHdrs = state.get_headers()
        if "X-Generator" in respHdrs and respHdrs["X-Generator"].startswith("Drupal"): 
            ret.evidence = {"type":"header",
                            "X-Generator":respHdrs["X-Generator"]}
            return ret
        if "X-Drupal-Cache" in respHdrs: 
            ret.evidence = {"type":"header",
                            "X-Drupal-Cache":respHdrs["X-Drupal-Cache"]}
            return ret
        return None

class OpenNemasDetector(EngineDetector):
    def __init__(self):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        ret = NewsPaperEngine(engine="OpenNemas", sub_engine=None)
        doc = state.get_doc()
        head = doc.find("head")
        if head is None: return None
        meta = head.find_all("meta",{"name":"generator"})
        for m in meta:
            if 'OpenNemas' in m["content"]: 
                ret.evidence = {"type":"html head meta",
                                "name":m["name"],
                                "content":m["content"]}
                return ret
        return None

class BloggerDetector(EngineDetector):
    def __init__(self):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        ret = NewsPaperEngine(engine="Blogger", sub_engine=None)
        doc= state.get_doc()
        head = doc.find("head")
        if head is None: return None
        meta = head.find_all("meta",{"name":"generator"})
        for m in meta:
            if m["content"]=='blogger':
                ret.evidence = {"type":"html head meta",
                                "name":m["name"],
                                "content":m["content"]}
                return ret
    
        return None


class VocentoDetector(EngineDetector):
    def __init__(self):
        pass

    def detect(self, state:DetectionState)->NewsPaperEngine:
        ret = NewsPaperEngine(engine="Vocento", sub_engine=None)
        doc = state.get_doc()
        head = doc.find("head")
        if head is None: 
            return None
        #meta = head.find_all("meta",{"name":"generator"})
        meta = head.find_all("script", {"type":"application/ld+json"})
        for m in meta:
            try:
                data= json.loads(m.string)
            
                if isinstance(data,dict):
                    if "memberOf" not in data:
                        continue
                    for p in data["memberOf"]:
                        if "name" in p and "Vocento" in p["name"]:
                            ret.evidence = {"type":"html head script",
                                                "data":p}
                            return ret
            except:
                continue
        meta = head.find_all("link")
        for m in meta:
            if "href" not in m:
                continue
            if "vocstatic" in m["href"]:
                ret.evidence = {"type":"html head link",
                                "href":m["href"]}
                return ret
        
        return None
    
'''
<link href="https://static.vocstatic.com" rel="preconnect"/>
<link href="https://static.vocstatic.com" rel="dns-prefetch"/>

'''