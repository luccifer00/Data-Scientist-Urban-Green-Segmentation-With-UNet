#scripts/valencia_config.py

from pyproj import Transformer

# ------------------------------------------------------------------
#  CONFIGURACIÓN GLOBAL DE VALENCIA PARA NOTEBOOKS Y APP
# -----------------------------------------------------------------
# Configuración global de Valencia para distintos notebooks y App
VALENCIA = {
    'name': 'Valencia',
    'utm_crs': 'EPSG:25830',       # UTM zona 30N ETRS89
    'wgs_crs': 'EPSG:4326',
    'center_wgs': (39.482365,-0.365038), 
    'center_utm': Transformer.from_crs('EPSG:4326','EPSG:25830',always_xy=True)
                   .transform(-0.374908,39.474862),
    'grid_size': 15,
    'pixel_size': 0.24,            # 24 cm/píxel
    'patch_pixels': 256,
    'pnoa_url': 'https://www.ign.es/wmts/pnoa-ma',
    'pnoa_layer': 'OI.OrthoimageCoverage',
    'tilematrixset': 'GoogleMapsCompatible',
    'osm_area_id': 3600344953,
    'zoom': 18,
    'zoom_start': 18
}
