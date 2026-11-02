"""
Ana pipeline:

- data/raw altındaki tüm modality klasörlerini dolaşır
- Her görüntüye:
    - HE
    - CLAHE
    - Adaptive Gamma
  uygular
- Çıktı görüntülerini results/images/... altına kaydeder
- MSE, PSNR, SSIM hesaplayıp results/metrics/metrics_all.csv dosyasına yazar
"""

from pathlib import Path
from typing import Dict, List
import traceback
import pandas as pd

from . import config
from . import utils
from . import enhancement_methods as em
from . import evaluation_metrics as evalm


# =============================================================================
# TEK BİR GÖRÜNTÜ + TEK YÖNTEM İŞLEME
# =============================================================================

def process_image_for_method(
    modality: str,
    img_path: Path,
    method: str
) -> Dict:
    """
    Bir görüntüye verilen iyileştirme yöntemini uygular, çıktıyı kaydeder,
    metrikleri hesaplar ve bir sonuç satırı döndürür.

    Adaptive gamma'nın gamma değerini ayrıca döndürür.
    """
    # Orijinal görüntü
    original = utils.load_image(img_path)

    gamma_used = None  # adaptive gamma için

    # --- Yöntemi uygula ---
    if method == "gamma_auto":
        enhanced, gamma_used = em.apply_adaptive_gamma(
            original,
            target_mean=config.ADAPTIVE_GAMMA_TARGET_MEAN
        )
    else:
        enhanced = em.apply_method(original, method=method)

    # --- Çıktı dosya yolu ---
    out_path = utils.build_output_image_path(
        input_path=img_path,
        modality=modality,
        method=method,
        gamma=gamma_used  # adaptif gamma için
    )
    utils.save_image(out_path, enhanced)

    # --- Metrikleri hesapla ---
    metrics = evalm.compute_all_metrics(original, enhanced)

    # --- Satır olarak döndür ---
    return {
        "modality": modality,
        "image_name": img_path.name,
        "method": method,
        "gamma": gamma_used,  # adaptive gamma değeri
        "output_path": str(out_path.relative_to(config.BASE_DIR)),
        "mse": metrics["mse"],
        "psnr": metrics["psnr"],
        "ssim": metrics["ssim"],
    }


# =============================================================================
# ANA PIPELINE
# =============================================================================

def run_pipeline() -> pd.DataFrame:
    """
    Tüm görüntülere HE, CLAHE ve Adaptive Gamma uygular.
    Metrikleri toplar, CSV’ye yazar ve DataFrame döndürür.
    """
    config.ensure_directories()

    all_rows: List[Dict] = []

    print("[INFO] Starting pipeline...")
    print(f"[INFO] Base dir: {config.BASE_DIR}")
    print(f"[INFO] Modalities: {config.MODALITIES}")
    print(f"[INFO] Methods: {config.METHODS}")

    for modality, img_path in utils.iter_modality_images():
        print(f"\n[INFO] Processing modality='{modality}', image='{img_path.name}'")

        for method in config.METHODS:
            try:
                print(f"  [METHOD] {method}")
                row = process_image_for_method(
                    modality=modality,
                    img_path=img_path,
                    method=method
                )
                all_rows.append(row)

            except Exception as e:
                print(f"[ERROR] Failed for {method} on {img_path.name}: {e}")
                traceback.print_exc()

    # === DataFrame oluştur ===
    df = pd.DataFrame(all_rows)

    # === CSV olarak kaydet ===
    metrics_csv_path = config.RESULTS_METRICS_DIR / "metrics_all.csv"
    metrics_csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(metrics_csv_path, index=False, float_format="%.6f")

    print(f"\n[INFO] Pipeline finished. Metrics saved to: {metrics_csv_path}")
    print(f"[INFO] Total processed rows: {len(df)}")

    return df


# =============================================================================
# MODÜL OLARAK ÇALIŞTIR
# =============================================================================

if __name__ == "__main__":
    run_pipeline()