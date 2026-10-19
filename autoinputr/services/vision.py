"""Servicios de vision utilizados por el Rastreador de AutoInputR."""

from pathlib import Path

import cv2
import numpy as np


def capture_bgr_region(capture_session, left, top, width, height):
    """Captura una region con MSS y la devuelve en formato BGR."""
    monitor = {
        "left": int(left),
        "top": int(top),
        "width": int(width),
        "height": int(height),
    }
    shot = np.array(capture_session.grab(monitor))
    return cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)


def save_bgr_image(path, image):
    """Guarda una imagen BGR y devuelve True si OpenCV pudo escribirla."""
    return bool(cv2.imwrite(str(Path(path)), image))


def load_bgr_image(path):
    """Carga una imagen BGR o devuelve None si no puede leerse."""
    image = cv2.imread(str(Path(path)), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        return None
    return image


def match_template(screen, template):
    """Devuelve la mejor confianza y ubicacion para una plantilla."""
    result = cv2.matchTemplate(
        screen,
        template,
        cv2.TM_CCOEFF_NORMED,
    )
    _, max_value, _, max_location = cv2.minMaxLoc(result)
    return float(max_value), max_location
