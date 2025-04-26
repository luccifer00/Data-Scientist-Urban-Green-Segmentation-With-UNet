# scripts/city_config.py

CITIES_CONFIG = [
    {
        'name': 'Valencia',
        'location': [39.474862, -0.374908],
        'grid_size': 4,
        'utm_crs': 'EPSG:32630',
        'zoom': 14,
        'official_data': {
            'type': 'api',
            'url': 'https://valencia.opendatasoft.com/api/records/1.0/search',
            'params': {
                'dataset': 'espais-verds-espacios-verdes',
                'fields': 'nombre,barrio,superficie,geo_shape'
            },
            'geometry_path': ['fields', 'geo_shape']
        },
        'osm_area_id': 3600344953,
        'dates': [
            ('2023-06-01', '2023-06-30'),
            ('2020-06-01', '2020-06-30'),
            ('2017-06-01', '2017-06-30')
        ]
    },
    {
        'name': 'Madrid',
        'location': [40.421240, -3.684797],
        'grid_size': 5,
        'utm_crs': 'EPSG:32630',
        'zoom': 14,
        'official_data': {
            'type': 'wfs',
            'url': 'https://datos.madrid.es/egob/catalogo/212629-10515014-wfs-espacios-verdes.wfs',
            'layer': 'EspaciosVerdes'
        },
        'osm_area_id': 3605326784,
        'dates': [
            ('2023-06-01', '2023-06-30'),
            ('2018-06-01', '2018-06-30')
        ]
    },
    {
        'name': 'Barcelona',
        'location': [41.406815, 2.177353],
        'grid_size': 5,
        'utm_crs': 'EPSG:32631',
        'zoom': 14,
        'official_data': {
            'type': 'wfs',
            'url': 'https://www.idecity.barcelona.cat/geoserver/wfs',
            'layer': 'public:espais_verds'
        },
        'osm_area_id': 3600347950,
        'dates': [
            ('2023-06-01', '2023-06-30'),
            ('2019-06-01', '2019-06-30')
        ]
    },
    {
        'name': 'Sevilla',
        'location': [37.379843, -5.975189],
        'grid_size': 3,
        'utm_crs': 'EPSG:32630',
        'zoom': 14,
        'official_data': {
            'type': 'wfs',
            'url': 'https://www.sevilla.org/geoserver/wfs',
            'layer': 'zonas_verdes'
        },
        'osm_area_id': 3600342563,
        'dates': [
            ('2023-06-01', '2023-06-30')
        ]
    },
    {
        'name': 'Zaragoza',
        'location': [41.650405, -0.887060],
        'grid_size': 4,
        'utm_crs': 'EPSG:32630',
        'zoom': 14,
        'official_data': {
            'type': 'geojson',
            'url': 'https://www.zaragoza.es/geoserver/wfs?service=WFS&version=1.1.0&request=GetFeature&typeNames=espacios_verdes'
        },
        'osm_area_id': 3600345740,
        'dates': [
            ('2023-06-01', '2023-06-30'),
            ('2020-06-01', '2020-06-30')
        ]
    },
    {
        'name': 'Bilbao',
        'location': [43.261206, -2.937684],
        'grid_size': 3,
        'utm_crs': 'EPSG:32630',
        'zoom': 14,
        'official_data': {},
        'osm_area_id': 3600339549,
        'dates': [
            ('2023-06-01', '2023-06-30'),
            ('2021-06-01', '2021-06-30')
        ]
    },
    {
        'name': 'Málaga',
        'location': [36.714187, -4.445086],
        'grid_size': 4,
        'utm_crs': 'EPSG:32630',
        'zoom': 14,
        'official_data': {
            'type': 'api',
            'url': 'https://datosabiertos.malaga.eu/api/records/1.0/search/',
            'params': {'dataset': 'zonas-verdes'},
            'geometry_path': ['geometry']
        },
        'osm_area_id': 3600340746,
        'dates': [
            ('2023-06-01', '2023-06-30')
        ]
    },
    {
        'name': 'Vigo',
        'location': [42.231218, -8.722136],
        'grid_size': 3,
        'utm_crs': 'EPSG:32629',
        'zoom': 14,
        'official_data': {
            'type': 'api',
            'url': 'https://datos-ckan.vigo.org/api/3/action/package_show',
            'params': {'id': 'parques-e-xardins'},
            'geometry_path': ['geometry']
        },
        'osm_area_id': 3600341381,
        'dates': [
            ('2023-06-01', '2023-06-30')
        ]
    }
]



