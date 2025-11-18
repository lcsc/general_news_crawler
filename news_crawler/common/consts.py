
provincias={
  'andalucia':[
    'sevilla',
    'malaga',
    'cadiz',
    'granada',
    'cordoba',
    'almeria',
    'jaen',
    'huelva',
  ],
  'aragon':[
    'zaragoza',
    'huesca',
    'teruel',
  ],
  'canarias':[
    'laspalmas',
    'santacruz',
  ],
  'cantabria':['cantabria'],
  'castillamancha':[
    'toledo',
    'ciudadreal',
    'albacete',
    'guadalajara',
    'cuenca',
  ],
  'castillaleon':[
    'valladolid',
    'leon',
    'burgos',
    'salamanca',
    'zamora',
    'segovia',
    'palencia',
    'avila',
    'soria',
  ],
  'catalunya':[
    'barcelona',
    'tarragona',
    'girona',
    'lleida',
  ],
  'ceutamelilla':[
    'ceuta',
    'melilla',
  ],
  'madrid':['madrid'],
  'navarra':['navarra'],
  'valencia':[
    'valencia',
    'alicante',
    'castellon',
  ],
  'extremadura':[
    'badajoz',
    'caceres',
  ],
  'galicia':[
    'lacoruña',
    'pontevedra',
    'lugo',
    'orense',
  ],
  'baleares':['baleares'],
  'rioja':['rioja'],
  'pvasco':[
    'vizcaya',
    'guipuzcoa',
    'alava',
  ],
  'asturias':['asturias'],
  'murcia':['murcia'],
}

ccaa = provincias.keys()

ccaa_geo_map={
'01':'andalucia', # COMUNIDAD AUTONOMA DE ANDALUCIA
'02':'aragon', # COMUNIDAD AUTONOMA DE ARAGON
'03':'asturias', # COMUNIDAD AUTONOMA DEL PRINCIPADO DE AST
'04':'baleares', # COMUNIDAD AUTONOMA DE LAS ILLES BALEARS
'05':'canarias', # COMUNIDAD AUTONOMA DE CANARIAS
'06':'cantabria', # COMUNIDAD AUTONOMA DE CANTABRIA
'07':'castillaleon', # COMUNIDAD DE CASTILLA Y LEON
'08':'castillamancha', # COMUNIDAD AUTONOMA DE CASTILLA-LA MANCHA
'09':'catalunya', # COMUNIDAD AUTONOMA DE CATALUÑA
'10':'valencia', # COMUNIDAD VALENCIANA
'11':'extremadura', # COMUNIDAD AUTONOMA DE EXTREMADURA
'12':'galicia', # COMUNIDAD AUTONOMA DE GALICIA
'13':'madrid', # COMUNIDAD DE MADRID
'14':'murcia', # COMUNIDAD AUTONOMA DE LA REGION DE MURCI
'15':'navarra', # COMUNIDAD FORAL DE NAVARRA
'16':'pvasco', # COMUNIDAD AUTONOMA DEL PAIS VASCO O DE E
'17':'rioja', # COMUNIDAD AUTONOMA DE LA RIOJA
'18':'ceutamelilla', # CIUDAD DE CEUTA
'19':'ceutamelilla', # CIUDAD DE MELILLA
}

ccaa_id_geo_map={
    '01':'andalucia', # COMUNIDAD AUTONOMA DE ANDALUCIA
'02':'aragon', # COMUNIDAD AUTONOMA DE ARAGON
'18':'asturias', # COMUNIDAD AUTONOMA DEL PRINCIPADO DE AST
'03':'baleares', # COMUNIDAD AUTONOMA DE LAS ILLES BALEARS
'04':'canarias', # COMUNIDAD AUTONOMA DE CANARIAS
'05':'cantabria', # COMUNIDAD AUTONOMA DE CANTABRIA
'07':'castillaleon', # COMUNIDAD DE CASTILLA Y LEON
'06':'castillamancha', # COMUNIDAD AUTONOMA DE CASTILLA-LA MANCHA
'08':'catalunya', # COMUNIDAD AUTONOMA DE CATALUÑA
'10':'extremadura', # COMUNIDAD AUTONOMA DE EXTREMADURA
'11':'galicia', # COMUNIDAD AUTONOMA DE GALICIA
'13':'madrid', # COMUNIDAD DE MADRID
'15':'murcia', # COMUNIDAD AUTONOMA DE LA REGION DE MURCI
'16':'navarra', # COMUNIDAD FORAL DE NAVARRA
'17':'pvasco', # COMUNIDAD AUTONOMA DEL PAIS VASCO O DE E
'12':'rioja', # COMUNIDAD AUTONOMA DE LA RIOJA
'19':'valencia', # COMUNIDAD VALENCIANA
'09':'ceutamelilla', # CIUDAD DE CEUTA
'14':'ceutamelilla', # CIUDAD DE MELILLA
}


prov_geo_map={
    '01':'alava', # Araba/Álava
'02':'albacete', # Albacete
'03':'alicante', # Alacant/Alicante
'04':'almeria', # Almería
'05':'avila', # Ávila
'06':'badajoz', # Badajoz
'07':'baleares', # Illes Balears
'08':'barcelona', # Barcelona
'09':'burgos', # Burgos
'10':'caceres', # Cáceres
'11':'cadiz', # Cádiz
'12':'castellon', # Castelló/Castellón
'13':'ciudadreal', # Ciudad Real
'14':'cordoba', # Córdoba
'15':'lacoruña', # A Coruña
'16':'cuenca', # Cuenca
'17':'girona', # Girona
'18':'granada', # Granada
'19':'guadalajara', # Guadalajara
'20':'guipuzcoa', # Gipuzkoa/Guipúzcoa
'21':'huelva', # Huelva
'22':'huesca', # Huesca
'23':'jaen', # Jaén
'24':'leon', # León
'25':'lleida', # Lleida
'26':'rioja', # La Rioja
'27':'lugo', # Lugo
'28':'madrid', # Madrid
'29':'malaga', # Málaga
'30':'murcia', # Murcia
'31':'navarra', # Navarra
'32':'orense', # Ourense
'33':'asturias', # Asturias
'34':'palencia', # Palencia
'35':'laspalmas', # Las Palmas
'36':'pontevedra', # Pontevedra
'37':'salamanca', # Salamanca
'38':'santacruz', # Santa Cruz De Tenerife
'39':'cantabria', # Cantabria
'40':'segovia', # Segovia
'41':'sevilla', # Sevilla
'42':'soria', # Soria
'43':'tarragona', # Tarragona
'44':'teruel', # Teruel
'45':'toledo', # Toledo
'46':'valencia', # València/Valencia
'47':'valladolid', # Valladolid
'48':'vizcaya', # Bizkaia/Vizcaya
'49':'zamora', # Zamora
'50':'zaragoza', # Zaragoza
'51':'ceuta', # Ceuta
'52':'melilla', # Melilla
}

# Minimo de articulos para considerar que el mes esta activo
month_thresold = 20

ENGINE_ID_bCube = "bCube"
ENGINE_ID_WordPress = "wordpress"
ENGINE_ID_Jomla = "Joomla"
ENGINE_ID_Drupal = "Drupal"
ENGINE_ID_OpenNemas = "OpenNemas"
ENGINE_ID_Blogger = "Blogger"
ENGINE_ID_Vocento = "Vocento"

SUBENGINE_ID_bc_PrensaIberica = "PrensaIberica"
SUBENGINE_ID_wp_json = "wp-json"
SUBENGINE_ID_vc_v22="v22"

engines = [ENGINE_ID_bCube,
           ENGINE_ID_WordPress,
           ENGINE_ID_Jomla,
           ENGINE_ID_Drupal,
           ENGINE_ID_OpenNemas,
           ENGINE_ID_Blogger,
           ENGINE_ID_Vocento
           ]

sub_engines = [SUBENGINE_ID_bc_PrensaIberica, SUBENGINE_ID_wp_json]

BfStatus_PENDING = "Pending"
BfStatus_OK = "OK"
BfStatus_ERROR = "ERROR"

DownloadStatus_OK = "ok"
DownloadStatus_NOT_FOUND = "not_found"