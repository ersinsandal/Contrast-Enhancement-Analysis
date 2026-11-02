"""
Değerlendirme Metrikleri:
- PSNR (Peak Signal-to-Noise Ratio)
- SSIM (Structural Similarity Index)
- MSE (Mean Squared Error)

Tüm fonksiyonlar 8-bit BGR veya GRAY görüntülerle çalışır.
Gerekirse görüntüleri gri seviyeye indirger.
"""

import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error


def _to_gray(img: np.ndarray) -> np.ndarray:
    """Görüntüyü gri seviyeye çevirir."""
    if len(img.shape) == 2 or img.shape[2] == 1:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# =============================================================================
# MSE
# =============================================================================

def compute_mse(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    MSE (Mean Squared Error) hesaplar.
    """
    gray1 = _to_gray(img1)
    gray2 = _to_gray(img2)

    return float(mean_squared_error(gray1, gray2))


# =============================================================================
# PSNR
# =============================================================================

def compute_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    PSNR hesaplar.
    """
    gray1 = _to_gray(img1)
    gray2 = _to_gray(img2)

    mse_val = mean_squared_error(gray1, gray2)
    if mse_val == 0:
        return float("inf")  # birebir aynı görüntü durumunda

    PIXEL_MAX = 255.0
    psnr = 20 * np.log10(PIXEL_MAX / np.sqrt(mse_val))
    return float(psnr)


# =============================================================================
# SSIM
# =============================================================================

def compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    SSIM hesaplar. (skimage üzerinden)
    
    SSIM = 1 → mükemmel benzerlik
    """
    gray1 = _to_gray(img1)
    gray2 = _to_gray(img2)

    value, _ = ssim(gray1, gray2, full=True)
    return float(value)


# =============================================================================
# TOPLU HESAPLAMA
# =============================================================================

def compute_all_metrics(img_original: np.ndarray, img_processed: np.ndarray) -> dict:
    """
    PSNR, SSIM, MSE'yi sözlük halinde döndürür.
    """

    return {
        "mse": compute_mse(img_original, img_processed),
        "psnr": compute_psnr(img_original, img_processed),
        "ssim": compute_ssim(img_original, img_processed)
    }
