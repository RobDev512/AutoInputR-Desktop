import sys
from pathlib import Path


APP_NAME = "AutoInputR"
APP_VERSION = "1.3.0"


def get_app_dir():
    """
    Devuelve el directorio principal utilizado por AutoInputR.

    En desarrollo corresponde a la raiz del proyecto.
    En una version compilada corresponde a la carpeta del ejecutable.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


APP_DIR = get_app_dir()

DATA_DIR = APP_DIR / "data"
CONFIG_DIR = DATA_DIR
CONFIG_FILE = CONFIG_DIR / "config.json"

LEGACY_CONFIG_FILE = APP_DIR / "config.json"
LEGACY_TRACKER_TEMPLATE_FILE = APP_DIR / "tracker_template.png"


def get_resource_path(relative_path):
    """
    Resuelve un recurso tanto durante el desarrollo como dentro
    de una aplicacion empaquetada con PyInstaller.
    """
    local_path = APP_DIR / relative_path

    if local_path.exists():
        return local_path

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled_path = Path(sys._MEIPASS) / relative_path

        if bundled_path.exists():
            return bundled_path

    return local_path


LOGO_PATH = get_resource_path(
    "assets/branding/LogoAIR.png"
)

ICON_PATH = get_resource_path(
    "assets/branding/Logo2AIR.png"
)

ICON_ICO_PATH = get_resource_path(
    "assets/branding/Logo2AIR.ico"
)

TRACKER_TEMPLATE_FILE = (
    CONFIG_DIR / "tracker_template.png"
)


def migrate_legacy_local_files():
    """
    Mueve archivos locales de versiones anteriores desde la raiz
    hacia ``data/`` sin sobrescribir archivos ya migrados.
    """
    pairs = (
        (LEGACY_CONFIG_FILE, CONFIG_FILE),
        (LEGACY_TRACKER_TEMPLATE_FILE, TRACKER_TEMPLATE_FILE),
    )

    for legacy_path, new_path in pairs:
        if new_path.exists() or not legacy_path.exists():
            continue

        try:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            legacy_path.replace(new_path)
        except Exception:
            pass


migrate_legacy_local_files()
