# app/app.py

# ------------------------------------------------------------------
# 0. IMPORTS
# ------------------------------------------------------------------

import streamlit as st
from streamlit_folium import st_folium
import folium
import mercantile
import tensorflow as tf
from pathlib import Path
import sys
import geopandas as gpd
import rasterio
import numpy as np
import warnings
from rasterio.errors import NotGeoreferencedWarning
warnings.filterwarnings("ignore", category=NotGeoreferencedWarning)
warnings.filterwarnings(
    "ignore",
    message=".*use_column_width parameter has been deprecated.*",
    category=DeprecationWarning
)

# ------------------------------------------------------------------
# 1. PATHS Y CONFIGURACIÓN
# ------------------------------------------------------------------
APP_DIR    = Path(__file__).resolve().parent
ROOT       = APP_DIR.parent
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

from valencia_config import VALENCIA
from utils import list_tiles, load_image, load_mask, predict_tile, compute_metrics

st.set_page_config(page_title="GreenMask", page_icon="🌿", layout="wide")
st.title("🌿 GreenMask App – Segmentación de Zonas Verdes")
st.markdown("---")

# ------------------------------------------------------------------
# 2. LISTAR Y CARGAR MODELO 
# ------------------------------------------------------------------

st.sidebar.subheader("🧠 Modelos disponibles")
MODELS_DIR = ROOT / "models"
model_files = sorted(MODELS_DIR.glob("*.h5"), key=lambda x: "fold5" in x.name, reverse=True)
if not model_files:
    st.sidebar.error(f"No hay archivos .h5 en {MODELS_DIR}")
    st.stop()
model_opts = [f.name for f in model_files]
default_name = "Mejor_modelo_CV_en_fold1.h5"
if default_name in model_opts:
    default_index = model_opts.index(default_name)
else:
    default_index = 0
chosen = st.sidebar.selectbox("Selecciona modelo",model_opts,index=default_index)
MODEL_PATH = MODELS_DIR / chosen
st.sidebar.write(f"Cargando `{chosen}`…")
try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    st.sidebar.success("✅ Modelo cargado")
except Exception as e:
    st.sidebar.error(f"Error cargando modelo: {e}")
    st.stop()

#  Sidebar adicional
st.sidebar.title("⚙️ Configuración")
thr = st.sidebar.slider("Umbral de segmentación", 0.0, 1.0, 0.5, step=0.01)

# Cargar grid de teselas
tiles_gdf = gpd.read_file(ROOT / "data" / "raw" / "pnoa" / "valencia_tiles_grid.geojson")
tile_opts = [f"{int(r.x)}_{int(r.y)}_{int(r.z)}" for _, r in tiles_gdf.iterrows()]
default_tile = "130806_99737_18"

if "selected_tile" not in st.session_state:
    st.session_state.selected_tile = default_tile if default_tile in tile_opts else tile_opts[0]

sel = st.sidebar.selectbox(
    "Selecciona parche",
    tile_opts,
    index=tile_opts.index(st.session_state.selected_tile)
)
st.session_state.selected_tile = sel

# ------------------------------------------------------------------
# 3. MAPA PRINCIPAL
# ------------------------------------------------------------------

st.markdown("### 🌍 Mapa Interactivo de Valencia", help="Haz clic en cualquier cuadrado rojo para seleccionar un parche")
m = folium.Map(
    location=VALENCIA["center_wgs"],
    zoom_start=15,
    tiles=None,
    control_scale=True
)

# Capa base
folium.TileLayer(
    tiles=(
        f"{VALENCIA['pnoa_url']}?service=WMTS&request=GetTile&version=1.0.0&"
        f"layer={VALENCIA['pnoa_layer']}&style=default&format=image/jpeg&"
        f"TileMatrixSet={VALENCIA['tilematrixset']}&"
        "TileMatrix={z}&TileRow={y}&TileCol={x}"
    ),
    attr="IGN PNOA 25cm",
    name="Ortofoto",
    overlay=False
).add_to(m)

# Resaltado del tile/parche seleccionado
selected_tile_data = tiles_gdf[tiles_gdf.apply(
    lambda x: f"{int(x.x)}_{int(x.y)}_{int(x.z)}" == st.session_state.selected_tile, axis=1
)].to_json()

folium.GeoJson(
    selected_tile_data,
    style_function=lambda x: {
        "fillColor": "#ff0000",
        "color": "#ff0000",
        "weight": 3,
        "fillOpacity": 0.4,
        "opacity": 0.9
    },
    name="Tile seleccionado"
).add_to(m)

# Borde con efecto sombra
folium.GeoJson(
    selected_tile_data,
    style_function=lambda x: {
        "color": "#ffffff",
        "weight": 6,
        "opacity": 0.5
    },
    name="Sombra"
).add_to(m)

# Cuadrícula general
folium.GeoJson(
    tiles_gdf.to_json(),
    style_function=lambda x: {"color":"#ff0000","weight":1.5,"fillOpacity":0}
).add_to(m)

folium.LayerControl().add_to(m)

map_data = st_folium(m, width="100%", height=500, returned_objects=["last_clicked"])
if map_data.get("last_clicked"):
    lon, lat = map_data["last_clicked"]["lng"], map_data["last_clicked"]["lat"]
    t = mercantile.tile(lon, lat, VALENCIA["zoom"])
    key = f"{t.x}_{t.y}_{t.z}"
    if key in tile_opts and key != st.session_state.selected_tile:
        st.session_state.selected_tile = key
        st.rerun()

# ------------------------------------------------------------------
# 4. RESULTADOS DEL PARCHE SELECCIONADO
# ------------------------------------------------------------------
st.markdown("---")
st.markdown(f"### 📊 Resultados para: `{st.session_state.selected_tile}`")
sel = st.session_state.selected_tile
img_path  = ROOT / "data" / "raw" / "pnoa" / f"valencia_tile_{sel}.jpg"
mask_path = ROOT / "data" / "processed" / f"valencia_tile_{sel}_MASK.tif"

try:
    img_sm  = load_image(img_path, (256,256))
    gt_sm   = load_mask(img_path, ROOT/"data"/"processed", (256,256))
    pred_sm = model.predict(tf.expand_dims(img_sm, 0))[0,:,:,0]
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

with st.expander("🔍 Fuente de datos"):
    st.write(f"- Imagen: {img_sm.shape}")
    st.write(f"- Máscara: {gt_sm.shape}, valores: {np.unique(gt_sm)}")
    st.write(f"- Predicción: {pred_sm.shape}, rango: {pred_sm.min()}–{pred_sm.max()}")

cols = st.columns(4)
cols[0].image((img_sm*255).astype("uint8"), caption="Entrada RGB")
cols[1].image((gt_sm*255).astype("uint8"), caption="Máscara Real")
cols[2].image((pred_sm*255).astype("uint8"), caption="Predicción", clamp=True)
cols[3].image(((pred_sm>thr)*255).astype("uint8"), caption=f"Umbral {thr}")

try:
    metrics = compute_metrics(gt_sm, pred_sm, thr)
except Exception as e:
    st.error(f"Error calculando métricas: {e}")
    metrics = {"precision":0,"recall":0,"f1":0,"iou":0}

st.subheader("📈 Métricas de Rendimiento")
mcols = st.columns(4)
mcols[0].metric("Precisión", f"{metrics['precision']:.2f}",
                help="Porcentaje de predicciones positivas correctas")
mcols[1].metric("Recall",    f"{metrics['recall']:.2f}",
                help="Porcentaje de vegetación real detectada")
mcols[2].metric("F1 Score",  f"{metrics['f1']:.2f}",
                help="Balance entre Precisión y Recall")
mcols[3].metric("IoU",       f"{metrics['iou']:.2f}",
                help="Intersección sobre Unión con la máscara real")

# ------------------------------------------------------------------
# 4. FOOTER
# ------------------------------------------------------------------

st.divider()
footer = """
<div style="text-align: center; padding: 1rem 0; color: #666;">
  <small>
    🛠️ Desarrollado por 
    <a href="https://github.com/luccifer00" target="_blank" style="color: #2e86c1; text-decoration: none;">
      Fernando G.
    </a> 
    motivado por 
    <a href="https://greenurbandata.com/" target="_blank" style="color: #28b463; text-decoration: none; font-weight: bold;">
      Green Urban Data 🌳
    </a>
  </small>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)