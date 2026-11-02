"""
Histogram Plotting Pipeline
---------------------------

Bu dosya:
- data/raw içindeki tüm görüntüleri dolaşır
- Original, HE, CLAHE, Adaptive Gamma uygulanmış görüntülerin
  histogramlarını üretir
- Çıktıyı results/histograms/<modality>/<image>_<method>_hist.png
  altına kaydeder
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from . import utils
from . import enhancement_methods as em
from . import config

plt.style.use("ggplot")


# =============================================================================
# 1) Tek bir histogram çizme fonksiyonu
# =============================================================================

def plot_histogram(img: np.ndarray, title: str, save_path: Path):
    """
    Bir görüntünün gri histogramını çizer ve dosyaya kaydeder.
    """
    if img is None:
        raise ValueError("plot_histogram: input image is None")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()

    plt.figure(figsize=(6, 4))
    plt.plot(hist, color="black")
    plt.title(title)
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Pixel Count")
    plt.tight_layout()

    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(save_path), dpi=300)
    plt.close()


# =============================================================================
# 2) Tek bir görüntü için tüm histogramları üret
# =============================================================================

def process_histograms_for_image(modality: str, img_path: Path):
    """
    Bir görüntü için:
    - Original histogram
    - HE histogram
    - CLAHE histogram
    - Adaptive Gamma histogram
    üreterek kaydeder.
    """

    print(f"[INFO] Processing histograms for {modality}/{img_path.name}")

    # 1) Orijinal görüntü
    img = utils.load_image(img_path)

    plot_histogram(
        img,
        title=f"{modality} - {img_path.name} - ORIGINAL",
        save_path=config.RESULTS_DIR / "histograms" / modality / f"{img_path.stem}_orig_hist.png"
    )

    # 2) HE
    he_img = em.apply_histogram_equalization(img)
    plot_histogram(
        he_img,
        title=f"{modality} - {img_path.name} - HE",
        save_path=config.RESULTS_DIR / "histograms" / modality / f"{img_path.stem}_he_hist.png"
    )

    # 3) CLAHE
    clahe_img = em.apply_clahe(img)
    plot_histogram(
        clahe_img,
        title=f"{modality} - {img_path.name} - CLAHE",
        save_path=config.RESULTS_DIR / "histograms" / modality / f"{img_path.stem}_clahe_hist.png"
    )

    # 4) Adaptive Gamma
    gamma_img, gamma_val = em.apply_adaptive_gamma(img)
    plot_histogram(
        gamma_img,
        title=f"{modality} - {img_path.name} - Adaptive Gamma (γ={gamma_val:.3f})",
        save_path=config.RESULTS_DIR / "histograms" / modality / f"{img_path.stem}_gamma_hist.png"
    )

    print(f"[OK] Saved histograms for {modality}/{img_path.name}")


# =============================================================================
# 3) Tüm dataset için histogram pipeline
# =============================================================================

def run_histogram_pipeline():
    print("[INFO] Histogram pipeline starting...")

    for modality, img_path in utils.iter_modality_images():
        process_histograms_for_image(modality, img_path)

    print("[INFO] Histogram pipeline completed.")


# =============================================================================
# 4) Modül direkt çalıştırılırsa pipeline başlat
# =============================================================================

if __name__ == "__main__":
    run_histogram_pipeline()
