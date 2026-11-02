import cv2
import numpy as np
from pathlib import Path

from . import config
from . import utils
from .enhancement_methods import (
    apply_histogram_equalization,
    apply_clahe,
    apply_adaptive_gamma
)


# =============================================================================
# Yardımcı: Görüntüyü hedef boyuta getir
# =============================================================================
def resize_to_match(img, target_size=(512, 512)):
    return cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)


# =============================================================================
# Yardımcı: Etiket yaz
# =============================================================================
def add_label(img, text):
    labeled = img.copy()
    cv2.rectangle(labeled, (0, 0), (img.shape[1], 40), (0, 0, 0), -1)
    cv2.putText(labeled, text, (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (255, 255, 255), 2, cv2.LINE_AA)
    return labeled


# =============================================================================
# Tek bir görüntü için kolaj oluştur
# =============================================================================
def create_collage_for_image(modality, img_path: Path):
    # Orijinal yükle
    original = utils.load_image(img_path)

    # Yöntemleri uygula
    he = apply_histogram_equalization(original)
    clahe = apply_clahe(original)
    gamma_img, gamma_used = apply_adaptive_gamma(original)

    # Boyut sabitle
    size = (512, 512)
    original_r = resize_to_match(original, size)
    he_r = resize_to_match(he, size)
    clahe_r = resize_to_match(clahe, size)
    gamma_r = resize_to_match(gamma_img, size)

    # Etiket ekle
    original_l = add_label(original_r, "Original")
    he_l = add_label(he_r, "HE")
    clahe_l = add_label(clahe_r, "CLAHE")

    gamma_label = f"Adaptive Gamma (γ={gamma_used:.2f})"
    gamma_l = add_label(gamma_r, gamma_label)

    # 2×2 grid oluştur
    top = np.hstack([original_l, he_l])
    bottom = np.hstack([clahe_l, gamma_l])
    collage = np.vstack([top, bottom])

    # Kayıt klasörü
    save_dir = config.RESULTS_COLLAGES_DIR / modality
    save_dir.mkdir(parents=True, exist_ok=True)

    out_path = save_dir / f"{img_path.stem}_collage.png"
    cv2.imwrite(str(out_path), collage)

    print(f"[INFO] Saved collage: {out_path}")


# =============================================================================
# Tüm modality klasörleri için kolaj üret
# =============================================================================
def run_collage_pipeline():
    print("[INFO] Starting collage generation...")

    for modality, img_path in utils.iter_modality_images():
        print(f"[INFO] Creating collage for: {modality}/{img_path.name}")
        create_collage_for_image(modality, img_path)

    print("[INFO] All collages generated!")


# =============================================================================
# Modül olarak çalıştır
# =============================================================================
if __name__ == "__main__":
    run_collage_pipeline()
