"""
Enhancement methods:
- Histogram Equalization (HE)
- CLAHE
- Adaptive Gamma Correction (PURE GLOBAL BPAGC)

Tüm fonksiyonlar BGR formatındaki görüntü alır (cv2.imread)
ve yine BGR görüntü döndürür.
"""

from typing import Tuple
import numpy as np
import cv2

from . import config


# =============================================================================
# Yardımcı Fonksiyonlar
# =============================================================================

def _to_gray(img: np.ndarray) -> np.ndarray:
    """Girdiyi tek kanallı gri seviyeye çevirir."""
    if img is None:
        raise ValueError("_to_gray: input image is None")

    if len(img.shape) == 2 or img.shape[2] == 1:
        return img.copy()

    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _from_gray_to_bgr(gray: np.ndarray) -> np.ndarray:
    """Gri seviye görüntüyü BGR formatına genişletir."""
    if gray is None:
        raise ValueError("_from_gray_to_bgr: input image is None")

    if len(gray.shape) == 2:
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    return gray


# =============================================================================
# 1) HISTOGRAM EQUALIZATION (HE)
# =============================================================================

def apply_histogram_equalization(img: np.ndarray) -> np.ndarray:
    """
    Histogram Equalization uygular.
    Gri görüntüde direkt HE,
    renkli görüntüde YCrCb->Y kanalına HE->geri dönüş.
    """
    if img is None:
        raise ValueError("apply_histogram_equalization: input image is None")

    # Gri görüntü
    if len(img.shape) == 2 or img.shape[2] == 1:
        gray = _to_gray(img)
        he = cv2.equalizeHist(gray)
        return _from_gray_to_bgr(he)

    # Renkli görüntü
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)

    y_eq = cv2.equalizeHist(y)
    ycrcb_eq = cv2.merge([y_eq, cr, cb])

    return cv2.cvtColor(ycrcb_eq, cv2.COLOR_YCrCb2BGR)


# =============================================================================
# 2) CLAHE
# =============================================================================

def _create_clahe():
    """Config'teki parametrelere göre CLAHE objesi oluşturur."""
    return cv2.createCLAHE(
        clipLimit=config.CLAHE_CLIP_LIMIT,
        tileGridSize=config.CLAHE_TILE_GRID_SIZE
    )


def apply_clahe(img: np.ndarray) -> np.ndarray:
    """
    CLAHE uygular.
    Gri görüntüde direkt, renkli görüntüde Y kanalına CLAHE uygulanır.
    """
    if img is None:
        raise ValueError("apply_clahe: input image is None")

    clahe = _create_clahe()

    if len(img.shape) == 2 or img.shape[2] == 1:
        gray = _to_gray(img)
        cl = clahe.apply(gray)
        return _from_gray_to_bgr(cl)

    # Renkli görüntü
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)

    y_clahe = clahe.apply(y)
    ycrcb_cl = cv2.merge([y_clahe, cr, cb])

    return cv2.cvtColor(ycrcb_cl, cv2.COLOR_YCrCb2BGR)


# =============================================================================
# 3) PURE ADAPTIVE GAMMA CORRECTION (BPAGC)
# =============================================================================

def apply_gamma_correction(img: np.ndarray, gamma: float) -> np.ndarray:
    """Standart global gamma correction uygular."""
    if img is None:
        raise ValueError("apply_gamma_correction: input image is None")
    if gamma <= 0:
        raise ValueError("gamma must be > 0")

    img_f = img.astype(np.float32) / 255.0
    corrected = np.power(img_f, gamma)
    return np.clip(corrected * 255.0, 0, 255).astype(np.uint8)


def estimate_gamma_pure(
    img_bgr: np.ndarray,
    target_mean: float = 0.5,
    gamma_min: float = 0.3,
    gamma_max: float = 3.0
) -> float:
    """
    SAF / ORİJİNAL ADAPTIVE GAMMA (BPAGC benzeri global model):

        gamma = log(target_mean) / log(current_mean)

    - current_mean: görüntünün ortalama parlaklığı (0-1 arası)
    - target_mean: ideal parlaklık seviyesi (genelde 0.5 civarı)

    Açıklama:
        * current_mean < target_mean  -->  0 < gamma < 1  (görüntüyü aydınlatır)
        * current_mean > target_mean  -->  gamma > 1      (görüntüyü koyulaştırır)

    Bu fonksiyon hiçbir ek heuristic kullanmaz; tamamen
    global parlaklık ortalamasına dayalıdır.
    """
    gray = _to_gray(img_bgr).astype(np.float32) / 255.0

    current_mean = float(gray.mean())

    # Güvenlik önlemi: log(0) ve log(1)'den kaçınmak için
    eps = 1e-6
    current_mean = float(np.clip(current_mean, eps, 1.0 - eps))
    target_mean = float(np.clip(target_mean, eps, 1.0 - eps))

    # BPAGC formülü
    gamma = float(np.log(target_mean) / np.log(current_mean))

    # Uç değerleri kırp
    gamma = float(np.clip(gamma, gamma_min, gamma_max))
    return gamma


def apply_adaptive_gamma(img: np.ndarray, target_mean: float = 0.5) -> Tuple[np.ndarray, float]:
    """
    PURE GLOBAL ADAPTIVE GAMMA (BPAGC):

    1) current_mean hesaplanır
    2) gamma = log(target_mean) / log(current_mean)
    3) Gamma correction uygulanır

    Dönen:
        (iyileştirilmiş_görüntü, kullanılan_gamma)
    """
    if img is None:
        raise ValueError("apply_adaptive_gamma: input image is None")

    gamma = estimate_gamma_pure(
        img_bgr=img,
        target_mean=target_mean,
        gamma_min=config.ADAPTIVE_GAMMA_MIN,
        gamma_max=config.ADAPTIVE_GAMMA_MAX,
    )

    corrected = apply_gamma_correction(img, gamma)
    return corrected, gamma


# =============================================================================
# 4) METHOD ROUTER
# =============================================================================

def apply_method(
    img: np.ndarray,
    method: str,
    gamma: float | None = None,
    target_mean: float = 0.5
) -> np.ndarray:
    """
    Verilen yönteme göre iyileştirme uygular.

    method:
        - "he"
        - "clahe"
        - "gamma_auto" / "adaptive_gamma" / "gamma"
          (hepsi saf global adaptive gamma olarak yorumlanır)
    """
    if img is None:
        raise ValueError("apply_method: input image is None")

    method = method.lower()

    if method == "he":
        return apply_histogram_equalization(img)

    elif method == "clahe":
        return apply_clahe(img)

    elif method in ("gamma_auto", "adaptive_gamma", "gamma"):
        corrected, gamma_used = apply_adaptive_gamma(
            img,
            target_mean=target_mean
        )
        # gamma_used istersen pipeline tarafında loglanabilir
        return corrected

    else:
        raise ValueError(f"Unknown method: {method}")
