# scripts/utils.py

# ------------------------------------------------------------------
# FUNCIONES ÚTILES PARA APP.py
# ------------------------------------------------------------------
import rasterio, numpy as np, tensorflow as tf
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, jaccard_score

def list_tiles(raw_dir: Path):
    return sorted(raw_dir.glob("valencia_tile_*.jpg"))

def load_image(tile_jpg: Path, size=(256,256)):
    with rasterio.open(tile_jpg) as src:
        arr = src.read([1,2,3]).transpose(1,2,0).astype(np.float32)
    arr = tf.image.resize(arr, size).numpy() / 255.0
    return arr

def load_mask(tile_jpg: Path, proc_dir: Path, size=(256,256)):
    mask_tif = proc_dir / f"{tile_jpg.stem}_MASK.tif"
    with rasterio.open(mask_tif) as src:
        m = src.read(1).astype(np.uint8)
    m = tf.image.resize(m[...,None], size, method="nearest").numpy().squeeze().astype(int)
    return m

def predict_tile(model, img_small, orig_shape):
    pred_small = model.predict(img_small[None])[0,:,:,0]
    pred_full  = tf.image.resize(pred_small[...,None], orig_shape, method="bilinear")
    return pred_full.numpy().squeeze()

def compute_metrics(gt_small, pred_small, thr):
    # Añadir checks de forma
    if gt_small.shape != pred_small.shape:
        raise ValueError(f"Shapes don't match! GT: {gt_small.shape}, Pred: {pred_small.shape}")
    
    # Asegurar que son binarias
    y_true = gt_small.flatten().astype(int)
    y_pred = (pred_small.flatten() > thr).astype(int)
    
    # Debug: Mostrar conteo de clases
    print(f"[DEBUG] Class counts - GT: {np.unique(y_true, return_counts=True)}")
    print(f"[DEBUG] Class counts - Pred: {np.unique(y_pred, return_counts=True)}")
    
    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "iou": jaccard_score(y_true, y_pred, zero_division=0)
    }