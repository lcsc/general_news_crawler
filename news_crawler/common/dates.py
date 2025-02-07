from datetime import datetime,timezone
import sys
from datetime import timedelta
#diferentes codificaciones de 0
invalid_dates= [datetime.fromisoformat("1970-01-01 00:00:00Z"),datetime.fromisoformat("1970-01-01 00:00:01Z"),
                datetime.fromisoformat("1969-12-31T23:00:00Z"),datetime.fromisoformat("1969-12-31T23:00:01Z"),
                datetime.fromisoformat("1999-11-30T00:00:00Z"),]

# Fecha del primer articulo en españa
first_article_spain = datetime.fromisoformat("1661-01-01T00:00:00Z")

# Cuanto tiempo debe haber pasado para volver a comprobar (en bulk)
delta_to_check = timedelta(days=7)


def isValidDay(day:datetime):
    if day.tzinfo is None:
        day=day.replace(tzinfo=timezone.utc)

    if day < first_article_spain:
        return False
    if day in invalid_dates:
        return False
    return True