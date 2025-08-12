
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