import os
from pathlib import Path

# =============================================================================
# PROJE TEMEL DİZİNLERİ
# =============================================================================

# Bu dosya src/ klasöründe, o yüzden proje kökü bir üst dizin
BASE_DIR = Path(__file__).resolve().parent.parent

# Veri klasörü
DATA_RAW_DIR = BASE_DIR / "data" / "raw"

# Sonuç klasörleri
RESULTS_DIR = BASE_DIR / "results"
RESULTS_IMAGES_DIR = RESULTS_DIR / "images"
RESULTS_METRICS_DIR = RESULTS_DIR / "metrics"
RESULTS_COLLAGES_DIR = RESULTS_DIR / "collages"

# Rapora özel klasörler
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_FIGURES_DIR = REPORTS_DIR / "figures"
REPORTS_TABLES_DIR = REPORTS_DIR / "tables"

# =============================================================================
# MODALITY (KATEGORİ) AYARLARI
# =============================================================================

MODALITIES = [
    "hdr",
    "high_contrast",
    "high_light",
    "low_contrast",
    "low_light",
    "medical",
    "microscopy",
    "natural",
]

# Her modality’nin raw klasörü
MODALITY_DIRS = {
    name: DATA_RAW_DIR / name for name in MODALITIES
}

# Akademik raporda kullanılacak "teorik olarak beklenen en iyi yöntem"
EXPECTED_BEST_METHOD = {
    "low_contrast": "he",
    "medical": "clahe",
    "microscopy": "clahe",
    "low_light": "clahe",
    "high_light": "gamma_auto",
    "high_contrast": "clahe",
    "natural": "gamma_auto",
    "hdr": "gamma_auto",
}

# =============================================================================
# GÖRÜNTÜ İŞLEME PARAMETRELERİ
# =============================================================================

# Artık üç yöntem var: HE, CLAHE, ADAPTIVE GAMMA
METHODS = ["he", "clahe", "gamma_auto"]

# CLAHE parametreleri
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Adaptive gamma hedef parlaklığı (0–1 arası)
ADAPTIVE_GAMMA_TARGET_MEAN = 0.5

# Aranacak gamma aralığı (0.3–2.5 arası iyidir)
ADAPTIVE_GAMMA_MIN = 0.3
ADAPTIVE_GAMMA_MAX = 2.5

# Desteklenen görsel uzantıları
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"]

# =============================================================================
# GÖRSEL ÇIKTI KLASÖRLERİ
# =============================================================================

RESULTS_IMAGES_METHOD_DIRS = {
    "he": RESULTS_IMAGES_DIR / "he",
    "clahe": RESULTS_IMAGES_DIR / "clahe",
    "gamma_auto": RESULTS_IMAGES_DIR / "gamma_auto",
}

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def is_image_file(path: Path) -> bool:
    """Desteklenen uzantılarla bitip bitmediğini kontrol eder."""
    return path.suffix.lower() in IMAGE_EXTENSIONS


def ensure_directories() -> None:
    """Tüm gerekli klasörleri oluşturur."""
    # Sonuç klasörleri
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_METRICS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_COLLAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Yönteme göre çıktı klasörleri
    for p in RESULTS_IMAGES_METHOD_DIRS.values():
        p.mkdir(parents=True, exist_ok=True)

    # Rapor klasörleri
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Modality klasörleri kontrolü
    for name, p in MODALITY_DIRS.items():
        if not p.exists():
            print(f"[WARN] Modality folder does not exist: {p}")


if __name__ == "__main__":
    print(f"[INFO] Base dir: {BASE_DIR}")
    ensure_directories()
    print("[INFO] Directory check done.")