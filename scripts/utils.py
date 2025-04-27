# scripts/utils.py

# ------------------------------------------------------------------
# FUNCIONES ÚTILES PARA APP.py
# ------------------------------------------------------------------
import rasterio
import numpy as np
import tensorflow as tf
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, jaccard_score


def compute_exg_np(img: np.ndarray) -> np.ndarray:
    """
    Calcula el índice ExG para una imagen RGB normalizada (valores en [0,1]).
    Devuelve un array HxWx1 con ExG normalizado.
    """
    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]
    exg = 2 * G - R - B
    exg_min = exg.min()
    exg_max = exg.max()
    return ((exg - exg_min) / (exg_max - exg_min + 1e-6))[..., None]


def list_tiles(raw_dir: Path):
    return sorted(raw_dir.glob("valencia_tile_*.jpg"))


def load_image(tile_jpg: Path, size=(256, 256)) -> np.ndarray:
    """
    Carga una imagen RGB desde disk, la redimensiona y normaliza,
    calcula ExG y retorna un array HxWx4.
    """
    # Leer canales RGB
    with rasterio.open(tile_jpg) as src:
        arr = src.read([1, 2, 3]).transpose(1, 2, 0).astype(np.float32)
    # Redimensionar y normalizar
    arr = tf.image.resize(arr, size).numpy() / 255.0
    # Calcular ExG y concatenar
    exg = compute_exg_np(arr)
    return np.concatenate([arr, exg], axis=-1)


def load_mask(tile_jpg: Path, proc_dir: Path, size=(256, 256)) -> np.ndarray:
    mask_tif = proc_dir / f"{tile_jpg.stem}_MASK.tif"
    with rasterio.open(mask_tif) as src:
        m = src.read(1).astype(np.uint8)
    m = tf.image.resize(m[..., None], size, method="nearest").numpy().squeeze().astype(int)
    return m


def predict_tile(model, img_small: np.ndarray, orig_shape) -> np.ndarray:
    pred_small = model.predict(img_small[None])[0, :, :, 0]
    pred_full = tf.image.resize(pred_small[..., None], orig_shape, method="bilinear")
    return pred_full.numpy().squeeze()


def compute_metrics(gt_small: np.ndarray, pred_small: np.ndarray, thr: float) -> dict:
    if gt_small.shape != pred_small.shape:
        raise ValueError(f"Shapes don't match! GT: {gt_small.shape}, Pred: {pred_small.shape}")

    y_true = gt_small.flatten().astype(int)
    y_pred = (pred_small.flatten() > thr).astype(int)

    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "iou": jaccard_score(y_true, y_pred, zero_division=0)
    }