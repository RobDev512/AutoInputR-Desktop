import shutil
import sys
from pathlib import Path


APP_NAME = "TaskPilot"
APP_VERSION = "1.4.0-dev"
LEGACY_APP_NAME = "AutoInputR"


def get_app_dir():
    """
    Devuelve el directorio principal utilizado por TaskPilot.

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

# Archivos legados dentro de la misma carpeta de ejecucion.
LEGACY_CONFIG_FILE = APP_DIR / "config.json"
LEGACY_TRACKER_TEMPLATE_FILE = APP_DIR / "tracker_template.png"

# AutoInputR fue el nombre publico hasta v1.3.0. Para instalaciones nuevas de
# TaskPilot se conserva una ruta de compatibilidad con la instalacion anterior.
LEGACY_PRODUCT_DIR = APP_DIR.parent / LEGACY_APP_NAME
LEGACY_PRODUCT_DATA_DIR = LEGACY_PRODUCT_DIR / "data"
LEGACY_PRODUCT_CONFIG_FILE = LEGACY_PRODUCT_DATA_DIR / "config.json"
LEGACY_PRODUCT_ROOT_CONFIG_FILE = LEGACY_PRODUCT_DIR / "config.json"
LEGACY_PRODUCT_TRACKER_TEMPLATE_FILE = (
    LEGACY_PRODUCT_DATA_DIR / "tracker_template.png"
)
LEGACY_PRODUCT_ROOT_TRACKER_TEMPLATE_FILE = (
    LEGACY_PRODUCT_DIR / "tracker_template.png"
)


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
    "assets/branding/TaskPilotLogo.png"
)

LOGO_HORIZONTAL_PATH = get_resource_path(
    "assets/branding/TaskPilotLogoHorizontal.png"
)

LOGO_TRANSPARENT_PATH = get_resource_path(
    "assets/branding/TaskPilotLogoTransparent.png"
)

MONO_LOGO_PATH = get_resource_path(
    "assets/branding/TaskPilotMono.png"
)

ICON_PATH = get_resource_path(
    "assets/branding/TaskPilotIcon.png"
)

ICON_ICO_PATH = get_resource_path(
    "assets/branding/TaskPilotIcon.ico"
)

TRACKER_TEMPLATE_FILE = (
    CONFIG_DIR / "tracker_template.png"
)


def migrate_legacy_local_files():
    """
    Mueve archivos locales legados desde la raiz de ejecucion hacia ``data/``
    sin sobrescribir archivos ya migrados.
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


def migrate_legacy_product_files():
    """
    Copia configuracion y plantilla desde una instalacion anterior de
    AutoInputR cuando TaskPilot se ejecuta como una instalacion nueva.

    Se copia en lugar de mover para no inutilizar la instalacion anterior.
    """
    candidate_groups = (
        (
            (
                LEGACY_PRODUCT_CONFIG_FILE,
                LEGACY_PRODUCT_ROOT_CONFIG_FILE,
            ),
            CONFIG_FILE,
        ),
        (
            (
                LEGACY_PRODUCT_TRACKER_TEMPLATE_FILE,
                LEGACY_PRODUCT_ROOT_TRACKER_TEMPLATE_FILE,
            ),
            TRACKER_TEMPLATE_FILE,
        ),
    )

    for candidates, destination in candidate_groups:
        if destination.exists():
            continue

        for source in candidates:
            if not source.exists() or source == destination:
                continue

            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                break
            except Exception:
                continue


migrate_legacy_local_files()
migrate_legacy_product_files()
