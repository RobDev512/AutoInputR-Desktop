import json

from .resources import CONFIG_DIR, CONFIG_FILE


def load_config_file(config_file=CONFIG_FILE):
    """
    Carga la configuracion almacenada en JSON.

    Conserva el comportamiento historico de AutoInputR:
    si el archivo no existe o no puede leerse, devuelve un
    diccionario vacio.
    """
    try:
        if config_file.exists():
            with open(
                config_file,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)
    except Exception:
        pass

    return {}


def save_config_file(
    config,
    config_dir=CONFIG_DIR,
    config_file=CONFIG_FILE
):
    """
    Guarda la configuracion de AutoInputR en formato JSON.

    Devuelve True cuando el guardado termina correctamente
    y False si ocurre algun error.
    """
    try:
        config_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            config_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                config,
                file,
                indent=4
            )

        return True

    except Exception:
        return False
