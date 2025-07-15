from datetime import datetime,timezone
import sys
from datetime import timedelta

from typing import List,Dict,Tuple
from ..core.model.newspaper import NewsArticle
from .consts import month_thresold
import logging

LOG:logging.Logger=logging.getLogger(__name__)

#diferentes codificaciones de 0
invalid_dates= [datetime.fromisoformat("1970-01-01 00:00:00Z"),datetime.fromisoformat("1970-01-01 00:00:01Z"),
                datetime.fromisoformat("1969-12-31T23:00:00Z"),datetime.fromisoformat("1969-12-31T23:00:01Z"),
                datetime.fromisoformat("1999-11-30T00:00:00Z"),]

# Fecha del primer articulo en españa
first_article_spain = datetime.fromisoformat("1661-01-01T00:00:00Z")

# Cuanto tiempo debe haber pasado para volver a comprobar (en bulk)
delta_to_check = timedelta(days=7)

# Fecha minima, si nos viene negativa la cambiamos por esta
fecha_minima = datetime.fromisoformat("0001-01-01T00:00:00Z")

def isValidDay(day:datetime|str):

    if isinstance(day,str):
        if day.startswith("-"):
            return False
        day=datetime.fromisoformat(day)

    if day.tzinfo is None:
        day=day.replace(tzinfo=timezone.utc)

    if day < first_article_spain:
        return False
    if day in invalid_dates:
        return False
    return True

def build_monthly_histogram(articles:List[NewsArticle],histogram:Dict[str,int]={})->Dict[str,int]:
    for arti in articles:
        month = arti.date.strftime("%Y-%m")
        if month not in histogram:
            histogram.update({month:1})
        else:
            histogram[month] += 1

    return histogram

def find_first_month(histogram:Dict[str,int])->str:
    months = sorted(list(histogram.keys()))
    first_month:str=None
    for m in months:
        if histogram[m] >= month_thresold:
            if first_month is None:
                first_month=m
            if m < first_month:
                first_month=m
    return first_month


def get_range(year:int,month:int=None,day:int=None)->Tuple[datetime,datetime]:
    '''
    Convierte los parametros de usuaro en un rango de comienzo fin
    return (comienzo,fin)
    '''
    if month is None:
        LOG.debug("Nos solicitan un Año")
        #2017-02-01T15:12:09.000Z
        start = datetime.fromisoformat(f"{year}-01-01T00:00:00Z")
        end = datetime.fromisoformat(f"{year+1}-01-01T00:00:00Z")-timedelta(seconds=1)
        return (start,end)
    if day is None:
        LOG.debug("Nos solicitan un Mes")
        #2017-02-01T15:12:09.000Z
        start = datetime.fromisoformat(f"{year}-{month:02}-01T00:00:00Z")
        if month==12:
            end = datetime.fromisoformat(f"{year+1}-01-01T00:00:00Z")-timedelta(seconds=1)
        else:
            end = datetime.fromisoformat(f"{year}-{month+1:02}-01T00:00:00Z")-timedelta(seconds=1)
        return (start,end)
    start = datetime.fromisoformat(f"{year}-{month:02}-{day:02}T00:00:00Z")
    end = start+timedelta(days=1)-timedelta(seconds=1)
    return (start,end)