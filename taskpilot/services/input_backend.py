"""
Backend de entrada compartido de TaskPilot.

Centraliza las operaciones de mouse que pueden utilizar
PyAutoGUI o PyDirectInput.

Por ahora conserva exactamente el comportamiento previo
del programa. Otros accesos directos a PyAutoGUI se
migraran de forma incremental.
"""

import pyautogui


try:
    import pydirectinput  # type: ignore

    pydirectinput.PAUSE = 0

    HAS_PYDIRECTINPUT = True

except Exception:
    pydirectinput = None
    HAS_PYDIRECTINPUT = False


class InputBackendMixin:
    def move_cursor_to(self, x, y):
        x = int(x)
        y = int(y)

        if self.input_backend == "pydirectinput" and HAS_PYDIRECTINPUT:
            pydirectinput.moveTo(x, y)
        else:
            pyautogui.moveTo(x, y, duration=0)

    def move_cursor_rel(self, dx, dy):
        dx = int(dx)
        dy = int(dy)

        if self.input_backend == "pydirectinput" and HAS_PYDIRECTINPUT:
            pydirectinput.moveRel(dx, dy)
        else:
            pyautogui.moveRel(dx, dy, duration=0)

    def click_mouse(self, x=None, y=None, button="left", clicks=1):
        if self.input_backend == "pydirectinput" and HAS_PYDIRECTINPUT:
            if x is not None and y is not None:
                pydirectinput.moveTo(int(x), int(y))

            for _ in range(max(1, int(clicks))):
                pydirectinput.click(button=button)

            return

        if x is None or y is None:
            pyautogui.click(button=button, clicks=clicks, interval=0)
        else:
            pyautogui.click(
                x=int(x),
                y=int(y),
                button=button,
                clicks=clicks,
                interval=0
            )
