"""
Modulo Ruta de TaskPilot.

Agrupa la interfaz, grabacion, HUD, reproduccion y hotkeys
especificas de las rutas del cursor.
"""

import ctypes
import ctypes.wintypes
import sys
import threading
import time
import tkinter as tk

import customtkinter as ctk
import pyautogui
from pynput import keyboard, mouse


class RutaMixin:
    def create_route_section(self, parent):
        info_frame = ctk.CTkFrame(parent, corner_radius=14)
        info_frame.pack(padx=12, pady=(4, 4), fill="x")

        title = ctk.CTkLabel(
            info_frame,
            text="Ruta del cursor",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        title.pack(anchor="w", padx=14, pady=(10, 4))

        self.route_description_label = ctk.CTkLabel(
            info_frame,
            text=self.get_route_description_text(),
            text_color="#a6adc8",
            font=ctk.CTkFont(size=12),
            wraplength=500,
            justify="left"
        )
        self.route_description_label.pack(anchor="w", padx=14, pady=(0, 8))

        self.route_info_label = ctk.CTkLabel(
            info_frame,
            text=self.get_route_summary(),
            text_color="#a6adc8",
            justify="left"
        )
        self.route_info_label.pack(anchor="w", padx=14, pady=(0, 12))

        speed_frame = ctk.CTkFrame(parent, corner_radius=14)
        speed_frame.pack(padx=12, pady=6, fill="x")

        speed_title = ctk.CTkLabel(
            speed_frame,
            text="Velocidad de reproducción",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        speed_title.pack(anchor="w", padx=14, pady=(10, 4))

        speed_row = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_row.pack(padx=14, pady=(4, 12), fill="x")

        self.route_speed_label = ctk.CTkLabel(
            speed_row,
            text=f"x{self.route_speed_multiplier}",
            text_color="#a6e3a1",
            width=50
        )
        self.route_speed_label.pack(side="right", padx=(12, 0))

        self.route_speed_slider = ctk.CTkSlider(
            speed_row,
            from_=1,
            to=1000,
            number_of_steps=999,
            command=self.change_route_speed
        )
        self.route_speed_slider.pack(side="left", fill="x", expand=True)
        self.route_speed_slider.set(self.route_speed_multiplier)

        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(padx=12, pady=(8, 2), fill="x")

        route_actions_row = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        route_actions_row.grid(row=0, column=0, columnspan=2, pady=4, sticky="ew")

        self.record_route_button = ctk.CTkButton(
            route_actions_row,
            text="●",
            width=48,
            height=42,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.open_route_recorder
        )
        self.record_route_button.pack(side="left", padx=(0, 8))

        self.record_route_game_button = ctk.CTkButton(
            route_actions_row,
            text="● ▶",
            width=64,
            height=42,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.open_route_game_recorder
        )
        self.record_route_game_button.pack(side="left", padx=(0, 8))

        self.clear_route_button = ctk.CTkButton(
            route_actions_row,
            text="🧹 Limpiar ruta",
            height=42,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.clear_route
        )
        self.clear_route_button.pack(side="left", fill="x", expand=True)

        self.start_route_button = ctk.CTkButton(
            buttons_frame,
            text=f"Iniciar ({self.route_hotkey.upper()})",
            height=42,
            command=self.start_route
        )
        self.start_route_button.grid(row=1, column=0, padx=(0, 8), pady=4, sticky="ew")

        self.stop_route_button = ctk.CTkButton(
            buttons_frame,
            text=f"Detener ({self.route_hotkey.upper()})",
            height=42,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.stop_route
        )
        self.stop_route_button.grid(row=1, column=1, padx=(8, 0), pady=4, sticky="ew")

        self.route_hotkey_button = ctk.CTkButton(
            buttons_frame,
            text="Configuración de hotkey",
            height=42,
            command=self.open_route_hotkey_window
        )
        self.route_hotkey_button.grid(row=2, column=0, columnspan=2, pady=4, sticky="ew")

        self.route_hotkey_button.bind("<Return>", lambda event: "break")
        self.route_hotkey_button.bind("<space>", lambda event: "break")
        self.route_hotkey_button.bind("<KP_Enter>", lambda event: "break")
        self.route_hotkey_button.bind("<KeyPress>", lambda event: "break")

        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        status_row = ctk.CTkFrame(parent, fg_color="transparent")
        status_row.pack(padx=12, pady=(26, 0), fill="x")

        self.route_play_speed_label = ctk.CTkLabel(
            status_row,
            text="Velocidad: 0 pasos/s",
            text_color="#a6adc8"
        )
        self.route_play_speed_label.pack(side="right", padx=(12, 0))

        self.route_status_label = ctk.CTkLabel(
            status_row,
            text="Estado: Ruta detenida",
            text_color="#a6adc8"
        )
        self.route_status_label.pack(side="right")

    def get_route_click_count(self):
        return sum(
            1
            for event in self.route_events
            if isinstance(event, dict) and event.get("type") == "click"
        )

    def get_route_move_count(self):
        return sum(
            1
            for event in self.route_events
            if isinstance(event, dict) and event.get("type") == "move"
        )

    def get_route_description_text(self):
        record_key = self.get_key_display(self.route_record_key)

        return (
            "Prepara una grabación, mueve el cursor al punto inicial\n"
            f"y presiona {record_key} para empezar o pausar.\n"
            "Los clicks que hagas durante la grabación también se guardan."
        )

    def get_route_summary(self):
        move_count = self.get_route_move_count()
        click_count = self.get_route_click_count()

        if move_count == 0 and click_count == 0:
            return "Ruta no grabada"

        return f"{move_count} puntos de movimiento · {click_count} clicks registrados"

    def update_route_status(self, text, color="#a6adc8"):
        if self.route_status_label is not None:
            self.route_status_label.configure(
                text=text,
                text_color=color
            )

    def update_route_play_speed_label(self, speed):
        self.route_current_speed = speed

        if self.route_play_speed_label is not None:
            self.route_play_speed_label.configure(
                text=f"Velocidad: {speed} pasos/s"
            )

    def update_route_labels(self):
        if self.route_description_label is not None:
            self.route_description_label.configure(
                text=self.get_route_description_text()
            )

        if self.route_info_label is not None:
            self.route_info_label.configure(
                text=self.get_route_summary(),
                text_color="#a6e3a1" if self.route_events else "#a6adc8"
            )

        if self.route_speed_label is not None:
            self.route_speed_label.configure(
                text=f"x{self.route_speed_multiplier}"
            )

        if self.start_route_button is not None:
            self.start_route_button.configure(
                text=f"Iniciar ({self.route_hotkey.upper()})"
            )

        if self.stop_route_button is not None:
            self.stop_route_button.configure(
                text=f"Detener ({self.route_hotkey.upper()})"
            )

    def change_route_speed(self, value):
        self.route_speed_multiplier = int(round(float(value)))
        self.route_speed_multiplier = max(1, min(1000, self.route_speed_multiplier))

        if self.route_speed_label is not None:
            self.route_speed_label.configure(
                text=f"x{self.route_speed_multiplier}"
            )

        self.save_config()

    def normalize_pynput_key(self, key):
        if isinstance(key, keyboard.KeyCode):
            return key.char.lower() if key.char else ""

        return str(key).replace("Key.", "").lower()

    def stop_route_game_listeners(self):
        try:
            if self.route_game_mouse_listener is not None:
                self.route_game_mouse_listener.stop()
        except Exception:
            pass

        try:
            if self.route_game_keyboard_listener is not None:
                self.route_game_keyboard_listener.stop()
        except Exception:
            pass

        self.route_game_mouse_listener = None
        self.route_game_keyboard_listener = None
        self.route_game_recording_active = False

    def make_window_click_through(self, window, transparent_color="#ff00ff"):
        if sys.platform != "win32":
            return

        try:
            window.update_idletasks()
            window.update()

            hwnd = window.winfo_id()

            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000
            LWA_COLORKEY = 0x00000001

            user32 = ctypes.windll.user32

            current_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

            new_style = (
                current_style
                | WS_EX_LAYERED
                | WS_EX_TRANSPARENT
                | WS_EX_TOOLWINDOW
                | WS_EX_NOACTIVATE
            )

            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)

            color_map = {
                "#ff00ff": 0x00FF00FF,
                "#010203": 0x00030201
            }

            color_key = color_map.get(transparent_color.lower(), 0x00FF00FF)

            user32.SetLayeredWindowAttributes(
                hwnd,
                color_key,
                0,
                LWA_COLORKEY
            )

        except Exception:
            pass

    def get_work_area_rect(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if sys.platform != "win32":
            return 0, 0, screen_width, screen_height

        try:
            rect = ctypes.wintypes.RECT()
            SPI_GETWORKAREA = 48

            ok = ctypes.windll.user32.SystemParametersInfoW(
                SPI_GETWORKAREA,
                0,
                ctypes.byref(rect),
                0
            )

            if ok:
                return rect.left, rect.top, rect.right, rect.bottom

        except Exception:
            pass

        return 0, 0, screen_width, screen_height

    def open_route_game_hud(self, text):
        self.close_route_game_hud()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.route_game_hud_windows = []

        transparent_color = "#ff00ff"

        def prepare_hud_window(window, x, y, width, height):
            window.withdraw()
            window.overrideredirect(True)
            window.attributes("-topmost", True)
            window.configure(bg=transparent_color)
            window.geometry(f"{width}x{height}+{x}+{y}")

            try:
                window.attributes("-transparentcolor", transparent_color)
            except Exception:
                pass

            window.update_idletasks()
            window.update()

            self.make_window_click_through(window, transparent_color)

            self.route_game_hud_windows.append(window)

            try:
                window.deiconify()
                window.lift()
            except Exception:
                pass

        # Texto superior, sin fullscreen
        text_width = 720
        text_height = 42
        text_x = max(0, (screen_width - text_width) // 2)
        text_y = 30

        text_window = tk.Toplevel(self)
        self.route_game_hud_window = text_window

        prepare_hud_window(
            text_window,
            text_x,
            text_y,
            text_width,
            text_height
        )

        text_canvas = tk.Canvas(
            text_window,
            bg=transparent_color,
            highlightthickness=0,
            bd=0
        )
        text_canvas.pack(fill="both", expand=True)

        text_canvas.create_rectangle(
            2,
            2,
            text_width - 2,
            text_height - 2,
            fill="#11111b",
            outline="#cdd6f4",
            width=1
        )

        self.route_game_hud_canvas = text_canvas

        self.route_game_hud_shadow = text_canvas.create_text(
            text_width // 2 + 1,
            text_height // 2 + 1,
            text=text,
            fill="#000000",
            font=("Segoe UI", 13, "bold")
        )

        self.route_game_hud_text = text_canvas.create_text(
            text_width // 2,
            text_height // 2,
            text=text,
            fill="white",
            font=("Segoe UI", 13, "bold")
        )

        # Esquinas separadas, para evitar cuadros blancos fullscreen
        corner_size = 78
        margin_x = 28
        top_margin = 82
        bottom_margin = 82
        line_length = 44
        line_width = 3
        color = "white"

        corner_positions = [
            ("tl", margin_x, top_margin),
            ("tr", screen_width - margin_x - corner_size, top_margin),
            ("bl", margin_x, screen_height - bottom_margin - corner_size),
            ("br", screen_width - margin_x - corner_size, screen_height - bottom_margin - corner_size)
        ]

        for corner, x, y in corner_positions:
            corner_window = tk.Toplevel(self)

            prepare_hud_window(
                corner_window,
                x,
                y,
                corner_size,
                corner_size
            )

            canvas = tk.Canvas(
                corner_window,
                bg=transparent_color,
                highlightthickness=0,
                bd=0
            )
            canvas.pack(fill="both", expand=True)

            if corner == "tl":
                canvas.create_line(2, 2, line_length, 2, fill=color, width=line_width)
                canvas.create_line(2, 2, 2, line_length, fill=color, width=line_width)

            elif corner == "tr":
                canvas.create_line(corner_size - 2, 2, corner_size - line_length, 2, fill=color, width=line_width)
                canvas.create_line(corner_size - 2, 2, corner_size - 2, line_length, fill=color, width=line_width)

            elif corner == "bl":
                canvas.create_line(2, corner_size - 2, line_length, corner_size - 2, fill=color, width=line_width)
                canvas.create_line(2, corner_size - 2, 2, corner_size - line_length, fill=color, width=line_width)

            elif corner == "br":
                canvas.create_line(corner_size - 2, corner_size - 2, corner_size - line_length, corner_size - 2, fill=color, width=line_width)
                canvas.create_line(corner_size - 2, corner_size - 2, corner_size - 2, corner_size - line_length, fill=color, width=line_width)

        self.after(100, self.raise_route_game_hud)
        self.after(500, self.raise_route_game_hud)

    def raise_route_game_hud(self):
        try:
            if self.route_game_hud_window is not None:
                if self.route_game_hud_window.winfo_exists():
                    self.route_game_hud_window.attributes("-topmost", True)
                    self.route_game_hud_window.lift()
        except Exception:
            pass

        try:
            for window in self.route_game_hud_windows:
                if window is not None and window.winfo_exists():
                    window.attributes("-topmost", True)
                    window.lift()
        except Exception:
            pass

    def update_route_game_hud(self, text, color="white"):
        try:
            if self.route_game_hud_canvas is None:
                return

            if self.route_game_hud_text is None:
                return

            self.route_game_hud_canvas.itemconfig(
                self.route_game_hud_text,
                text=text,
                fill=color
            )

            if self.route_game_hud_shadow is not None:
                self.route_game_hud_canvas.itemconfig(
                    self.route_game_hud_shadow,
                    text=text
                )

            self.raise_route_game_hud()

        except Exception:
            pass

    def close_route_game_hud(self):
        try:
            for window in self.route_game_hud_windows:
                try:
                    if window is not None and window.winfo_exists():
                        window.destroy()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            if self.route_game_hud_window is not None:
                self.route_game_hud_window.destroy()
        except Exception:
            pass

        self.route_game_hud_windows = []
        self.route_game_hud_window = None
        self.route_game_hud_canvas = None
        self.route_game_hud_text = None
        self.route_game_hud_shadow = None
        self.route_game_hud_bg = None

    def open_route_game_recorder(self):
        self.stop_route()

        if self.route_recorder_open:
            self.update_route_status("Estado: Ya hay una grabación abierta", "#f9e2af")
            return

        self.route_recorder_open = True
        self.route_game_recording_active = False

        record_key_text = self.get_key_display(self.route_record_key)

        local_events = []
        last_position = {
            "x": None,
            "y": None
        }

        state = {
            "active": False,
            "finished": False
        }

        lock = threading.Lock()

        def restore_window():
            try:
                self.deiconify()
                self.state("normal")
                self.attributes("-topmost", self.keep_on_top)
                self.lift()
                self.focus_force()
            except Exception:
                pass

        def add_move(x, y, force=False):
            x = int(x)
            y = int(y)

            with lock:
                last_x = last_position["x"]
                last_y = last_position["y"]

                if last_x is not None and last_y is not None:
                    distance = ((x - last_x) ** 2 + (y - last_y) ** 2) ** 0.5

                    if not force and distance < 4:
                        return

                local_events.append({
                    "type": "move",
                    "x": x,
                    "y": y
                })

                last_position["x"] = x
                last_position["y"] = y

        def finish_recording(save_route):
            if state["finished"]:
                return

            state["finished"] = True
            state["active"] = False

            with lock:
                events = list(local_events)

            self.route_recorder_open = False
            self.route_game_recording_active = False
            self.after(0, self.close_route_game_hud)

            try:
                if self.route_game_mouse_listener is not None:
                    self.route_game_mouse_listener.stop()
            except Exception:
                pass

            self.route_game_mouse_listener = None
            self.route_game_keyboard_listener = None

            if not save_route:
                def cancel_ui():
                    self.update_route_status(
                        "Estado: Grabación en juego cancelada",
                        "#a6adc8"
                    )
                    restore_window()

                self.after(0, cancel_ui)
                return

            if not events:
                def empty_ui():
                    self.update_route_status(
                        "Estado: No se grabó ningún punto",
                        "#f38ba8"
                    )
                    restore_window()

                self.after(0, empty_ui)
                return

            def save_ui():
                self.route_events = events
                self.update_route_labels()
                self.update_route_status(
                    "Estado: Ruta en juego grabada",
                    "#a6e3a1"
                )
                self.save_config()
                restore_window()

            self.after(0, save_ui)

        def on_key_press(key):
            pressed = self.normalize_pynput_key(key)

            if pressed == self.route_record_key:
                if state["active"]:
                    state["active"] = False
                    self.route_game_recording_active = False

                    self.after(
                        0,
                        lambda: self.update_route_status(
                            f"Estado: Grabación pausada · {record_key_text} continúa · ENTER guarda",
                            "#f9e2af"
                        )
                    )

                    self.after(
                        0,
                        lambda: self.update_route_game_hud(
                            f"Pausado · {record_key_text} continúa · ENTER guarda · ESC cancela",
                            "#f9e2af"
                        )
                    )
                    return

                state["active"] = True
                self.route_game_recording_active = True

                try:
                    x, y = pyautogui.position()
                    add_move(x, y, force=True)
                except Exception:
                    pass

                self.after(
                    0,
                    lambda: self.update_route_status(
                        f"Estado: Grabando en juego · {record_key_text} pausa · ENTER guarda · ESC cancela",
                        "#a6e3a1"
                    )
                )

                self.after(
                    0,
                    lambda: self.update_route_game_hud(
                        f"Grabando · {record_key_text} pausa · ENTER guarda · ESC cancela",
                        "#a6e3a1"
                    )
                )
                return

            if pressed == "enter":
                finish_recording(True)
                return False

            if pressed == "esc":
                finish_recording(False)
                return False

        def on_move(x, y):
            if not state["active"] or state["finished"]:
                return

            add_move(x, y)

        def on_click(x, y, button, pressed):
            if not pressed:
                return

            if not state["active"] or state["finished"]:
                return

            button_map = {
                mouse.Button.left: "left",
                mouse.Button.middle: "middle",
                mouse.Button.right: "right"
            }

            button_name = button_map.get(button, "left")

            add_move(x, y, force=True)

            with lock:
                local_events.append({
                    "type": "click",
                    "x": int(x),
                    "y": int(y),
                    "button": button_name
                })

        self.update_route_status(
            f"Estado: Juego · {record_key_text} inicia/pausa · ENTER guarda · ESC cancela",
            "#f9e2af"
        )

        self.open_route_game_hud(
            f"Juego · {record_key_text} inicia/pausa · ENTER guarda · ESC cancela"
        )

        self.route_game_mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click
        )

        self.route_game_keyboard_listener = keyboard.Listener(
            on_press=on_key_press
        )

        self.route_game_mouse_listener.daemon = True
        self.route_game_keyboard_listener.daemon = True

        self.route_game_mouse_listener.start()
        self.route_game_keyboard_listener.start()

        def minimize_for_game():
            try:
                self.attributes("-topmost", False)
                self.lower()
                self.iconify()
            except Exception:
                pass

            self.after(200, self.raise_route_game_hud)
            self.after(700, self.raise_route_game_hud)

        self.after(600, minimize_for_game)

    def open_route_recorder(self):
        self.stop_route()

        self.route_recorder_open = True
        record_key_text = self.get_key_display(self.route_record_key)

        local_events = []
        click_count = 0
        last_x = None
        last_y = None

        recording_state = {
            "active": False
        }

        overlay = tk.Toplevel(self)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.35)
        overlay.configure(bg="black")

        canvas = tk.Canvas(
            overlay,
            bg="black",
            cursor="cross",
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True)

        screen_width = overlay.winfo_screenwidth()

        instruction = canvas.create_text(
            screen_width // 2,
            45,
            text=(
                "Mueve el cursor al punto inicial | "
                f"{record_key_text} inicia/pausa | ENTER guarda | ESC cancela"
            ),
            fill="white",
            font=("Arial", 18, "bold")
        )

        counter_text = canvas.create_text(
            screen_width // 2,
            85,
            text="Preparado · Puntos: 0 · Clicks: 0",
            fill="#a6e3a1",
            font=("Arial", 14, "bold")
        )

        def update_counter():
            state_text = "Grabando" if recording_state["active"] else "Pausado"
            moves = sum(1 for event in local_events if event.get("type") == "move")
            clicks = sum(1 for event in local_events if event.get("type") == "click")

            canvas.itemconfig(
                counter_text,
                text=f"{state_text} · Puntos: {moves} · Clicks: {clicks}"
            )

        def add_move(x, y, force=False, draw_line=True):
            nonlocal last_x, last_y

            x = int(x)
            y = int(y)

            if last_x is not None and last_y is not None:
                distance = ((x - last_x) ** 2 + (y - last_y) ** 2) ** 0.5

                if not force and distance < 4:
                    return

            local_events.append({
                "type": "move",
                "x": x,
                "y": y
            })

            if draw_line and last_x is not None and last_y is not None:
                canvas.create_line(
                    last_x,
                    last_y,
                    x,
                    y,
                    fill="#89b4fa",
                    width=3
                )

            last_x = x
            last_y = y

            update_counter()

        def toggle_recording(event=None):
            x = overlay.winfo_pointerx()
            y = overlay.winfo_pointery()

            if recording_state["active"]:
                recording_state["active"] = False

                canvas.itemconfig(
                    instruction,
                    text=(
                        "Grabación pausada | Mueve el cursor si quieres reposicionarte | "
                        f"{record_key_text} continúa | ENTER guarda | ESC cancela"
                    ),
                    fill="#f9e2af"
                )

                update_counter()
                return "break"

            recording_state["active"] = True

            add_move(x, y, force=True, draw_line=False)

            canvas.create_oval(
                x - 6,
                y - 6,
                x + 6,
                y + 6,
                outline="#a6e3a1",
                width=3
            )

            canvas.itemconfig(
                instruction,
                text=(
                    "Grabando ruta | Mueve el cursor y haz clicks si quieres guardarlos | "
                    f"{record_key_text} pausa | ENTER guarda | ESC cancela"
                ),
                fill="#a6e3a1"
            )

            update_counter()
            return "break"

        def record_motion(event):
            if not recording_state["active"]:
                return

            add_move(event.x_root, event.y_root)

        def record_click(event):
            nonlocal click_count

            if not recording_state["active"]:
                canvas.itemconfig(
                    instruction,
                    text=f"Primero presiona {record_key_text} para empezar a grabar.",
                    fill="#f38ba8"
                )
                return "break"

            button_map = {
                1: "left",
                2: "middle",
                3: "right"
            }

            x = int(event.x_root)
            y = int(event.y_root)
            button = button_map.get(event.num, "left")

            add_move(x, y, force=True)

            local_events.append({
                "type": "click",
                "x": x,
                "y": y,
                "button": button
            })

            click_count += 1

            canvas.create_oval(
                x - 8,
                y - 8,
                x + 8,
                y + 8,
                outline="#f9e2af",
                width=3
            )

            canvas.create_text(
                x,
                y - 18,
                text=str(click_count),
                fill="#f9e2af",
                font=("Arial", 11, "bold")
            )

            update_counter()

            return "break"

        def cancel_recording(event=None):
            self.route_recorder_open = False

            try:
                overlay.destroy()
            except Exception:
                pass

            self.update_route_status("Estado: Grabación cancelada", "#a6adc8")
            self.lift()
            self.focus_force()

        def finish_recording(event=None):
            if not local_events:
                canvas.itemconfig(
                    instruction,
                    text=f"No se grabó ningún punto. Presiona {record_key_text} y mueve el cursor antes de guardar.",
                    fill="#f38ba8"
                )
                return "break"

            self.route_events = local_events

            self.update_route_labels()
            self.update_route_status("Estado: Ruta grabada", "#a6e3a1")
            self.save_config()

            self.route_recorder_open = False

            try:
                overlay.destroy()
            except Exception:
                pass

            self.lift()
            self.focus_force()

            return "break"

        def handle_recorder_key(event):
            pressed = self.normalize_tk_key(event.keysym)

            if pressed == self.route_record_key:
                return toggle_recording(event)

            if pressed == "enter":
                return finish_recording(event)

            if pressed == "esc":
                return cancel_recording(event)

            return None


        overlay.bind("<KeyPress>", handle_recorder_key)
        canvas.bind("<KeyPress>", handle_recorder_key)

        canvas.bind("<Motion>", record_motion)
        canvas.bind("<Button-1>", record_click)
        canvas.bind("<Button-2>", record_click)
        canvas.bind("<Button-3>", record_click)

        overlay.after(100, lambda: canvas.focus_set())

    def start_route(self):
        if not self.route_events:
            self.update_route_status("Estado: Falta grabar una ruta", "#f38ba8")

            self.show_warning_once(
                "Ruta no grabada",
                "Primero graba una ruta para poder reproducirla."
            )
            return

        self.route_counter = 0
        self.route_click_counter = 0
        self.route_last_speed_check = time.perf_counter()
        self.update_route_play_speed_label(0)

        self.route_running = True

        if self.record_route_button is not None:
            self.record_route_button.configure(state="disabled")

        if self.clear_route_button is not None:
            self.clear_route_button.configure(state="disabled")

        if self.record_route_game_button is not None:
            self.record_route_game_button.configure(state="disabled")

        self.update_route_status("Estado: Reproduciendo ruta", "#a6e3a1")

        if self.start_route_button is not None:
            self.start_route_button.configure(
                fg_color="#a6e3a1",
                text_color="black"
            )

        if self.stop_route_button is not None:
            self.stop_route_button.configure(
                fg_color="#45475a",
                text_color="white"
            )

    def stop_route(self):
        self.route_running = False
        self.target_window_paused_modules.discard("route")
        self.target_window_stop_scheduled.discard("route")

        if self.record_route_button is not None:
            self.record_route_button.configure(state="normal")

        if self.clear_route_button is not None:
            self.clear_route_button.configure(state="normal")

        if self.record_route_game_button is not None:
            self.record_route_game_button.configure(state="normal")

        self.update_route_status("Estado: Ruta detenida", "#a6adc8")
        self.update_route_play_speed_label(0)

        if self.start_route_button is not None:
            self.start_route_button.configure(
                fg_color="#1f6aa5",
                text_color="white"
            )

        if self.stop_route_button is not None:
            self.stop_route_button.configure(
                fg_color="#f38ba8",
                text_color="black"
            )

    def toggle_route(self):
        if self.route_running:
            self.stop_route()
        else:
            self.start_route()

    def clear_route(self):
        self.stop_route()

        self.route_events = []

        self.update_route_labels()
        self.update_route_status("Estado: Ruta limpiada", "#f9e2af")
        self.save_config()

    def route_loop(self):
        while not self.stop_thread:
            if self.route_running:
                events = list(self.route_events)

                if not events:
                    self.after(0, self.stop_route)
                    continue

                delay = 0.02 / max(1, self.route_speed_multiplier)

                for event in events:
                    if not self.route_running or self.stop_thread:
                        break

                    while self.route_running and not self.stop_thread:
                        if self.can_execute_for_target_window("route"):
                            break
                        time.sleep(0.05)

                    if not self.route_running or self.stop_thread:
                        break

                    try:
                        event_type = event.get("type")

                        if event_type == "move":
                            x = int(event.get("x", 0))
                            y = int(event.get("y", 0))

                            self.move_cursor_to(x, y)
                            self.route_counter += 1

                        elif event_type == "click":
                            x = int(event.get("x", 0))
                            y = int(event.get("y", 0))
                            button = event.get("button", "left")

                            self.click_mouse(
                                x=x,
                                y=y,
                                button=button,
                                clicks=1
                            )

                            self.route_counter += 1
                            self.route_click_counter += 1

                    except pyautogui.FailSafeException:
                        self.route_running = False

                        self.after(0, self.stop_route)
                        self.after(
                            0,
                            lambda: self.update_route_status(
                                "Estado: Ruta detenida por failsafe",
                                "#f38ba8"
                            )
                        )
                        break

                    except Exception:
                        self.route_running = False

                        self.after(0, self.stop_route)
                        self.after(
                            0,
                            lambda: self.update_route_status(
                                "Estado: Error al reproducir ruta",
                                "#f38ba8"
                            )
                        )
                        break

                    now = time.perf_counter()
                    elapsed = now - self.route_last_speed_check

                    if elapsed >= 1:
                        speed = int(self.route_counter / elapsed)

                        self.route_counter = 0
                        self.route_last_speed_check = now

                        self.after(
                            0,
                            lambda value=speed: self.update_route_play_speed_label(value)
                        )

                    time.sleep(delay)

                if self.route_running:
                    self.after(
                        0,
                        lambda: self.update_route_status(
                            "Estado: Reproduciendo ruta",
                            "#a6e3a1"
                        )
                    )

            else:
                time.sleep(0.01)

    def open_route_hotkey_window(self):
        if self.route_running:
            self.update_route_status(
                "Estado: Detén la ruta antes de cambiar la hotkey",
                "#f9e2af"
            )
            return

        if self.capturing_route_hotkey:
            return

        if self.route_hotkey_window is not None:
            try:
                if self.route_hotkey_window.winfo_exists():
                    self.route_hotkey_window.lift()
                    self.route_hotkey_window.focus_force()
                    return
            except Exception:
                pass

            self.route_hotkey_window = None
            self.route_hotkey_status_label = None
            self.capturing_route_hotkey = False

        if (
            self.hotkey_window is not None
            or self.click_hotkey_window is not None
            or self.press_key_window is not None
            or self.press_hotkey_window is not None
        ):
            return

        self.capturing_route_hotkey = True

        window_width = 420
        window_height = 190

        window = ctk.CTkToplevel(self)
        self.route_hotkey_window = window
        self.apply_icon_to_window(window)

        window.title("Hotkey de Ruta")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            window,
            text="Presiona la nueva tecla para iniciar/detener Ruta",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        label.pack(pady=(28, 10))

        self.route_hotkey_status_label = ctk.CTkLabel(
            window,
            text=f"Actual: {self.route_hotkey.upper()}",
            text_color="#a6adc8"
        )
        self.route_hotkey_status_label.pack(pady=4)

        hint = ctk.CTkLabel(
            window,
            text="No puede repetirse con otras hotkeys o la tecla de KeyPresser.",
            text_color="#6c7086",
            font=ctk.CTkFont(size=12)
        )
        hint.pack(pady=(4, 0))

        close_button = ctk.CTkButton(
            window,
            text="Cancelar",
            command=self.close_current_route_hotkey_window
        )
        close_button.pack(pady=14)

        window.protocol("WM_DELETE_WINDOW", self.close_current_route_hotkey_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(150, window.focus_force)

    def close_current_route_hotkey_window(self):
        window = self.route_hotkey_window

        self.route_hotkey_window = None
        self.route_hotkey_status_label = None
        self.capturing_route_hotkey = False

        if window is None:
            return

        try:
            window.grab_release()
        except Exception:
            pass

        try:
            if window.winfo_exists():
                window.withdraw()
        except Exception:
            pass

        def destroy_later():
            try:
                if window.winfo_exists():
                    window.destroy()
            except Exception:
                pass

        self.after(500, destroy_later)

        self.lift()
        self.focus_force()

    def open_route_record_key_window(self):
        if self.capturing_route_record_key:
            return

        if self.route_record_key_window is not None:
            try:
                if self.route_record_key_window.winfo_exists():
                    self.route_record_key_window.lift()
                    self.route_record_key_window.focus_force()
                    return
            except Exception:
                pass

            self.route_record_key_window = None
            self.route_record_key_status_label = None
            self.capturing_route_record_key = False

        if (
            self.hotkey_window is not None
            or self.click_hotkey_window is not None
            or self.press_key_window is not None
            or self.press_hotkey_window is not None
            or self.route_hotkey_window is not None
        ):
            return

        self.capturing_route_record_key = True

        window_width = 430
        window_height = 195

        window = ctk.CTkToplevel(self)
        self.route_record_key_window = window
        self.apply_icon_to_window(window)

        window.title("Tecla de grabación de Ruta")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        if self.general_settings_window is not None:
            window.transient(self.general_settings_window)
        else:
            window.transient(self)

        window.grab_set()
        window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            window,
            text="Presiona la tecla para iniciar/pausar la grabación",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        label.pack(pady=(28, 10))

        self.route_record_key_status_label = ctk.CTkLabel(
            window,
            text=f"Actual: {self.get_key_display(self.route_record_key)}",
            text_color="#a6adc8"
        )
        self.route_record_key_status_label.pack(pady=4)

        hint = ctk.CTkLabel(
            window,
            text="No puede ser ENTER, ESC ni una hotkey global.",
            text_color="#6c7086",
            font=ctk.CTkFont(size=12)
        )
        hint.pack(pady=(4, 0))

        close_button = ctk.CTkButton(
            window,
            text="Cancelar",
            command=self.close_current_route_record_key_window
        )
        close_button.pack(pady=14)

        window.protocol("WM_DELETE_WINDOW", self.close_current_route_record_key_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(150, window.focus_force)

    def close_current_route_record_key_window(self):
        window = self.route_record_key_window

        self.route_record_key_window = None
        self.route_record_key_status_label = None
        self.capturing_route_record_key = False

        if window is None:
            return

        try:
            window.grab_release()
        except Exception:
            pass

        try:
            if window.winfo_exists():
                window.withdraw()
        except Exception:
            pass

        def destroy_later():
            try:
                if window.winfo_exists():
                    window.destroy()
            except Exception:
                pass

        self.after(500, destroy_later)

        if self.general_settings_window is not None:
            try:
                self.general_settings_window.lift()
                self.general_settings_window.focus_force()
            except Exception:
                pass
        else:
            self.lift()
            self.focus_force()
