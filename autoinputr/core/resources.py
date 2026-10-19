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

CONFIG_DIR = APP_DIR
CONFIG_FILE = CONFIG_DIR / "config.json"


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
