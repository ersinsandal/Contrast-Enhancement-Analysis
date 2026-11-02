"""
Yardımcı fonksiyonlar:
- Görsel yükleme / kaydetme
- Modality klasörlerinden görüntü listeleme
- Çıktı dosya yollarını oluşturma
"""

from typing import List, Iterator, Tuple, Optional
from pathlib import Path
import cv2
import numpy as np

from . import config


# =============================================================================
# GÖRÜNTÜ YÜKLEME & KAYDETME
# =============================================================================

def load_image(path: Path) -> np.ndarray:
    """
    Verilen yoldan BGR formatında görüntü yükler.
    Hata durumunda ValueError fırlatır.
    """
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    return img


def save_image(path: Path, img: np.ndarray) -> None:
    """
    Görüntüyü verilen yola kaydeder. Gerekirse klasörleri oluşturur.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(str(path), img)
    if not success:
        raise IOError(f"Could not write image to: {path}")


# =============================================================================
# GÖRÜNTÜ LİSTELEME
# =============================================================================

def list_images_in_directory(directory: Path) -> List[Path]:
    """
    Bir dizindeki (alt klasörlere girmeden) tüm görüntü dosyalarını listeler.
    """
    if not directory.exists():
        return []

    files = [
        p for p in directory.iterdir()
        if p.is_file() and config.is_image_file(p)
    ]
    # Tutarlılık için isimlere göre sırala
    files.sort()
    return files


def iter_modality_images() -> Iterator[Tuple[str, Path]]:
    """
    Tüm modality klasörlerini dolaşır ve her görüntü için:
        (modality_name, image_path)
    şeklinde tuple döndürür.

    Örnek:
        for modality, img_path in iter_modality_images():
            ...
    """
    for modality, dir_path in config.MODALITY_DIRS.items():
        image_paths = list_images_in_directory(dir_path)
        for img_path in image_paths:
            yield modality, img_path


# =============================================================================
# ÇIKTI DOSYA ADLARI
# =============================================================================

def build_output_image_path(
    input_path: Path,
    modality: str,
    method: str,
    gamma: Optional[float] = None
) -> Path:
    """
    Girdi görüntüsüne, yönteme ve (varsa) gamma değerine göre
    çıktı dosya yolunu üretir.

    Örnek:
        input:  data/raw/low_light/low_light(1).png
        method: "clahe"
        modality: "low_light"
        -> results/images/clahe/low_light/low_light(1)_clahe.png

        method: "gamma", gamma=0.6
        -> results/images/gamma/low_light/low_light(1)_gamma_0.60.png
    """
    method = method.lower()
    if method not in config.RESULTS_IMAGES_METHOD_DIRS:
        raise ValueError(f"Unknown method: {method}")

    base_dir = config.RESULTS_IMAGES_METHOD_DIRS[method]

    # Modality alt klasörü
    out_dir = base_dir / modality
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem
    suffix = input_path.suffix.lower()

    if method == "gamma" and gamma is not None:
        filename = f"{stem}_gamma_{gamma:.2f}{suffix}"
    else:
        filename = f"{stem}_{method}{suffix}"

    return out_dir / filename