import random
import threading
import time
import tkinter as tk
from tkinter import messagebox
import os
import sys
from PIL import Image, ImageDraw, ImageTk
import pystray # type: ignore

import customtkinter as ctk
import pyautogui

try:
    import pydirectinput # type: ignore
    pydirectinput.PAUSE = 0
    HAS_PYDIRECTINPUT = True
except Exception:
    pydirectinput = None
    HAS_PYDIRECTINPUT = False

from pynput import keyboard, mouse
import cv2
import mss
import numpy as np

import ctypes
import ctypes.wintypes

from autoinputr.core.resources import (
    APP_DIR,
    CONFIG_DIR,
    CONFIG_FILE,
    LOGO_PATH,
    ICON_PATH,
    ICON_ICO_PATH,
    APP_NAME,
    APP_VERSION,
    TRACKER_TEMPLATE_FILE,
)

from autoinputr.core.config import (
    load_config_file,
    save_config_file,
)

from autoinputr.core.target_window import TargetWindowMixin
from autoinputr.modules.keypresser import KeyPresserMixin
from autoinputr.modules.clicker import ClickerMixin
from autoinputr.modules.mover import MoverMixin

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)


class AutoInputR(KeyPresserMixin, ClickerMixin, MoverMixin, TargetWindowMixin, ctk.CTk):
    def __init__(self):
        super().__init__()

        self.withdraw()

        self.title(f"{APP_NAME} v{APP_VERSION}")

        self.app_icon_photo = None
        self.header_icon_image = None
        self.window_icon_image = None
        self.window_selector_icon_image = None
        self.load_app_assets()

        self.window_width = 600
        self.window_height = 667

        self.config = self.load_config()

        self.input_backend = self.config.get("input_backend", "pydirectinput")

        if self.input_backend == "pydirectinput" and not HAS_PYDIRECTINPUT:
            self.input_backend = "pyautogui"

        # Ajusta estos valores si quieres mover la ventana unos pixeles.
        # 0, 0 significa centro exacto según Windows.
        self.center_offset_x = self.config.get("center_offset_x", -100)
        self.center_offset_y = self.config.get("center_offset_y", -100)

        self.keep_on_top = self.config.get("keep_on_top", True)
        self.turbo_mode = self.config.get("turbo_mode", False)

        # Ventana objetivo (AutoInputR v1.3)
        self.target_window_title = str(
            self.config.get("target_window_title", "") or ""
        )
        self.target_window_process = str(
            self.config.get("target_window_process", "") or ""
        )
        self.target_window_class = str(
            self.config.get("target_window_class", "") or ""
        )
        self.target_window_focus_only = bool(
            self.config.get("target_window_focus_only", True)
        )
        self.target_window_auto_resume = bool(
            self.config.get("target_window_auto_resume", True)
        )
        self.target_window_hwnd = 0
        self.target_window_last_resolve_attempt = 0.0
        self.target_window_state_code = "none"
        self.target_window_state_text = "Sin ventana objetivo"
        self.target_window_paused_modules = set()
        self.target_window_stop_scheduled = set()
        self.available_target_windows = []
        self.target_window_label_map = {}

        # Preparación para futura función de autoclick
        self.click_hours = self.config.get("click_hours", "0")
        self.click_minutes = self.config.get("click_minutes", "0")
        self.click_seconds = self.config.get("click_seconds", "0")
        self.click_milliseconds = self.config.get("click_milliseconds", "1")

        self.click_mouse_button = self.config.get("click_mouse_button", "Izquierdo")
        self.click_type = self.config.get("click_type", "Doble")

        self.click_repeat_mode = self.config.get("click_repeat_mode", "until_stopped")
        self.click_repeat_times = self.config.get("click_repeat_times", "1")

        self.click_position_mode = self.config.get("click_position_mode", "current")
        self.click_x = self.config.get("click_x", "0")
        self.click_y = self.config.get("click_y", "0")

        self.click_turbo_mode = self.config.get("click_turbo_mode", False)
        self.click_hotkey = self.config.get("click_hotkey", "f7")

        self.click_running = False
        self.click_hotkey_is_down = False
        self.click_counter = 0
        self.click_last_speed_check = time.perf_counter()
        self.click_current_speed = 0
        self.click_repeat_done = 0

        # AutoPresser
        self.press_hours = self.config.get("press_hours", "0")
        self.press_minutes = self.config.get("press_minutes", "0")
        self.press_seconds = self.config.get("press_seconds", "0")
        self.press_milliseconds = self.config.get("press_milliseconds", "100")

        self.press_key = self.config.get("press_key", "space")
        self.press_hotkey = self.config.get("press_hotkey", "f6")
        self.press_turbo_mode = self.config.get("press_turbo_mode", False)

        self.press_repeat_mode = self.config.get("press_repeat_mode", "until_stopped")
        self.press_repeat_times = self.config.get("press_repeat_times", "1")

        self.press_running = False
        self.press_hotkey_is_down = False
        self.press_counter = 0
        self.press_last_speed_check = time.perf_counter()
        self.press_current_speed = 0
        self.press_repeat_done = 0

        # Ruta del cursor
        self.route_events = self.config.get("route_events", [])

        if not isinstance(self.route_events, list):
            self.route_events = []

        self.route_speed_multiplier = int(
            self.config.get("route_speed_multiplier", 1)
        )
        self.route_speed_multiplier = max(1, min(1000, self.route_speed_multiplier))

        self.route_hotkey = self.config.get("route_hotkey", "f5")
        self.route_hotkey_is_down = False

        self.route_record_key = str(
            self.config.get("route_record_key", "space")
        ).lower()

        self.route_recorder_open = False

        self.route_game_keyboard_listener = None
        self.route_game_mouse_listener = None
        self.route_game_recording_active = False

        self.route_game_hud_window = None
        self.route_game_hud_canvas = None
        self.route_game_hud_text = None
        self.route_game_hud_bg = None
        self.route_game_hud_windows = []
        self.route_game_hud_shadow = None

        self.route_running = False
        self.route_counter = 0
        self.route_click_counter = 0
        self.route_last_speed_check = time.perf_counter()
        self.route_current_speed = 0

        # Rastreador visual por plantilla
        self.tracker_area = None
        self.tracker_template = None

        self.tracker_hotkey = self.config.get("tracker_hotkey", "f4")
        self.tracker_hotkey_is_down = False

        self.tracker_running = False
        self.tracker_speed_multiplier = int(
            self.config.get("tracker_speed_multiplier", 20)
        )
        self.tracker_speed_multiplier = max(1, min(100, self.tracker_speed_multiplier))

        self.tracker_confidence = float(
            self.config.get("tracker_confidence", 0.75)
        )
        self.tracker_confidence = max(0.50, min(0.99, self.tracker_confidence))

        self.tracker_counter = 0
        self.tracker_last_speed_check = time.perf_counter()
        self.tracker_current_speed = 0
        self.tracker_last_status_update = 0

        self.tracker_smooth_follow = bool(
            self.config.get("tracker_smooth_follow", True)
        )

        self.tracker_nudge_enabled = bool(
            self.config.get("tracker_nudge_enabled", True)
        )

        self.tracker_random_click_enabled = bool(
            self.config.get("tracker_random_click_enabled", True)
        )

        self.tracker_random_click_min_seconds = float(
            self.config.get("tracker_random_click_min_seconds", 35)
        )

        self.tracker_random_click_max_seconds = float(
            self.config.get("tracker_random_click_max_seconds", 50)
        )

        self.tracker_next_random_click_time = 0

        self.tracker_last_target = None
        self.tracker_stuck_counter = 0
        self.tracker_unstick_direction_index = 0
        self.tracker_unstick_strength = int(
            self.config.get("tracker_unstick_strength", 90)
        )
        self.tracker_unstick_strength = max(30, min(250, self.tracker_unstick_strength))

        self.movement_mode = self.config.get("movement_mode", "Aleatorio")

        self.movement_smooth_enabled = bool(
            self.config.get("movement_smooth_enabled", True)
        )

        self.movement_random_click_enabled = bool(
            self.config.get("movement_random_click_enabled", True)
        )

        self.movement_random_click_min_seconds = float(
            self.config.get("movement_random_click_min_seconds", 25)
        )

        self.movement_random_click_max_seconds = float(
            self.config.get("movement_random_click_max_seconds", 45)
        )

        self.movement_next_random_click_time = 0

        self.movement_speed = int(
            self.config.get("movement_speed", 700)
        )
        self.movement_speed = max(0, min(1000, self.movement_speed))

        self.movement_speed_label = None
        self.movement_speed_slider = None

        self.current_x = None
        self.current_y = None
        self.direction_x = 1
        self.direction_y = 1

        self.area = None
        self.running = False

        self.hotkey = self.config.get("hotkey", "f8")

        self.hotkey_is_down = False
        self.capturing_hotkey = False

        self.hotkey_window = None
        self.hotkey_status_label = None

        self.click_hotkey_window = None
        self.click_hotkey_status_label = None
        self.capturing_click_hotkey = False

        self.press_key_window = None
        self.press_key_status_label = None
        self.capturing_press_key = False

        self.press_hotkey_window = None
        self.press_hotkey_status_label = None
        self.capturing_press_hotkey = False

        self.route_hotkey_window = None
        self.route_hotkey_status_label = None
        self.capturing_route_hotkey = False

        self.route_record_key_window = None
        self.route_record_key_status_label = None
        self.capturing_route_record_key = False

        self.tracker_hotkey_window = None
        self.tracker_hotkey_status_label = None
        self.capturing_tracker_hotkey = False

        self.route_info_label = None
        self.route_description_label = None
        self.route_speed_label = None
        self.route_speed_slider = None
        self.route_status_label = None
        self.route_play_speed_label = None
        self.start_route_button = None
        self.stop_route_button = None
        self.record_route_button = None

        self.record_route_game_button = None

        self.clear_route_button = None
        self.route_hotkey_button = None

        self.tracker_area_label = None
        self.tracker_template_label = None
        self.tracker_speed_label = None
        self.tracker_speed_slider = None
        self.tracker_confidence_label = None
        self.tracker_confidence_slider = None
        self.tracker_status_label = None
        self.tracker_detection_speed_label = None
        self.start_tracker_button = None
        self.stop_tracker_button = None
        self.tracker_hotkey_button = None

        self.settings_window = None
        self.general_settings_window = None
        self.window_selector_window = None

        self.window_selector_button = None
        self.window_selector_option = None
        self.window_selector_status_label = None
        self.window_selector_focus_checkbox = None
        self.window_selector_auto_resume_checkbox = None

        self.general_target_window_option = None
        self.general_target_window_status_label = None
        self.general_target_focus_checkbox = None
        self.general_target_auto_resume_checkbox = None

        self.general_keep_on_top_checkbox = None

        self.general_click_turbo_checkbox = None
        self.general_press_turbo_checkbox = None
        self.general_movement_turbo_checkbox = None

        self.general_click_turbo_value_label = None
        self.general_press_turbo_value_label = None
        self.general_movement_turbo_value_label = None

        self.general_click_hotkey_label = None
        self.general_press_hotkey_label = None
        self.general_movement_hotkey_label = None
        self.general_route_hotkey_label = None
        self.general_route_record_key_label = None
        self.general_tracker_hotkey_label = None

        self.general_tracker_speed_label = None
        self.general_tracker_speed_slider = None
        self.general_tracker_confidence_label = None
        self.general_tracker_confidence_slider = None
        self.general_tracker_smooth_checkbox = None
        self.general_tracker_nudge_checkbox = None
        self.general_tracker_random_click_checkbox = None

        self.general_press_key_label = None
        self.general_movement_mode_option = None
        self.general_movement_speed_label = None
        self.general_movement_speed_slider = None
        self.general_area_label = None

        self.general_settings_status_label = None

        self.about_window = None
        self.close_dialog = None

        self.warning_open = False
        self.stop_thread = False

        self.movement_counter = 0
        self.last_speed_check = time.perf_counter()
        self.current_speed = 0

        self.tray_icon = None
        self.closing_from_tray = False
        self.skip_save_on_close = False

        self.geometry(f"{self.window_width}x{self.window_height}")
        self.resizable(False, False)

        self.create_ui()
        self.load_saved_area()
        self.load_saved_tracker_area()
        self.load_saved_tracker_template()
        self.resolve_saved_target_window()
        self.start_keyboard_listener()
        self.after(350, self.refresh_target_window_state_loop)

        self.movement_thread = threading.Thread(
            target=self.movement_loop,
            daemon=True
        )
        self.movement_thread.start()

        self.click_thread = threading.Thread(
            target=self.click_loop,
            daemon=True
        )
        self.click_thread.start()

        self.press_thread = threading.Thread(
            target=self.press_loop,
            daemon=True
        )
        self.press_thread.start()

        self.route_thread = threading.Thread(
            target=self.route_loop,
            daemon=True
        )
        self.route_thread.start()

        self.tracker_thread = threading.Thread(
            target=self.tracker_loop,
            daemon=True
        )
        self.tracker_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.handle_close_request)

        self.after(100, self.show_main_window)

    def load_app_assets(self):
        try:
            if ICON_ICO_PATH.exists():
                self.iconbitmap(default=str(ICON_ICO_PATH))
        except Exception:
            pass

        try:
            if ICON_PATH.exists():
                icon_image = Image.open(ICON_PATH).convert("RGBA")
                self.app_icon_photo = ImageTk.PhotoImage(icon_image)
                self.iconphoto(True, self.app_icon_photo)
        except Exception:
            self.app_icon_photo = None

        try:
            if ICON_PATH.exists():
                icon_image = Image.open(ICON_PATH).convert("RGBA")

                self.header_icon_image = ctk.CTkImage(
                    light_image=icon_image,
                    dark_image=icon_image,
                    size=(38, 38)
                )

                self.window_icon_image = ctk.CTkImage(
                    light_image=icon_image,
                    dark_image=icon_image,
                    size=(30, 30)
                )
        except Exception:
            self.header_icon_image = None

        try:
            monitor_icon = Image.new("RGBA", (28, 28), (0, 0, 0, 0))
            draw = ImageDraw.Draw(monitor_icon)
            draw.rounded_rectangle(
                (3, 4, 25, 19),
                radius=2,
                outline=(205, 214, 244, 255),
                width=2
            )
            draw.line((14, 19, 14, 23), fill=(205, 214, 244, 255), width=2)
            draw.line((9, 24, 19, 24), fill=(205, 214, 244, 255), width=2)

            self.window_selector_icon_image = ctk.CTkImage(
                light_image=monitor_icon,
                dark_image=monitor_icon,
                size=(24, 24)
            )
        except Exception:
            self.window_selector_icon_image = None
    
    
    def apply_icon_to_window(self, window):
        def apply_now():
            try:
                if ICON_ICO_PATH.exists():
                    window.iconbitmap(default=str(ICON_ICO_PATH))
                    window.wm_iconbitmap(default=str(ICON_ICO_PATH))
            except Exception:
                pass

            try:
                if self.app_icon_photo is not None:
                    window.iconphoto(False, self.app_icon_photo)
            except Exception:
                pass

        def add_visible_logo():
            try:
                if self.window_icon_image is None:
                    return

                if hasattr(window, "_app_logo_label"):
                    return

                window._app_logo_label = ctk.CTkLabel(
                    window,
                    text="",
                    image=self.window_icon_image
                )
                window._app_logo_label.place(x=14, y=14)
            except Exception:
                pass

        apply_now()
        add_visible_logo()

        try:
            window.after(150, apply_now)
            window.after(400, apply_now)
            window.after(150, add_visible_logo)
        except Exception:
            pass
    
    def create_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(6, 2))

        if self.header_icon_image is not None:
            header_icon = ctk.CTkLabel(
                header_frame,
                text="",
                image=self.header_icon_image
            )
            header_icon.pack(side="left", padx=(0, 10))

        title = ctk.CTkLabel(
            header_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")

        version_label = ctk.CTkLabel(
            header_frame,
            text=f"v{APP_VERSION}",
            text_color="#a6adc8",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        version_label.pack(side="left", padx=(8, 0), pady=(8, 0))

        subtitle = ctk.CTkLabel(
            self,
            text="Automatizador de clicks, teclas, rutas, rastreo y movimiento del cursor",
            text_color="#a6adc8"
        )
        subtitle.pack(pady=(0, 4))

        main_frame = ctk.CTkFrame(self, corner_radius=16)
        main_frame.pack(padx=20, pady=(6, 12), fill="both", expand=True)

        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(padx=12, pady=(12, 6), fill="both", expand=False)

        click_tab = self.tabview.add("Clicker")
        press_tab = self.tabview.add("KeyPresser")
        movement_tab = self.tabview.add("Mover")
        route_tab = self.tabview.add("Ruta")
        tracker_tab = self.tabview.add("Rastreador")

        self.create_click_section(click_tab)
        self.create_press_section(press_tab)

        self.create_interval_section(movement_tab)
        self.create_area_section(movement_tab)
        self.create_buttons_section(movement_tab)

        self.create_route_section(route_tab)

        self.create_tracker_section(tracker_tab)

        self.create_general_controls(main_frame)





    
    def create_general_controls(self, parent):
        general_frame = ctk.CTkFrame(parent, fg_color="transparent")
        general_frame.pack(padx=12, pady=(0, 6), fill="x")

        self.topmost_checkbox = ctk.CTkCheckBox(
            general_frame,
            text="Mantener encima",
            command=self.toggle_topmost
        )
        self.topmost_checkbox.pack(side="left")

        if self.keep_on_top:
            self.topmost_checkbox.select()

        settings_button = ctk.CTkButton(
            general_frame,
            text="⚙",
            width=42,
            height=36,
            fg_color="#45475a",
            hover_color="#585b70",
            font=ctk.CTkFont(size=18),
            command=self.open_settings_window
        )
        settings_button.pack(side="right")

        self.window_selector_button = ctk.CTkButton(
            general_frame,
            text="" if self.window_selector_icon_image is not None else "▣",
            image=self.window_selector_icon_image,
            width=42,
            height=36,
            fg_color="#45475a",
            hover_color="#585b70",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.open_window_selector
        )
        self.window_selector_button.pack(side="right", padx=(0, 8))

    

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

    def create_tracker_section(self, parent):
        info_frame = ctk.CTkFrame(parent, corner_radius=14)
        info_frame.pack(padx=12, pady=(6, 6), fill="x")

        title = ctk.CTkLabel(
            info_frame,
            text="Rastreador visual",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        title.pack(anchor="w", padx=14, pady=(10, 4))

        description = ctk.CTkLabel(
            info_frame,
            text="Busca un objetivo visual dentro de una zona y mueve el cursor hacia él.",
            text_color="#a6adc8",
            font=ctk.CTkFont(size=12),
            wraplength=500,
            justify="left"
        )
        description.pack(anchor="w", padx=14, pady=(0, 4))

        self.tracker_area_label = ctk.CTkLabel(
            info_frame,
            text=self.get_tracker_summary_text(),
            text_color="#a6adc8",
            justify="left",
            font=ctk.CTkFont(size=12)
        )
        self.tracker_area_label.pack(anchor="w", padx=14, pady=(0, 8))

        self.tracker_template_label = None

        controls_frame = ctk.CTkFrame(parent, corner_radius=14)
        controls_frame.pack(padx=12, pady=4, fill="x")

        controls_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_row.pack(padx=14, pady=(8, 10), fill="x")

        # Velocidad
        speed_column = ctk.CTkFrame(controls_row, fg_color="transparent")
        speed_column.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        speed_header = ctk.CTkFrame(speed_column, fg_color="transparent")
        speed_header.pack(fill="x", pady=(0, 2))

        speed_title = ctk.CTkLabel(
            speed_header,
            text="Velocidad",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        speed_title.pack(side="left")

        self.tracker_speed_label = ctk.CTkLabel(
            speed_header,
            text=f"x{self.tracker_speed_multiplier}",
            text_color="#a6e3a1",
            width=38
        )
        self.tracker_speed_label.pack(side="right")

        self.tracker_speed_slider = ctk.CTkSlider(
            speed_column,
            from_=1,
            to=100,
            number_of_steps=99,
            command=self.change_tracker_speed
        )
        self.tracker_speed_slider.pack(fill="x")
        self.tracker_speed_slider.set(self.tracker_speed_multiplier)

        # Coincidencia
        confidence_column = ctk.CTkFrame(controls_row, fg_color="transparent")
        confidence_column.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        confidence_header = ctk.CTkFrame(confidence_column, fg_color="transparent")
        confidence_header.pack(fill="x", pady=(0, 2))

        confidence_title = ctk.CTkLabel(
            confidence_header,
            text="Coincidencia",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confidence_title.pack(side="left")

        self.tracker_confidence_label = ctk.CTkLabel(
            confidence_header,
            text=f"{int(self.tracker_confidence * 100)}%",
            text_color="#a6e3a1",
            width=38
        )
        self.tracker_confidence_label.pack(side="right")

        self.tracker_confidence_slider = ctk.CTkSlider(
            confidence_column,
            from_=50,
            to=99,
            number_of_steps=49,
            command=self.change_tracker_confidence
        )
        self.tracker_confidence_slider.pack(fill="x")
        self.tracker_confidence_slider.set(int(self.tracker_confidence * 100))

        controls_row.grid_columnconfigure(0, weight=1)
        controls_row.grid_columnconfigure(1, weight=1)

        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(padx=12, pady=(8, 2), fill="x")

        area_button = ctk.CTkButton(
            buttons_frame,
            text="Elegir zona",
            height=40,
            command=self.select_tracker_area
        )
        area_button.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="ew")

        template_button = ctk.CTkButton(
            buttons_frame,
            text="Elegir objetivo",
            height=40,
            command=self.select_tracker_template
        )
        template_button.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="ew")

        clear_button = ctk.CTkButton(
            buttons_frame,
            text="Limpiar rastreador",
            height=40,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.clear_tracker
        )
        clear_button.grid(row=1, column=0, columnspan=2, pady=4, sticky="ew")

        self.start_tracker_button = ctk.CTkButton(
            buttons_frame,
            text=f"Iniciar ({self.tracker_hotkey.upper()})",
            height=40,
            command=self.start_tracker
        )
        self.start_tracker_button.grid(row=2, column=0, padx=(0, 8), pady=4, sticky="ew")

        self.stop_tracker_button = ctk.CTkButton(
            buttons_frame,
            text=f"Detener ({self.tracker_hotkey.upper()})",
            height=40,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.stop_tracker
        )
        self.stop_tracker_button.grid(row=2, column=1, padx=(8, 0), pady=4, sticky="ew")

        self.tracker_hotkey_button = ctk.CTkButton(
            buttons_frame,
            text="Configuración de hotkey",
            height=40,
            command=self.open_tracker_hotkey_window
        )
        self.tracker_hotkey_button.grid(row=3, column=0, columnspan=2, pady=4, sticky="ew")

        self.tracker_hotkey_button.bind("<Return>", lambda event: "break")
        self.tracker_hotkey_button.bind("<space>", lambda event: "break")
        self.tracker_hotkey_button.bind("<KP_Enter>", lambda event: "break")
        self.tracker_hotkey_button.bind("<KeyPress>", lambda event: "break")

        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        status_row = ctk.CTkFrame(parent, fg_color="transparent")
        status_row.pack(padx=12, pady=(30, 0), fill="x")

        self.tracker_detection_speed_label = ctk.CTkLabel(
            status_row,
            text="Velocidad: 0 det/s",
            text_color="#a6adc8"
        )
        self.tracker_detection_speed_label.pack(side="right", padx=(12, 0))

        self.tracker_status_label = ctk.CTkLabel(
            status_row,
            text="Estado: Rastreador detenido",
            text_color="#a6adc8"
        )
        self.tracker_status_label.pack(side="right")


    # ------------------------------------------------------------------
    # Ventana objetivo (AutoInputR v1.3)
    # ------------------------------------------------------------------



















    def open_window_selector(self):
        if self.window_selector_window is not None:
            try:
                self.window_selector_window.lift()
                self.window_selector_window.focus_force()
            except Exception:
                pass
            return

        window_width = 560
        window_height = 330

        window = ctk.CTkToplevel(self)
        self.window_selector_window = window
        self.apply_icon_to_window(window)

        window.title(f"Ventana objetivo - {APP_NAME}")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")
        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", self.keep_on_top)

        title = ctk.CTkLabel(
            window,
            text="Ventana objetivo",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(22, 6))

        info = ctk.CTkLabel(
            window,
            text="AutoInputR pausará sus acciones cuando la ventana seleccionada no tenga el foco.",
            text_color="#a6adc8",
            wraplength=500,
            justify="center"
        )
        info.pack(pady=(0, 12))

        self.window_selector_option = ctk.CTkOptionMenu(
            window,
            values=["Cargando ventanas..."],
            width=500,
            height=36,
            command=self.choose_target_window_from_label
        )
        self.window_selector_option.pack(padx=28, pady=(0, 10), fill="x")

        actions = ctk.CTkFrame(window, fg_color="transparent")
        actions.pack(padx=28, pady=(0, 10), fill="x")

        refresh_button = ctk.CTkButton(
            actions,
            text="Actualizar",
            height=34,
            command=self.refresh_target_window_list
        )
        refresh_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        focused_button = ctk.CTkButton(
            actions,
            text="Usar ventana enfocada",
            height=34,
            command=self.capture_foreground_target_window
        )
        focused_button.grid(row=0, column=1, padx=6, sticky="ew")

        clear_button = ctk.CTkButton(
            actions,
            text="Limpiar",
            height=34,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.clear_target_window
        )
        clear_button.grid(row=0, column=2, padx=(6, 0), sticky="ew")

        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)

        self.window_selector_focus_checkbox = ctk.CTkCheckBox(
            window,
            text="Pausar automatizaciones si la ventana pierde el foco",
            command=self.toggle_target_focus_only
        )
        self.window_selector_focus_checkbox.pack(anchor="w", padx=30, pady=(0, 8))

        self.window_selector_auto_resume_checkbox = ctk.CTkCheckBox(
            window,
            text="Reanudar automáticamente al recuperar el foco",
            command=self.toggle_target_auto_resume
        )
        self.window_selector_auto_resume_checkbox.pack(anchor="w", padx=30, pady=(0, 10))

        self.window_selector_status_label = ctk.CTkLabel(
            window,
            text="",
            text_color="#a6adc8",
            wraplength=500
        )
        self.window_selector_status_label.pack(pady=(0, 8))

        close_button = ctk.CTkButton(
            window,
            text="Cerrar",
            width=130,
            height=34,
            command=self.close_window_selector
        )
        close_button.pack(pady=(0, 14))

        window.protocol("WM_DELETE_WINDOW", self.close_window_selector)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        self.refresh_target_window_controls()
        window.after(100, window.lift)
        window.after(100, window.focus_force)

    def close_window_selector(self):
        window = self.window_selector_window
        self.window_selector_window = None

        if window is not None:
            try:
                window.grab_release()
            except Exception:
                pass

            try:
                window.destroy()
            except Exception:
                pass

        self.window_selector_option = None
        self.window_selector_status_label = None
        self.window_selector_focus_checkbox = None
        self.window_selector_auto_resume_checkbox = None

        try:
            self.lift()
            self.focus_force()
        except Exception:
            pass

    def create_target_window_settings_section(self, parent):
        target_frame = ctk.CTkFrame(parent, corner_radius=12)
        target_frame.pack(padx=10, pady=8, fill="x")

        title = ctk.CTkLabel(
            target_frame,
            text="Ventana objetivo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(anchor="w", padx=14, pady=(10, 8))

        self.general_target_window_option = ctk.CTkOptionMenu(
            target_frame,
            values=["Cargando ventanas..."],
            command=self.choose_target_window_from_label
        )
        self.general_target_window_option.pack(
            padx=14,
            pady=(0, 8),
            fill="x"
        )

        actions = ctk.CTkFrame(target_frame, fg_color="transparent")
        actions.pack(padx=14, pady=(0, 8), fill="x")

        refresh_button = ctk.CTkButton(
            actions,
            text="Actualizar",
            height=31,
            command=self.refresh_target_window_list
        )
        refresh_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        focused_button = ctk.CTkButton(
            actions,
            text="Usar enfocada",
            height=31,
            command=self.capture_foreground_target_window
        )
        focused_button.grid(row=0, column=1, padx=5, sticky="ew")

        clear_button = ctk.CTkButton(
            actions,
            text="Limpiar",
            height=31,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.clear_target_window
        )
        clear_button.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)

        self.general_target_focus_checkbox = ctk.CTkCheckBox(
            target_frame,
            text="Pausar si la ventana pierde el foco",
            command=self.toggle_target_focus_only
        )
        self.general_target_focus_checkbox.pack(
            anchor="w",
            padx=14,
            pady=(0, 7)
        )

        self.general_target_auto_resume_checkbox = ctk.CTkCheckBox(
            target_frame,
            text="Reanudar al recuperar el foco",
            command=self.toggle_target_auto_resume
        )
        self.general_target_auto_resume_checkbox.pack(
            anchor="w",
            padx=14,
            pady=(0, 7)
        )

        self.general_target_window_status_label = ctk.CTkLabel(
            target_frame,
            text="",
            text_color="#a6adc8",
            font=ctk.CTkFont(size=12),
            wraplength=420,
            justify="left"
        )
        self.general_target_window_status_label.pack(
            anchor="w",
            padx=14,
            pady=(0, 12)
        )

        self.refresh_target_window_controls()






    def center_window(self, window, width, height, offset_x=0, offset_y=0):
        window.update_idletasks()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = ((screen_width - width) // 2) + offset_x
        y = ((screen_height - height) // 2) + offset_y

        window.geometry(f"{width}x{height}+{x}+{y}")

    def show_main_window(self):
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.resizable(False, False)

        self.center_window(
            self,
            self.window_width,
            self.window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", self.keep_on_top)

    def show_warning_once(self, title, message):
        if self.warning_open:
            return

        self.warning_open = True

        try:
            messagebox.showwarning(title, message, parent=self)
        finally:
            self.warning_open = False

    def load_config(self):
        return load_config_file()

    def save_config(self):
        try:
            config = {
                "hotkey": self.hotkey,
                "center_offset_x": self.center_offset_x,
                "center_offset_y": self.center_offset_y,
                "keep_on_top": self.keep_on_top,
                "turbo_mode": self.turbo_mode,

                "target_window_title": self.target_window_title,
                "target_window_process": self.target_window_process,
                "target_window_class": self.target_window_class,
                "target_window_focus_only": self.target_window_focus_only,
                "target_window_auto_resume": self.target_window_auto_resume,

                "movement_mode": self.movement_mode,
                "movement_speed": self.movement_speed,
                "movement_smooth_enabled": self.movement_smooth_enabled,
                "movement_random_click_enabled": self.movement_random_click_enabled,
                "movement_random_click_min_seconds": self.movement_random_click_min_seconds,
                "movement_random_click_max_seconds": self.movement_random_click_max_seconds,

                "route_events": self.route_events,
                "route_speed_multiplier": self.route_speed_multiplier,
                "route_hotkey": self.route_hotkey,
                "route_record_key": self.route_record_key,

                "tracker_area": list(self.tracker_area) if self.tracker_area else None,
                "tracker_hotkey": self.tracker_hotkey,
                "tracker_speed_multiplier": self.tracker_speed_multiplier,
                "tracker_confidence": self.tracker_confidence,

                "tracker_smooth_follow": self.tracker_smooth_follow,
                "tracker_nudge_enabled": self.tracker_nudge_enabled,
                "tracker_unstick_strength": self.tracker_unstick_strength,

                "tracker_random_click_enabled": self.tracker_random_click_enabled,
                "tracker_random_click_min_seconds": self.tracker_random_click_min_seconds,
                "tracker_random_click_max_seconds": self.tracker_random_click_max_seconds,

                "input_backend": self.input_backend,

                "click_hours": (
                    self.click_hours_entry.get()
                    if hasattr(self, "click_hours_entry")
                    else self.click_hours
                ),
                "click_minutes": (
                    self.click_minutes_entry.get()
                    if hasattr(self, "click_minutes_entry")
                    else self.click_minutes
                ),
                "click_seconds": (
                    self.click_seconds_entry.get()
                    if hasattr(self, "click_seconds_entry")
                    else self.click_seconds
                ),
                "click_milliseconds": (
                    self.click_milliseconds_entry.get()
                    if hasattr(self, "click_milliseconds_entry")
                    else self.click_milliseconds
                ),
                "click_mouse_button": (
                    self.click_mouse_button_option.get()
                    if hasattr(self, "click_mouse_button_option")
                    else self.click_mouse_button
                ),
                "click_type": (
                    self.click_type_option.get()
                    if hasattr(self, "click_type_option")
                    else self.click_type
                ),
                "click_repeat_mode": (
                    self.click_repeat_var.get()
                    if hasattr(self, "click_repeat_var")
                    else self.click_repeat_mode
                ),
                "click_repeat_times": (
                    self.click_repeat_entry.get()
                    if hasattr(self, "click_repeat_entry")
                    else self.click_repeat_times
                ),
                "click_position_mode": (
                    self.click_position_var.get()
                    if hasattr(self, "click_position_var")
                    else self.click_position_mode
                ),
                "click_turbo_mode": (
                    bool(self.click_turbo_checkbox.get())
                    if hasattr(self, "click_turbo_checkbox")
                    else self.click_turbo_mode
                ),
                "click_hotkey": self.click_hotkey,
                "click_x": (
                    self.click_x_entry.get()
                    if hasattr(self, "click_x_entry")
                    else self.click_x
                ),
                "click_y": (
                    self.click_y_entry.get()
                    if hasattr(self, "click_y_entry")
                    else self.click_y
                ),
                "press_hours": (
                    self.press_hours_entry.get()
                    if hasattr(self, "press_hours_entry")
                    else self.press_hours
                ),
                "press_minutes": (
                    self.press_minutes_entry.get()
                    if hasattr(self, "press_minutes_entry")
                    else self.press_minutes
                ),
                "press_seconds": (
                    self.press_seconds_entry.get()
                    if hasattr(self, "press_seconds_entry")
                    else self.press_seconds
                ),
                "press_milliseconds": (
                    self.press_milliseconds_entry.get()
                    if hasattr(self, "press_milliseconds_entry")
                    else self.press_milliseconds
                ),
                "press_key": self.press_key,
                "press_hotkey": self.press_hotkey,
                "press_turbo_mode": (
                    bool(self.press_turbo_checkbox.get())
                    if hasattr(self, "press_turbo_checkbox")
                    else self.press_turbo_mode
                ),
                "press_repeat_mode": (
                    self.press_repeat_var.get()
                    if hasattr(self, "press_repeat_var")
                    else self.press_repeat_mode
                ),
                "press_repeat_times": (
                    self.press_repeat_entry.get()
                    if hasattr(self, "press_repeat_entry")
                    else self.press_repeat_times
                ),

                "area": list(self.area) if self.area else None
            }

            if hasattr(self, "hours_entry"):
                config["hours"] = self.hours_entry.get()
                config["minutes"] = self.minutes_entry.get()
                config["seconds"] = self.seconds_entry.get()
                config["milliseconds"] = self.milliseconds_entry.get()

            save_config_file(config)

        except Exception:
            pass
















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



    def get_key_display(self, key_name):
        names = {
            "space": "ESPACIO",
            "enter": "ENTER",
            "esc": "ESC",
            "ctrl": "CTRL",
            "shift": "SHIFT",
            "alt": "ALT",
            "tab": "TAB"
        }

        return names.get(str(key_name).lower(), str(key_name).upper())

    def normalize_tk_key(self, keysym):
        value = str(keysym or "").lower()

        aliases = {
            "return": "enter",
            "escape": "esc",
            "control_l": "ctrl",
            "control_r": "ctrl",
            "shift_l": "shift",
            "shift_r": "shift",
            "alt_l": "alt",
            "alt_r": "alt"
        }

        return aliases.get(value, value)

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
    






    def toggle_topmost(self):
        if hasattr(self, "topmost_checkbox"):
            self.set_keep_on_top(bool(self.topmost_checkbox.get()))










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

    def select_tracker_area(self):
        self.stop_tracker()

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
            50,
            text="Arrastra para seleccionar la zona donde aparecerá el objetivo | ESC cancela",
            fill="white",
            font=("Arial", 18, "bold")
        )

        data = {
            "start_x": 0,
            "start_y": 0,
            "rectangle": None
        }

        def cancel_selection(event=None):
            try:
                overlay.destroy()
            except Exception:
                pass

            self.update_tracker_status("Estado: Selección cancelada", "#a6adc8")
            self.lift()
            self.focus_force()

        def on_press(event):
            data["start_x"] = event.x
            data["start_y"] = event.y

            if data["rectangle"]:
                canvas.delete(data["rectangle"])

            data["rectangle"] = canvas.create_rectangle(
                event.x,
                event.y,
                event.x,
                event.y,
                outline="#89b4fa",
                width=3
            )

        def on_drag(event):
            if data["rectangle"]:
                canvas.coords(
                    data["rectangle"],
                    data["start_x"],
                    data["start_y"],
                    event.x,
                    event.y
                )

        def on_release(event):
            x1 = min(data["start_x"], event.x)
            y1 = min(data["start_y"], event.y)
            x2 = max(data["start_x"], event.x)
            y2 = max(data["start_y"], event.y)

            if x2 - x1 < 40 or y2 - y1 < 40:
                canvas.itemconfig(
                    instruction,
                    text="Zona demasiado pequeña. Intenta de nuevo | ESC cancela",
                    fill="#f38ba8"
                )
                return

            self.tracker_area = (x1, y1, x2, y2)

            self.update_tracker_labels()
            self.update_tracker_status("Estado: Zona de búsqueda seleccionada", "#a6e3a1")
            self.save_config()

            try:
                overlay.destroy()
            except Exception:
                pass

            self.lift()
            self.focus_force()

        overlay.bind("<Escape>", cancel_selection)
        canvas.bind("<Escape>", cancel_selection)

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

        overlay.after(100, lambda: canvas.focus_set())

    def select_tracker_template(self):
        self.stop_tracker()

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
            50,
            text="Arrastra sobre el objetivo exacto que quieres seguir | ESC cancela",
            fill="white",
            font=("Arial", 18, "bold")
        )

        data = {
            "start_x": 0,
            "start_y": 0,
            "rectangle": None
        }

        def cancel_selection(event=None):
            try:
                overlay.destroy()
            except Exception:
                pass

            self.update_tracker_status("Estado: Selección de objetivo cancelada", "#a6adc8")
            self.lift()
            self.focus_force()

        def on_press(event):
            data["start_x"] = event.x_root
            data["start_y"] = event.y_root

            if data["rectangle"]:
                canvas.delete(data["rectangle"])

            data["rectangle"] = canvas.create_rectangle(
                event.x,
                event.y,
                event.x,
                event.y,
                outline="#a6e3a1",
                width=3
            )

        def on_drag(event):
            if data["rectangle"]:
                canvas.coords(
                    data["rectangle"],
                    data["start_x"] - overlay.winfo_rootx(),
                    data["start_y"] - overlay.winfo_rooty(),
                    event.x,
                    event.y
                )

        def capture_template(x1, y1, x2, y2):
            try:
                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)

                width = x2 - x1
                height = y2 - y1

                if width < 8 or height < 8:
                    self.update_tracker_status(
                        "Estado: Objetivo demasiado pequeño",
                        "#f38ba8"
                    )
                    return

                try:
                    if TRACKER_TEMPLATE_FILE.exists():
                        TRACKER_TEMPLATE_FILE.unlink()
                except Exception:
                    pass

                with mss.MSS() as sct:
                    monitor = {
                        "left": x1,
                        "top": y1,
                        "width": width,
                        "height": height
                    }

                    shot = np.array(sct.grab(monitor))
                    template = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)

                if template is None or template.size == 0:
                    raise RuntimeError("captura vacía")

                saved_ok = cv2.imwrite(str(TRACKER_TEMPLATE_FILE), template)

                if not saved_ok:
                    raise RuntimeError("no se pudo guardar tracker_template.png")

                saved_template = cv2.imread(str(TRACKER_TEMPLATE_FILE), cv2.IMREAD_COLOR)

                if saved_template is None or saved_template.size == 0:
                    raise RuntimeError("no se pudo leer tracker_template.png")

                self.tracker_template = saved_template

                self.update_tracker_labels()
                self.update_tracker_status("Estado: Objetivo seleccionado", "#a6e3a1")
                self.save_config()

            except Exception as error:
                self.update_tracker_status(
                    f"Estado: Error al capturar objetivo: {str(error)[:65]}",
                    "#f38ba8"
                )

            self.lift()
            self.focus_force()

        def on_release(event):
            x1 = min(data["start_x"], event.x_root)
            y1 = min(data["start_y"], event.y_root)
            x2 = max(data["start_x"], event.x_root)
            y2 = max(data["start_y"], event.y_root)

            try:
                overlay.withdraw()
                overlay.update_idletasks()
                overlay.update()
            except Exception:
                pass

            def destroy_overlay():
                try:
                    overlay.destroy()
                except Exception:
                    pass

            self.after(700, lambda: capture_template(x1, y1, x2, y2))
            self.after(1000, destroy_overlay)

        overlay.bind("<Escape>", cancel_selection)
        canvas.bind("<Escape>", cancel_selection)

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

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


    def schedule_next_tracker_random_click(self):
        min_seconds = max(
            5,
            float(self.tracker_random_click_min_seconds)
        )

        max_seconds = max(
            min_seconds,
            float(self.tracker_random_click_max_seconds)
        )

        self.tracker_next_random_click_time = (
            time.perf_counter()
            + random.uniform(min_seconds, max_seconds)
        )

    def maybe_do_tracker_random_click(self):
        if not self.tracker_random_click_enabled:
            return

        if not self.tracker_running:
            return

        if self.tracker_next_random_click_time <= 0:
            self.schedule_next_tracker_random_click()
            return

        now = time.perf_counter()

        if now < self.tracker_next_random_click_time:
            return

        try:
            # Click izquierdo en la posición actual.
            # No mueve el cursor ni elige coordenadas aleatorias.
            self.click_mouse(
                button="left",
                clicks=1
            )

        except pyautogui.FailSafeException:
            raise

        except Exception:
            # Un fallo aislado del click no debe detener el Rastreador.
            pass

        finally:
            self.schedule_next_tracker_random_click()


    def start_tracker(self):
        if not self.tracker_area:
            self.update_tracker_status("Estado: Falta elegir zona", "#f38ba8")
            self.show_warning_once(
                "Zona no seleccionada",
                "Primero elige la zona donde aparecerá el objetivo."
            )
            return

        if self.tracker_template is None:
            self.update_tracker_status("Estado: Falta elegir objetivo", "#f38ba8")
            self.show_warning_once(
                "Objetivo no seleccionado",
                "Primero elige el objetivo que quieres rastrear."
            )
            return

        self.tracker_counter = 0
        self.tracker_last_speed_check = time.perf_counter()
        self.update_tracker_speed_label(0)

        self.tracker_running = True
        self.schedule_next_tracker_random_click()

        self.update_tracker_status("Estado: Buscando objetivo", "#a6e3a1")

        if self.start_tracker_button is not None:
            self.start_tracker_button.configure(
                fg_color="#a6e3a1",
                text_color="black"
            )

        if self.stop_tracker_button is not None:
            self.stop_tracker_button.configure(
                fg_color="#45475a",
                text_color="white"
            )

    def stop_tracker(self):
        self.tracker_running = False
        self.target_window_paused_modules.discard("tracker")
        self.target_window_stop_scheduled.discard("tracker")
        self.tracker_next_random_click_time = 0

        self.update_tracker_status("Estado: Rastreador detenido", "#a6adc8")
        self.update_tracker_speed_label(0)

        if self.start_tracker_button is not None:
            self.start_tracker_button.configure(
                fg_color="#1f6aa5",
                text_color="white"
            )

        if self.stop_tracker_button is not None:
            self.stop_tracker_button.configure(
                fg_color="#f38ba8",
                text_color="black"
            )

    def toggle_tracker(self):
        if self.tracker_running:
            self.stop_tracker()
        else:
            self.start_tracker()

    def clear_tracker(self):
        self.stop_tracker()

        self.tracker_area = None
        self.tracker_template = None

        try:
            if TRACKER_TEMPLATE_FILE.exists():
                TRACKER_TEMPLATE_FILE.unlink()
        except Exception:
            pass

        self.update_tracker_labels()
        self.update_tracker_status("Estado: Rastreador limpiado", "#f9e2af")
        self.save_config()


    def move_tracker_cursor_to(self, target_x, target_y):
        target_x = int(target_x)
        target_y = int(target_y)

        if not self.tracker_smooth_follow:
            self.move_cursor_to(target_x, target_y)
            return

        start_x, start_y = pyautogui.position()

        dx = target_x - start_x
        dy = target_y - start_y

        distance = max(abs(dx), abs(dy))

        if distance <= 1:
            self.move_cursor_to(target_x, target_y)
            return

        steps = max(3, min(24, int(distance / 18)))
        delay = max(
            0.001,
            min(0.008, 0.04 / max(1, self.tracker_speed_multiplier))
        )

        for step in range(1, steps + 1):
            if not self.tracker_running or self.stop_thread:
                return

            next_x = start_x + (dx * step / steps)
            next_y = start_y + (dy * step / steps)

            self.move_cursor_to(next_x, next_y)

            time.sleep(delay)


    def apply_tracker_unstick_if_needed(self, target_x, target_y):
        if not self.tracker_nudge_enabled:
            return

        target_x = int(target_x)
        target_y = int(target_y)

        try:
            current_x, current_y = pyautogui.position()
        except Exception:
            return

        cursor_near_target = (
            abs(current_x - target_x) <= 4
            and abs(current_y - target_y) <= 4
        )

        same_target = False

        if self.tracker_last_target is not None:
            last_x, last_y = self.tracker_last_target

            same_target = (
                abs(last_x - target_x) <= 5
                and abs(last_y - target_y) <= 5
            )

        if cursor_near_target and same_target:
            self.tracker_stuck_counter += 1
        else:
            self.tracker_stuck_counter = 0

        self.tracker_last_target = (target_x, target_y)

        if self.tracker_stuck_counter < 3:
            return

        self.tracker_stuck_counter = 0

        template_width = 0
        template_height = 0

        try:
            if self.tracker_template is not None:
                template_height, template_width = self.tracker_template.shape[:2]
        except Exception:
            pass

        dynamic_strength = max(
            self.tracker_unstick_strength,
            int(max(template_width, template_height) * 2.2),
            90
        )

        dynamic_strength = max(30, min(250, dynamic_strength))

        directions = [
            (dynamic_strength, 0),
            (-dynamic_strength, 0),
            (0, dynamic_strength),
            (0, -dynamic_strength),
            (dynamic_strength, dynamic_strength),
            (-dynamic_strength, dynamic_strength),
            (dynamic_strength, -dynamic_strength),
            (-dynamic_strength, -dynamic_strength)
        ]

        dx, dy = directions[
            self.tracker_unstick_direction_index % len(directions)
        ]

        self.tracker_unstick_direction_index += 1

        escape_x = target_x + dx
        escape_y = target_y + dy

        if self.tracker_area:
            x1, y1, x2, y2 = self.tracker_area

            escape_x = max(x1, min(x2, escape_x))
            escape_y = max(y1, min(y2, escape_y))

        try:
            self.move_cursor_to(int(escape_x), int(escape_y))
            time.sleep(0.06)
        except pyautogui.FailSafeException:
            raise
        except Exception:
            pass


    def tracker_loop(self):
        with mss.MSS() as sct:
            while not self.stop_thread:
                if self.tracker_running and self.tracker_area and self.tracker_template is not None:
                    if not self.can_execute_for_target_window("tracker"):
                        time.sleep(0.05)
                        continue

                    try:
                        x1, y1, x2, y2 = self.tracker_area

                        width = x2 - x1
                        height = y2 - y1

                        if width <= 0 or height <= 0:
                            self.tracker_running = False
                            self.after(0, self.stop_tracker)
                            continue

                        template = self.tracker_template
                        template_height, template_width = template.shape[:2]

                        if width < template_width or height < template_height:
                            self.tracker_running = False
                            self.after(0, self.stop_tracker)
                            self.after(
                                0,
                                lambda: self.update_tracker_status(
                                    "Estado: La zona es menor que el objetivo",
                                    "#f38ba8"
                                )
                            )
                            continue

                        monitor = {
                            "left": x1,
                            "top": y1,
                            "width": width,
                            "height": height
                        }

                        shot = np.array(sct.grab(monitor))
                        screen = cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)

                        result = cv2.matchTemplate(
                            screen,
                            template,
                            cv2.TM_CCOEFF_NORMED
                        )

                        _, max_value, _, max_location = cv2.minMaxLoc(result)

                        now = time.perf_counter()

                        if max_value >= self.tracker_confidence:
                            target_x = x1 + max_location[0] + template_width // 2
                            target_y = y1 + max_location[1] + template_height // 2

                            self.apply_tracker_unstick_if_needed(target_x, target_y)

                            self.move_tracker_cursor_to(target_x, target_y)

                            if self.tracker_nudge_enabled:
                                self.move_cursor_rel(2, 0)
                                self.move_cursor_rel(-2, 0)

                            if now - self.tracker_last_status_update >= 0.25:
                                confidence_percent = int(max_value * 100)
                                self.after(
                                    0,
                                    lambda value=confidence_percent: self.update_tracker_status(
                                        f"Estado: Objetivo encontrado ({value}%)",
                                        "#a6e3a1"
                                    )
                                )
                                self.tracker_last_status_update = now
                        else:
                            if now - self.tracker_last_status_update >= 0.5:
                                confidence_percent = int(max_value * 100)
                                self.after(
                                    0,
                                    lambda value=confidence_percent: self.update_tracker_status(
                                        f"Estado: Buscando objetivo ({value}%)",
                                        "#f9e2af"
                                    )
                                )
                                self.tracker_last_status_update = now

                        self.maybe_do_tracker_random_click()

                        self.tracker_counter += 1

                        elapsed = now - self.tracker_last_speed_check

                        if elapsed >= 1:
                            speed = int(self.tracker_counter / elapsed)

                            self.tracker_counter = 0
                            self.tracker_last_speed_check = now

                            self.after(
                                0,
                                lambda value=speed: self.update_tracker_speed_label(value)
                            )

                        delay = max(0.001, 0.08 / max(1, self.tracker_speed_multiplier))
                        time.sleep(delay)

                    except pyautogui.FailSafeException:
                        self.tracker_running = False

                        self.after(0, self.stop_tracker)
                        self.after(
                            0,
                            lambda: self.update_tracker_status(
                                "Estado: Rastreador detenido por failsafe",
                                "#f38ba8"
                            )
                        )

                    except Exception as error:
                        self.tracker_running = False
                        error_text = str(error)[:70]

                        self.after(0, self.stop_tracker)
                        self.after(
                            0,
                            lambda value=error_text: self.update_tracker_status(
                                f"Estado: Error en rastreador: {value}",
                                "#f38ba8"
                            )
                        )
                else:
                    time.sleep(0.01)


    def get_tracker_area_text(self):
        if not self.tracker_area:
            return "Zona de búsqueda: no seleccionada"

        x1, y1, x2, y2 = self.tracker_area
        return f"Zona de búsqueda: X1:{x1} Y1:{y1}  X2:{x2} Y2:{y2}"



    def get_tracker_summary_text(self):
        if self.tracker_area:
            x1, y1, x2, y2 = self.tracker_area
            area_text = f"Zona: {x1},{y1} → {x2},{y2}"
        else:
            area_text = "Zona: no seleccionada"

        if self.tracker_template is not None:
            height, width = self.tracker_template.shape[:2]
            template_text = f"Objetivo: {width}x{height}"
        else:
            template_text = "Objetivo: no seleccionado"

        return f"{area_text}   ·   {template_text}"



    def get_tracker_template_text(self):
        if self.tracker_template is None:
            return "Objetivo: no seleccionado"

        height, width = self.tracker_template.shape[:2]
        return f"Objetivo: plantilla cargada ({width}x{height})"

    def update_tracker_status(self, text, color="#a6adc8"):
        if self.tracker_status_label is not None:
            self.tracker_status_label.configure(
                text=text,
                text_color=color
            )

    def update_tracker_speed_label(self, speed):
        self.tracker_current_speed = speed

        if self.tracker_detection_speed_label is not None:
            self.tracker_detection_speed_label.configure(
                text=f"Velocidad: {speed} det/s"
            )


    def update_tracker_labels(self):
        if self.tracker_area_label is not None:
            tracker_ready = self.tracker_area is not None and self.tracker_template is not None

            self.tracker_area_label.configure(
                text=self.get_tracker_summary_text(),
                text_color="#a6e3a1" if tracker_ready else "#a6adc8"
            )

        if self.tracker_speed_label is not None:
            self.tracker_speed_label.configure(
                text=f"x{self.tracker_speed_multiplier}"
            )

        if self.tracker_confidence_label is not None:
            self.tracker_confidence_label.configure(
                text=f"{int(self.tracker_confidence * 100)}%"
            )

        if self.start_tracker_button is not None:
            self.start_tracker_button.configure(
                text=f"Iniciar ({self.tracker_hotkey.upper()})"
            )

        if self.stop_tracker_button is not None:
            self.stop_tracker_button.configure(
                text=f"Detener ({self.tracker_hotkey.upper()})"
            )


    def change_tracker_speed(self, value):
        self.tracker_speed_multiplier = int(round(float(value)))
        self.tracker_speed_multiplier = max(1, min(100, self.tracker_speed_multiplier))

        self.update_tracker_labels()
        self.save_config()

    def change_tracker_confidence(self, value):
        self.tracker_confidence = int(round(float(value))) / 100
        self.tracker_confidence = max(0.50, min(0.99, self.tracker_confidence))

        self.update_tracker_labels()
        self.save_config()

    def load_saved_tracker_area(self):
        saved_area = self.config.get("tracker_area")

        if (
            isinstance(saved_area, list)
            and len(saved_area) == 4
            and all(isinstance(value, int) for value in saved_area)
        ):
            self.tracker_area = tuple(saved_area)
            self.update_tracker_labels()


    def load_saved_tracker_template(self):
        try:
            if TRACKER_TEMPLATE_FILE.exists():
                template = cv2.imread(str(TRACKER_TEMPLATE_FILE), cv2.IMREAD_COLOR)

                if template is not None and template.size > 0:
                    self.tracker_template = template
                    self.update_tracker_labels()
        except Exception:
            self.tracker_template = None


    def start_keyboard_listener(self):
        def normalize_key(key):
            if isinstance(key, keyboard.KeyCode):
                return key.char.lower() if key.char else ""

            return str(key).replace("Key.", "").lower()

        def on_press(key):
            pressed = normalize_key(key)

            if self.capturing_tracker_hotkey:
                if pressed == "esc":
                    self.after(0, self.close_current_tracker_hotkey_window)
                    return

                if not pressed:
                    return

                if pressed in {
                    self.hotkey,
                    self.click_hotkey,
                    self.press_hotkey,
                    self.route_hotkey,
                    self.tracker_hotkey
                }:
                    if self.tracker_hotkey_status_label:
                        self.after(
                            0,
                            lambda: self.tracker_hotkey_status_label.configure(
                                text="Esa tecla ya está en uso",
                                text_color="#f38ba8"
                            )
                        )
                    return

                self.tracker_hotkey = pressed
                self.tracker_hotkey_is_down = False
                self.capturing_tracker_hotkey = False

                self.after(0, self.update_tracker_labels)
                self.after(0, self.refresh_general_settings_labels)
                self.after(0, self.save_config)

                if self.tracker_hotkey_status_label:
                    self.after(
                        0,
                        lambda: self.tracker_hotkey_status_label.configure(
                            text=f"Nueva hotkey: {self.tracker_hotkey.upper()}",
                            text_color="#a6e3a1"
                        )
                    )

                if self.tracker_hotkey_window:
                    self.after(1500, self.close_current_tracker_hotkey_window)

                return

            if self.capturing_route_record_key:
                if pressed == "esc":
                    self.after(0, self.close_current_route_record_key_window)
                    return

                if not pressed:
                    return

                if pressed == "enter":
                    if self.route_record_key_status_label:
                        self.after(
                            0,
                            lambda: self.route_record_key_status_label.configure(
                                text="ENTER se usa para guardar la ruta",
                                text_color="#f38ba8"
                            )
                        )
                    return

                if pressed in {
                    self.hotkey,
                    self.click_hotkey,
                    self.press_hotkey,
                    self.route_hotkey,
                    self.tracker_hotkey
                }:
                    if self.route_record_key_status_label:
                        self.after(
                            0,
                            lambda: self.route_record_key_status_label.configure(
                                text="Esa tecla ya se usa como hotkey",
                                text_color="#f38ba8"
                            )
                        )
                    return

                self.route_record_key = pressed
                self.capturing_route_record_key = False

                self.after(0, self.update_route_labels)
                self.after(0, self.refresh_general_settings_labels)
                self.after(0, self.save_config)

                if self.route_record_key_status_label:
                    self.after(
                        0,
                        lambda: self.route_record_key_status_label.configure(
                            text=f"Nueva tecla: {self.get_key_display(self.route_record_key)}",
                            text_color="#a6e3a1"
                        )
                    )

                if self.route_record_key_window:
                    self.after(1500, self.close_current_route_record_key_window)

                return

            if self.capturing_route_hotkey:
                if pressed == "esc":
                    self.after(0, self.close_current_route_hotkey_window)
                    return

                if pressed in {
                    self.hotkey,
                    self.click_hotkey,
                    self.press_hotkey,
                    self.route_hotkey,
                    self.tracker_hotkey
                }:
                    if self.route_hotkey_status_label:
                        self.after(
                            0,
                            lambda: self.route_hotkey_status_label.configure(
                                text="Esa tecla ya está en uso",
                                text_color="#f38ba8"
                            )
                        )
                    return

                self.route_hotkey = pressed
                self.route_hotkey_is_down = False
                self.capturing_route_hotkey = False

                self.after(0, self.update_route_labels)
                self.after(0, self.refresh_general_settings_labels)
                self.after(0, self.save_config)

                if self.route_hotkey_status_label:
                    self.after(
                        0,
                        lambda: self.route_hotkey_status_label.configure(
                            text=f"Nueva hotkey: {self.route_hotkey.upper()}",
                            text_color="#a6e3a1"
                        )
                    )

                if self.route_hotkey_window:
                    self.after(1500, self.close_current_route_hotkey_window)

                return

            if self.capturing_press_key:
                if pressed == "esc":
                    self.after(0, self.close_current_press_key_window)
                    return

                if pressed in {
                    self.hotkey,
                    self.click_hotkey,
                    self.press_hotkey,
                    self.route_hotkey,
                    self.tracker_hotkey
                }:
                    if self.press_key_status_label:
                        self.after(
                            0,
                            lambda: self.press_key_status_label.configure(
                                text="Esa tecla ya se usa como hotkey",
                                text_color="#f38ba8"
                            )
                        )
                    return

                self.press_key = pressed
                self.capturing_press_key = False

                self.after(0, self.update_press_labels)
                self.after(0, self.refresh_general_settings_labels)
                self.after(0, self.save_config)

                if self.press_key_status_label:
                    self.after(
                        0,
                        lambda: self.press_key_status_label.configure(
                            text=f"Nueva tecla: {self.press_key.upper()}",
                            text_color="#a6e3a1"
                        )
                    )

                if self.press_key_window:
                    self.after(1500, self.close_current_press_key_window)

                return


            if self.capturing_press_hotkey:
                if pressed == "esc":
                    self.after(0, self.close_current_press_hotkey_window)
                    return

                if pressed in {
                    self.hotkey,
                    self.click_hotkey,
                    self.press_hotkey,
                    self.route_hotkey,
                    self.tracker_hotkey
                }:
                    if self.press_hotkey_status_label:
                        self.after(
                            0,
                            lambda: self.press_hotkey_status_label.configure(
                                text="Esa tecla ya está en uso",
                                text_color="#f38ba8"
                            )
                        )
                    return

                self.press_hotkey = pressed
                self.press_hotkey_is_down = False
                self.capturing_press_hotkey = False

                self.after(0, self.update_press_labels)
                self.after(0, self.refresh_general_settings_labels)
                self.after(0, self.save_config)

                if self.press_hotkey_status_label:
                    self.after(
                        0,
                        lambda: self.press_hotkey_status_label.configure(
                            text=f"Nueva hotkey: {self.press_hotkey.upper()}",
                            text_color="#a6e3a1"
                        )
                    )

                if self.press_hotkey_window:
                    self.after(1500, self.close_current_press_hotkey_window)

                return

            if self.capturing_click_hotkey:
                if pressed == "esc":
                    self.after(0, self.close_current_click_hotkey_window)
                    return

                if pressed in {
                    self.hotkey,
                    self.click_hotkey,
                    self.press_hotkey,
                    self.route_hotkey,
                    self.tracker_hotkey
                }:
                    if self.click_hotkey_status_label:
                        self.after(
                            0,
                            lambda: self.click_hotkey_status_label.configure(
                                text="Esa tecla ya está en uso",
                                text_color="#f38ba8"
                            )
                        )
                    return

                self.click_hotkey = pressed
                self.click_hotkey_is_down = False
                self.capturing_click_hotkey = False

                self.after(0, self.update_click_hotkey_labels)
                self.after(0, self.refresh_general_settings_labels)
                self.after(0, self.save_config)

                if self.click_hotkey_status_label:
                    self.after(
                        0,
                        lambda: self.click_hotkey_status_label.configure(
                            text=f"Nueva tecla: {self.click_hotkey.upper()}",
                            text_color="#a6e3a1"
                        )
                    )

                if self.click_hotkey_window:
                    self.after(1500, self.close_current_click_hotkey_window)

                return
            
            if self.route_recorder_open:
                return

            if pressed == "esc" and not self.capturing_hotkey:
                self.after(0, self.stop_movement)
                self.after(0, self.stop_clicking)
                self.after(0, self.stop_pressing)
                self.after(0, self.stop_route)
                self.after(0, self.stop_tracker)
                return

            if self.capturing_hotkey:
                if pressed == "esc":
                    self.after(0, self.close_current_hotkey_window)
                    return

                if pressed in {
                    self.click_hotkey,
                    self.press_hotkey,
                    self.press_key,
                    self.route_hotkey,
                    self.tracker_hotkey
                }:
                    if self.hotkey_status_label:
                        self.after(
                            0,
                            lambda: self.hotkey_status_label.configure(
                                text="Esa tecla ya está en uso",
                                text_color="#f38ba8"
                            )
                        )
                    return

                self.hotkey = pressed
                self.hotkey_is_down = False
                self.capturing_hotkey = False

                self.after(0, self.update_hotkey_labels)
                self.after(0, self.refresh_general_settings_labels)
                self.after(0, self.save_config)

                if self.hotkey_status_label:
                    self.after(
                        0,
                        lambda: self.hotkey_status_label.configure(
                            text=f"Nueva tecla: {self.hotkey.upper()}",
                            text_color="#a6e3a1"
                        )
                    )

                if self.hotkey_window:
                    self.after(1500, self.close_current_hotkey_window)

                return

            if pressed == self.hotkey:
                if self.hotkey_is_down:
                    return

                self.hotkey_is_down = True
                self.after(0, self.toggle_movement)
                return

            if pressed == self.click_hotkey:
                if self.click_hotkey_is_down:
                    return

                self.click_hotkey_is_down = True
                self.after(0, self.toggle_clicking)
                return

            if pressed == self.press_hotkey:
                if self.press_hotkey_is_down:
                    return

                self.press_hotkey_is_down = True
                self.after(0, self.toggle_pressing)
                return
            
            if pressed == self.route_hotkey:
                if self.route_hotkey_is_down:
                    return

                self.route_hotkey_is_down = True
                self.after(0, self.toggle_route)
                return
            
            if pressed == self.tracker_hotkey:
                if self.tracker_hotkey_is_down:
                    return

                self.tracker_hotkey_is_down = True
                self.after(0, self.toggle_tracker)
                return

        def on_release(key):
            pressed = normalize_key(key)

            if pressed == self.hotkey:
                self.hotkey_is_down = False

            if pressed == self.click_hotkey:
                self.click_hotkey_is_down = False

            if pressed == self.press_hotkey:
                self.press_hotkey_is_down = False
            
            if pressed == self.route_hotkey:
                self.route_hotkey_is_down = False

            if pressed == self.tracker_hotkey:
                self.tracker_hotkey_is_down = False

        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        listener.daemon = True
        listener.start()

    def open_hotkey_window(self):
        if self.hotkey_window is not None:
            return

        if (
            self.click_hotkey_window is not None
            or self.press_key_window is not None
            or self.press_hotkey_window is not None
        ):
            return

        self.capturing_hotkey = True

        window_width = 420
        window_height = 180

        window = ctk.CTkToplevel(self)
        self.hotkey_window = window
        self.apply_icon_to_window(window)

        window.title("Hotkey setting")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            window,
            text="Presiona la nueva tecla de inicio/pausa",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(pady=(30, 10))

        self.hotkey_status_label = ctk.CTkLabel(
            window,
            text=f"Actual: {self.hotkey.upper()}",
            text_color="#a6adc8"
        )
        self.hotkey_status_label.pack(pady=4)

        close_button = ctk.CTkButton(
            window,
            text="Cancelar",
            command=self.close_current_hotkey_window
        )
        close_button.pack(pady=16)

        window.protocol("WM_DELETE_WINDOW", self.close_current_hotkey_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(100, window.lift)
        window.after(100, window.focus_force)


    





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


    def open_tracker_hotkey_window(self):
        if self.tracker_running:
            self.update_tracker_status(
                "Estado: Detén el rastreador antes de cambiar la hotkey",
                "#f9e2af"
            )
            return

        if self.capturing_tracker_hotkey:
            return

        if self.tracker_hotkey_window is not None:
            try:
                if self.tracker_hotkey_window.winfo_exists():
                    self.tracker_hotkey_window.lift()
                    self.tracker_hotkey_window.focus_force()
                    return
            except Exception:
                pass

            self.tracker_hotkey_window = None
            self.tracker_hotkey_status_label = None
            self.capturing_tracker_hotkey = False

        if (
            self.hotkey_window is not None
            or self.click_hotkey_window is not None
            or self.press_key_window is not None
            or self.press_hotkey_window is not None
            or self.route_hotkey_window is not None
            or self.route_record_key_window is not None
        ):
            return

        self.capturing_tracker_hotkey = True

        window_width = 430
        window_height = 195

        window = ctk.CTkToplevel(self)
        self.tracker_hotkey_window = window
        self.apply_icon_to_window(window)

        window.title("Hotkey de Rastreador")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            window,
            text="Presiona la nueva tecla para iniciar/detener Rastreador",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        label.pack(pady=(28, 10))

        self.tracker_hotkey_status_label = ctk.CTkLabel(
            window,
            text=f"Actual: {self.tracker_hotkey.upper()}",
            text_color="#a6adc8"
        )
        self.tracker_hotkey_status_label.pack(pady=4)

        hint = ctk.CTkLabel(
            window,
            text="No puede repetirse con otras hotkeys.",
            text_color="#6c7086",
            font=ctk.CTkFont(size=12)
        )
        hint.pack(pady=(4, 0))

        close_button = ctk.CTkButton(
            window,
            text="Cancelar",
            command=self.close_current_tracker_hotkey_window
        )
        close_button.pack(pady=14)

        window.protocol("WM_DELETE_WINDOW", self.close_current_tracker_hotkey_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(150, window.focus_force)

    def close_current_tracker_hotkey_window(self):
        window = self.tracker_hotkey_window

        self.tracker_hotkey_window = None
        self.tracker_hotkey_status_label = None
        self.capturing_tracker_hotkey = False

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


    

    def open_settings_window(self):
        if self.settings_window is not None:
            try:
                self.settings_window.lift()
                self.settings_window.focus_force()
            except Exception:
                pass
            return

        window_width = 420
        window_height = 310

        window = ctk.CTkToplevel(self)
        self.settings_window = window
        self.apply_icon_to_window(window)

        window.title(f"Ajustes - {APP_NAME}")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", self.keep_on_top)

        title = ctk.CTkLabel(
            window,
            text="Ajustes",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(22, 6))

        info = ctk.CTkLabel(
            window,
            text=(
                f"Hotkey Clicker: {self.click_hotkey.upper()}\n"
                f"Hotkey KeyPresser: {self.press_hotkey.upper()}\n"
                f"Hotkey Mover: {self.hotkey.upper()}\n"
                f"Hotkey Ruta: {self.route_hotkey.upper()}\n"
                f"Hotkey Rastreador: {self.tracker_hotkey.upper()}"
            ),
            text_color="#a6adc8",
            justify="center"
        )
        info.pack(pady=(0, 14))

        general_config_button = ctk.CTkButton(
            window,
            text="Configuración general",
            height=38,
            command=self.open_general_settings_window
        )
        general_config_button.pack(padx=30, pady=6, fill="x")

        about_button = ctk.CTkButton(
            window,
            text=f"Acerca de {APP_NAME}",
            height=38,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.open_about_window
        )
        about_button.pack(padx=30, pady=6, fill="x")

        close_button = ctk.CTkButton(
            window,
            text="Cerrar",
            height=38,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.close_settings_window
        )
        close_button.pack(padx=30, pady=(12, 6), fill="x")

        footer = ctk.CTkLabel(
            window,
            text=f"{APP_NAME} · Ajustes",
            text_color="#6c7086",
            font=ctk.CTkFont(size=12)
        )
        footer.pack(pady=(4, 0))

        window.protocol("WM_DELETE_WINDOW", self.close_settings_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(100, window.lift)
        window.after(100, window.focus_force)
    
    def close_settings_window(self):
        if self.settings_window is None:
            return

        try:
            self.settings_window.grab_release()
        except Exception:
            pass

        try:
            self.settings_window.destroy()
        except Exception:
            pass

        self.settings_window = None

        self.lift()
        self.focus_force()

    
    def open_general_settings_window(self):
        if self.general_settings_window is not None:
            try:
                self.general_settings_window.lift()
                self.general_settings_window.focus_force()
            except Exception:
                pass
            return

        window_width = 520
        window_height = 590

        window = ctk.CTkToplevel(self)
        self.general_settings_window = window
        self.apply_icon_to_window(window)

        window.title(f"Configuración general - {APP_NAME}")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        if self.settings_window is not None:
            window.transient(self.settings_window)
        else:
            window.transient(self)

        window.grab_set()
        window.attributes("-topmost", self.keep_on_top)

        title = ctk.CTkLabel(
            window,
            text="Configuración general",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(22, 4))

        info = ctk.CTkLabel(
            window,
            text="Configuraciones guardadas de Clicker, KeyPresser, Mover, Ruta y Rastreador.",
            text_color="#a6adc8"
        )
        info.pack(pady=(0, 10))

        content = ctk.CTkScrollableFrame(
            window,
            corner_radius=14,
            fg_color="#2b2b2b"
        )
        content.pack(padx=24, pady=(0, 10), fill="both", expand=True)

        # General
        general_frame = ctk.CTkFrame(content, corner_radius=12)
        general_frame.pack(padx=10, pady=(10, 8), fill="x")

        general_title = ctk.CTkLabel(
            general_frame,
            text="General",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        general_title.pack(anchor="w", padx=14, pady=(10, 6))

        self.general_keep_on_top_checkbox = ctk.CTkCheckBox(
            general_frame,
            text="Mantener ventana encima",
            command=self.toggle_general_keep_on_top
        )
        self.general_keep_on_top_checkbox.pack(anchor="w", padx=14, pady=(0, 12))

        if self.keep_on_top:
            self.general_keep_on_top_checkbox.select()

        # Ventana objetivo
        self.create_target_window_settings_section(content)

        # Modos Turbo
        turbo_frame = ctk.CTkFrame(content, corner_radius=12)
        turbo_frame.pack(padx=10, pady=8, fill="x")

        turbo_title = ctk.CTkLabel(
            turbo_frame,
            text="Modos Turbo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        turbo_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 8))

        def add_turbo_row(row, label_text, current_value, command):
            name_label = ctk.CTkLabel(
                turbo_frame,
                text=label_text
            )
            name_label.grid(row=row, column=0, sticky="w", padx=14, pady=6)

            checkbox = ctk.CTkCheckBox(
                turbo_frame,
                text="Activado",
                command=command
            )
            checkbox.grid(row=row, column=1, sticky="w", padx=10, pady=6)

            if current_value:
                checkbox.select()

            value_label = ctk.CTkLabel(
                turbo_frame,
                text="True" if current_value else "False",
                text_color="#a6adc8",
                width=45
            )
            value_label.grid(row=row, column=2, sticky="e", padx=14, pady=6)

            return checkbox, value_label

        self.general_click_turbo_checkbox, self.general_click_turbo_value_label = add_turbo_row(
            1,
            "Modo Turbo - Clicker",
            self.click_turbo_mode,
            self.toggle_general_click_turbo
        )

        self.general_press_turbo_checkbox, self.general_press_turbo_value_label = add_turbo_row(
            2,
            "Modo Turbo - KeyPresser",
            self.press_turbo_mode,
            self.toggle_general_press_turbo
        )

        turbo_frame.grid_columnconfigure(0, weight=1)

        # Hotkeys
        hotkeys_frame = ctk.CTkFrame(content, corner_radius=12)
        hotkeys_frame.pack(padx=10, pady=8, fill="x")

        hotkeys_title = ctk.CTkLabel(
            hotkeys_frame,
            text="Hotkeys",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        hotkeys_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 8))

        def add_hotkey_row(row, label_text, value_text, command):
            name_label = ctk.CTkLabel(
                hotkeys_frame,
                text=label_text
            )
            name_label.grid(row=row, column=0, sticky="w", padx=14, pady=6)

            value_label = ctk.CTkLabel(
                hotkeys_frame,
                text=value_text.upper(),
                text_color="#a6adc8",
                width=70
            )
            value_label.grid(row=row, column=1, sticky="w", padx=10, pady=6)

            button = ctk.CTkButton(
                hotkeys_frame,
                text="Cambiar",
                width=88,
                height=30,
                command=command
            )
            button.grid(row=row, column=2, sticky="e", padx=14, pady=6)

            return value_label

        self.general_click_hotkey_label = add_hotkey_row(
            1,
            "Hotkey - Clicker",
            self.click_hotkey,
            self.open_click_hotkey_window
        )

        self.general_press_hotkey_label = add_hotkey_row(
            2,
            "Hotkey - KeyPresser",
            self.press_hotkey,
            self.open_press_hotkey_window
        )

        self.general_movement_hotkey_label = add_hotkey_row(
            3,
            "Hotkey - Mover",
            self.hotkey,
            self.open_hotkey_window
        )

        self.general_route_hotkey_label = add_hotkey_row(
            4,
            "Hotkey - Ruta",
            self.route_hotkey,
            self.open_route_hotkey_window
        )

        self.general_tracker_hotkey_label = add_hotkey_row(
            5,
            "Hotkey - Rastreador",
            self.tracker_hotkey,
            self.open_tracker_hotkey_window
        )

        hotkeys_frame.grid_columnconfigure(0, weight=1)

        # KeyPresser
        press_frame = ctk.CTkFrame(content, corner_radius=12)
        press_frame.pack(padx=10, pady=8, fill="x")

        press_title = ctk.CTkLabel(
            press_frame,
            text="KeyPresser",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        press_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 8))

        press_key_name = ctk.CTkLabel(
            press_frame,
            text="Tecla seleccionada"
        )
        press_key_name.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))

        self.general_press_key_label = ctk.CTkLabel(
            press_frame,
            text=self.press_key.upper(),
            text_color="#a6adc8",
            width=90
        )
        self.general_press_key_label.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 12))

        press_key_button = ctk.CTkButton(
            press_frame,
            text="Cambiar",
            width=88,
            height=30,
            command=self.open_press_key_window
        )
        press_key_button.grid(row=1, column=2, sticky="e", padx=14, pady=(0, 12))

        press_frame.grid_columnconfigure(0, weight=1)

        # Mover
        mover_frame = ctk.CTkFrame(content, corner_radius=12)
        mover_frame.pack(padx=10, pady=8, fill="x")

        mover_title = ctk.CTkLabel(
            mover_frame,
            text="Mover",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        mover_title.pack(anchor="w", padx=14, pady=(10, 8))

        mode_row = ctk.CTkFrame(mover_frame, fg_color="transparent")
        mode_row.pack(padx=14, pady=(0, 8), fill="x")

        mode_label = ctk.CTkLabel(
            mode_row,
            text="Tipo de movimiento"
        )
        mode_label.pack(side="left")

        self.general_movement_mode_option = ctk.CTkOptionMenu(
            mode_row,
            values=["Aleatorio", "Horizontal", "Vertical", "Rebote", "Suave"],
            command=self.change_general_movement_mode,
            width=150
        )
        self.general_movement_mode_option.pack(side="right")
        self.general_movement_mode_option.set(self.movement_mode)

        movement_speed_row = ctk.CTkFrame(mover_frame, fg_color="transparent")
        movement_speed_row.pack(padx=14, pady=(0, 8), fill="x")

        movement_speed_header = ctk.CTkFrame(movement_speed_row, fg_color="transparent")
        movement_speed_header.pack(fill="x", pady=(0, 2))

        movement_speed_name = ctk.CTkLabel(
            movement_speed_header,
            text="Velocidad"
        )
        movement_speed_name.pack(side="left")

        self.general_movement_speed_label = ctk.CTkLabel(
            movement_speed_header,
            text=f"x{self.movement_speed}",
            text_color="#a6e3a1",
            width=70
        )
        self.general_movement_speed_label.pack(side="right")

        self.general_movement_speed_slider = ctk.CTkSlider(
            movement_speed_row,
            from_=0,
            to=1000,
            number_of_steps=1000,
            command=self.change_general_movement_speed
        )
        self.general_movement_speed_slider.pack(fill="x")
        self.general_movement_speed_slider.set(self.movement_speed)

        area_row = ctk.CTkFrame(mover_frame, fg_color="transparent")
        area_row.pack(padx=14, pady=(2, 6), fill="x")

        area_title = ctk.CTkLabel(
            area_row,
            text="Zona seleccionada"
        )
        area_title.pack(side="left")

        self.general_area_label = ctk.CTkLabel(
            mover_frame,
            text=self.get_area_text(),
            text_color="#a6adc8",
            wraplength=420,
            justify="left"
        )
        self.general_area_label.pack(anchor="w", padx=14, pady=(0, 8))

        area_buttons_row = ctk.CTkFrame(mover_frame, fg_color="transparent")
        area_buttons_row.pack(padx=14, pady=(0, 12), fill="x")

        choose_area_button = ctk.CTkButton(
            area_buttons_row,
            text="Elegir zona",
            height=32,
            command=self.choose_area_from_general_settings
        )
        choose_area_button.pack(side="left", fill="x", expand=True, padx=(0, 6))

        clear_area_button = ctk.CTkButton(
            area_buttons_row,
            text="Limpiar zona",
            height=32,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.clear_area_from_general_settings
        )
        clear_area_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Ruta
        route_frame = ctk.CTkFrame(content, corner_radius=12)
        route_frame.pack(padx=10, pady=8, fill="x")

        route_title = ctk.CTkLabel(
            route_frame,
            text="Ruta",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        route_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 8))

        route_record_label = ctk.CTkLabel(
            route_frame,
            text="Tecla para \niniciar/pausar grabación"
        )
        route_record_label.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))

        self.general_route_record_key_label = ctk.CTkLabel(
            route_frame,
            text=self.get_key_display(self.route_record_key),
            text_color="#a6adc8",
            width=90
        )
        self.general_route_record_key_label.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 12))

        route_record_button = ctk.CTkButton(
            route_frame,
            text="Cambiar",
            width=88,
            height=30,
            command=self.open_route_record_key_window
        )
        route_record_button.grid(row=1, column=2, sticky="e", padx=14, pady=(0, 12))

        route_frame.grid_columnconfigure(0, weight=1)

        # Rastreador
        tracker_frame = ctk.CTkFrame(content, corner_radius=12)
        tracker_frame.pack(padx=10, pady=8, fill="x")

        tracker_title = ctk.CTkLabel(
            tracker_frame,
            text="Rastreador",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tracker_title.pack(anchor="w", padx=14, pady=(10, 8))

        tracker_speed_row = ctk.CTkFrame(tracker_frame, fg_color="transparent")
        tracker_speed_row.pack(padx=14, pady=(0, 8), fill="x")

        tracker_speed_header = ctk.CTkFrame(tracker_speed_row, fg_color="transparent")
        tracker_speed_header.pack(fill="x", pady=(0, 2))

        tracker_speed_name = ctk.CTkLabel(
            tracker_speed_header,
            text="Velocidad"
        )
        tracker_speed_name.pack(side="left")

        self.general_tracker_speed_label = ctk.CTkLabel(
            tracker_speed_header,
            text=f"x{self.tracker_speed_multiplier}",
            text_color="#a6e3a1",
            width=45
        )
        self.general_tracker_speed_label.pack(side="right")

        self.general_tracker_speed_slider = ctk.CTkSlider(
            tracker_speed_row,
            from_=1,
            to=100,
            number_of_steps=99,
            command=self.change_general_tracker_speed
        )
        self.general_tracker_speed_slider.pack(fill="x")
        self.general_tracker_speed_slider.set(self.tracker_speed_multiplier)

        tracker_confidence_row = ctk.CTkFrame(tracker_frame, fg_color="transparent")
        tracker_confidence_row.pack(padx=14, pady=(0, 10), fill="x")

        tracker_confidence_header = ctk.CTkFrame(tracker_confidence_row, fg_color="transparent")
        tracker_confidence_header.pack(fill="x", pady=(0, 2))

        tracker_confidence_name = ctk.CTkLabel(
            tracker_confidence_header,
            text="Coincidencia mínima"
        )
        tracker_confidence_name.pack(side="left")

        self.general_tracker_confidence_label = ctk.CTkLabel(
            tracker_confidence_header,
            text=f"{int(self.tracker_confidence * 100)}%",
            text_color="#a6e3a1",
            width=45
        )
        self.general_tracker_confidence_label.pack(side="right")

        self.general_tracker_confidence_slider = ctk.CTkSlider(
            tracker_confidence_row,
            from_=50,
            to=99,
            number_of_steps=49,
            command=self.change_general_tracker_confidence
        )
        self.general_tracker_confidence_slider.pack(fill="x")
        self.general_tracker_confidence_slider.set(int(self.tracker_confidence * 100))

        self.general_tracker_smooth_checkbox = ctk.CTkCheckBox(
            tracker_frame,
            text="Desplazar cursor suavemente al objetivo",
            command=self.toggle_general_tracker_smooth
        )
        self.general_tracker_smooth_checkbox.pack(anchor="w", padx=14, pady=(0, 8))

        if self.tracker_smooth_follow:
            self.general_tracker_smooth_checkbox.select()

        self.general_tracker_nudge_checkbox = ctk.CTkCheckBox(
            tracker_frame,
            text="Micro movimiento al llegar para activar hover",
            command=self.toggle_general_tracker_nudge
        )
        self.general_tracker_nudge_checkbox.pack(
            anchor="w",
            padx=14,
            pady=(0, 8)
        )

        if self.tracker_nudge_enabled:
            self.general_tracker_nudge_checkbox.select()

        self.general_tracker_random_click_checkbox = ctk.CTkCheckBox(
            tracker_frame,
            text="Click anti-AFK cada 35–50 segundos",
            command=self.toggle_general_tracker_random_click
        )
        self.general_tracker_random_click_checkbox.pack(
            anchor="w",
            padx=14,
            pady=(0, 12)
        )

        if self.tracker_random_click_enabled:
            self.general_tracker_random_click_checkbox.select()

        self.general_settings_status_label = ctk.CTkLabel(
            window,
            text="",
            text_color="#a6adc8",
            font=ctk.CTkFont(size=12)
        )
        self.general_settings_status_label.pack(pady=(0, 4))

        bottom_row = ctk.CTkFrame(window, fg_color="transparent")
        bottom_row.pack(padx=24, pady=(6, 12), fill="x")

        reset_button = ctk.CTkButton(
            bottom_row,
            text="↺",
            width=44,
            height=36,
            fg_color="#f38ba8",
            hover_color="#eba0ac",
            text_color="black",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.reset_config
        )
        reset_button.pack(side="left")

        reset_hint = ctk.CTkLabel(
            bottom_row,
            text="Restablecer",
            text_color="#6c7086",
            font=ctk.CTkFont(size=11)
        )
        reset_hint.pack(side="left", padx=(8, 0))

        close_button = ctk.CTkButton(
            bottom_row,
            text="Cerrar",
            width=120,
            height=36,
            command=self.close_general_settings_window
        )
        close_button.pack(side="right")

        window.protocol("WM_DELETE_WINDOW", self.close_general_settings_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(100, window.lift)
        window.after(100, window.focus_force)
    
    def close_general_settings_window(self):
        if self.general_settings_window is None:
            return

        try:
            self.general_settings_window.grab_release()
        except Exception:
            pass

        try:
            self.general_settings_window.destroy()
        except Exception:
            pass

        self.general_settings_window = None

        self.general_keep_on_top_checkbox = None

        self.general_target_window_option = None
        self.general_target_window_status_label = None
        self.general_target_focus_checkbox = None
        self.general_target_auto_resume_checkbox = None

        self.general_click_turbo_checkbox = None
        self.general_press_turbo_checkbox = None
        self.general_movement_turbo_checkbox = None

        self.general_click_turbo_value_label = None
        self.general_press_turbo_value_label = None
        self.general_movement_turbo_value_label = None

        self.general_click_hotkey_label = None
        self.general_press_hotkey_label = None
        self.general_movement_hotkey_label = None
        self.general_route_hotkey_label = None
        self.general_route_record_key_label = None

        self.general_tracker_hotkey_label = None
        self.general_tracker_speed_label = None
        self.general_tracker_speed_slider = None
        self.general_tracker_confidence_label = None
        self.general_tracker_confidence_slider = None
        self.general_tracker_smooth_checkbox = None
        self.general_tracker_nudge_checkbox = None
        self.general_tracker_random_click_checkbox = None

        self.general_press_key_label = None
        self.general_movement_mode_option = None
        self.general_movement_speed_label = None
        self.general_movement_speed_slider = None
        self.general_area_label = None

        self.general_settings_status_label = None

        if self.settings_window is not None:
            try:
                self.settings_window.lift()
                self.settings_window.focus_force()
            except Exception:
                pass
        else:
            self.lift()
            self.focus_force()


    def change_general_tracker_speed(self, value):
        self.tracker_speed_multiplier = int(round(float(value)))
        self.tracker_speed_multiplier = max(1, min(100, self.tracker_speed_multiplier))

        if self.tracker_speed_slider is not None:
            self.tracker_speed_slider.set(self.tracker_speed_multiplier)

        self.update_tracker_labels()
        self.refresh_general_settings_labels()
        self.save_config()
        self.set_general_status("Velocidad de Rastreador actualizada.", "#a6e3a1")

    def change_general_tracker_confidence(self, value):
        self.tracker_confidence = int(round(float(value))) / 100
        self.tracker_confidence = max(0.50, min(0.99, self.tracker_confidence))

        if self.tracker_confidence_slider is not None:
            self.tracker_confidence_slider.set(int(self.tracker_confidence * 100))

        self.update_tracker_labels()
        self.refresh_general_settings_labels()
        self.save_config()
        self.set_general_status("Coincidencia de Rastreador actualizada.", "#a6e3a1")

    def toggle_general_tracker_smooth(self):
        if self.general_tracker_smooth_checkbox is None:
            return

        self.tracker_smooth_follow = bool(self.general_tracker_smooth_checkbox.get())

        self.refresh_general_settings_labels()
        self.save_config()
        self.set_general_status("Movimiento suave de Rastreador actualizado.", "#a6e3a1")

    def toggle_general_tracker_nudge(self):
        if self.general_tracker_nudge_checkbox is None:
            return

        self.tracker_nudge_enabled = bool(self.general_tracker_nudge_checkbox.get())

        self.refresh_general_settings_labels()
        self.save_config()
        self.set_general_status("Micro movimiento de Rastreador actualizado.", "#a6e3a1")


    def toggle_general_tracker_random_click(self):
        if self.general_tracker_random_click_checkbox is None:
            return

        self.tracker_random_click_enabled = bool(
            self.general_tracker_random_click_checkbox.get()
        )

        if self.tracker_random_click_enabled:
            if self.tracker_running:
                self.schedule_next_tracker_random_click()

            status_text = "Click anti-AFK de Rastreador activado."
        else:
            self.tracker_next_random_click_time = 0
            status_text = "Click anti-AFK de Rastreador desactivado."

        self.refresh_general_settings_labels()
        self.save_config()
        self.set_general_status(status_text, "#a6e3a1")


    def set_general_status(self, text, color="#a6adc8"):
        if self.general_settings_status_label is not None:
            self.general_settings_status_label.configure(
                text=text,
                text_color=color
            )


    def set_checkbox_state(self, checkbox, value):
        try:
            if checkbox is None:
                return

            if value:
                checkbox.select()
            else:
                checkbox.deselect()
        except Exception:
            pass

    def set_value_label(self, label, value):
        try:
            if label is not None:
                label.configure(
                    text="True" if value else "False",
                    text_color="#a6e3a1" if value else "#a6adc8"
                )
        except Exception:
            pass

    def refresh_general_settings_labels(self):
        if self.general_settings_window is None:
            return

        self.set_checkbox_state(
            self.general_keep_on_top_checkbox,
            self.keep_on_top
        )

        self.set_checkbox_state(
            self.general_target_focus_checkbox,
            self.target_window_focus_only
        )
        self.set_checkbox_state(
            self.general_target_auto_resume_checkbox,
            self.target_window_auto_resume
        )

        try:
            if self.general_target_window_option is not None:
                self.general_target_window_option.set(
                    self.get_selected_target_label()
                )
        except Exception:
            pass

        self.refresh_target_window_state()

        self.set_checkbox_state(
            self.general_click_turbo_checkbox,
            self.click_turbo_mode
        )
        self.set_value_label(
            self.general_click_turbo_value_label,
            self.click_turbo_mode
        )

        self.set_checkbox_state(
            self.general_press_turbo_checkbox,
            self.press_turbo_mode
        )
        self.set_value_label(
            self.general_press_turbo_value_label,
            self.press_turbo_mode
        )

        self.set_checkbox_state(
            self.general_movement_turbo_checkbox,
            self.turbo_mode
        )
        self.set_value_label(
            self.general_movement_turbo_value_label,
            self.turbo_mode
        )

        try:
            if self.general_click_hotkey_label is not None:
                self.general_click_hotkey_label.configure(
                    text=self.click_hotkey.upper()
                )
        except Exception:
            pass

        try:
            if self.general_press_hotkey_label is not None:
                self.general_press_hotkey_label.configure(
                    text=self.press_hotkey.upper()
                )
        except Exception:
            pass

        try:
            if self.general_movement_hotkey_label is not None:
                self.general_movement_hotkey_label.configure(
                    text=self.hotkey.upper()
                )
        except Exception:
            pass

        try:
            if self.general_route_hotkey_label is not None:
                self.general_route_hotkey_label.configure(
                    text=self.route_hotkey.upper()
                )
        except Exception:
            pass

        try:
            if self.general_route_record_key_label is not None:
                self.general_route_record_key_label.configure(
                    text=self.get_key_display(self.route_record_key)
                )
        except Exception:
            pass

        try:
            if self.general_tracker_hotkey_label is not None:
                self.general_tracker_hotkey_label.configure(
                    text=self.tracker_hotkey.upper()
                )
        except Exception:
            pass

        try:
            if self.general_tracker_speed_label is not None:
                self.general_tracker_speed_label.configure(
                    text=f"x{self.tracker_speed_multiplier}"
                )
        except Exception:
            pass

        try:
            if self.general_tracker_speed_slider is not None:
                self.general_tracker_speed_slider.set(self.tracker_speed_multiplier)
        except Exception:
            pass

        try:
            if self.general_tracker_confidence_label is not None:
                self.general_tracker_confidence_label.configure(
                    text=f"{int(self.tracker_confidence * 100)}%"
                )
        except Exception:
            pass

        try:
            if self.general_tracker_confidence_slider is not None:
                self.general_tracker_confidence_slider.set(
                    int(self.tracker_confidence * 100)
                )
        except Exception:
            pass

        self.set_checkbox_state(
            self.general_tracker_smooth_checkbox,
            self.tracker_smooth_follow
        )

        self.set_checkbox_state(
            self.general_tracker_nudge_checkbox,
            self.tracker_nudge_enabled
        )

        self.set_checkbox_state(
            self.general_tracker_random_click_checkbox,
            self.tracker_random_click_enabled
        )

        try:
            if self.general_press_key_label is not None:
                self.general_press_key_label.configure(
                    text=self.press_key.upper()
                )
        except Exception:
            pass

        try:
            if self.general_movement_mode_option is not None:
                self.general_movement_mode_option.set(self.movement_mode)
        except Exception:
            pass

        try:
            if self.general_movement_speed_label is not None:
                self.general_movement_speed_label.configure(
                    text=f"x{self.movement_speed}"
                )
        except Exception:
            pass

        try:
            if self.general_movement_speed_slider is not None:
                self.general_movement_speed_slider.set(self.movement_speed)
        except Exception:
            pass

        try:
            if self.general_area_label is not None:
                self.general_area_label.configure(
                    text=self.get_area_text(),
                    text_color="#a6e3a1" if self.area else "#a6adc8"
                )
        except Exception:
            pass

    def toggle_general_keep_on_top(self):
        if self.general_keep_on_top_checkbox is None:
            return

        self.set_keep_on_top(bool(self.general_keep_on_top_checkbox.get()))
        self.set_general_status("Mantener encima actualizado.", "#a6e3a1")












    def set_keep_on_top(self, value):
        self.keep_on_top = bool(value)

        try:
            self.attributes("-topmost", self.keep_on_top)
        except Exception:
            pass

        for checkbox in [
            self.topmost_checkbox if hasattr(self, "topmost_checkbox") else None,
            self.general_keep_on_top_checkbox
        ]:
            try:
                if checkbox is not None:
                    if self.keep_on_top:
                        checkbox.select()
                    else:
                        checkbox.deselect()
            except Exception:
                pass

        for window in [
            self.settings_window,
            self.general_settings_window,
            self.window_selector_window,
            self.about_window,
            self.close_dialog,
            self.hotkey_window,
            self.click_hotkey_window,
            self.press_key_window,
            self.press_hotkey_window,
            self.route_hotkey_window,
            self.route_record_key_window,
            self.tracker_hotkey_window
        ]:
            try:
                if window is not None and window.winfo_exists():
                    window.attributes("-topmost", self.keep_on_top)
            except Exception:
                pass

        self.refresh_general_settings_labels()
        self.save_config()
    
    def open_about_window(self):
        if self.about_window is not None:
            try:
                self.about_window.lift()
                self.about_window.focus_force()
            except Exception:
                pass
            return

        window_width = 420
        window_height = 370

        window = ctk.CTkToplevel(self)
        self.about_window = window
        self.apply_icon_to_window(window)

        window.title(f"Acerca de {APP_NAME}")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", self.keep_on_top)

        title = ctk.CTkLabel(
            window,
            text=APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(24, 4))

        version = ctk.CTkLabel(
            window,
            text=f"Versión {APP_VERSION}",
            text_color="#a6adc8",
            font=ctk.CTkFont(size=14)
        )
        version.pack(pady=(0, 14))

        description = ctk.CTkLabel(
            window,
            text=(
                "Herramienta de escritorio para automatizar\n"
                "clicks, teclas, movimiento, rutas grabadas y rastreo visual.\n\n"
                "Permite reproducir caminos del mouse con clicks registrados,\n"
                "seguir objetivos visuales por plantilla, usar hotkeys configurables,\n"
                "limitar la ejecución a una ventana objetivo y guardar ajustes localmente."
            ),
            text_color="#cdd6f4",
            justify="center"
        )
        description.pack(pady=(0, 16))

        author = ctk.CTkLabel(
            window,
            text="Desarrollado por Robert",
            text_color="#a6e3a1"
        )
        author.pack(pady=(0, 10))

        config_info = ctk.CTkLabel(
            window,
            text=f"Configuración local:\n{CONFIG_FILE}",
            text_color="#6c7086",
            font=ctk.CTkFont(size=11),
            justify="center",
            wraplength=360
        )
        config_info.pack(pady=(0, 18))

        close_button = ctk.CTkButton(
            window,
            text="Cerrar",
            height=36,
            command=self.close_about_window
        )
        close_button.pack(padx=30, fill="x")

        window.protocol("WM_DELETE_WINDOW", self.close_about_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(100, window.lift)
        window.after(100, window.focus_force)

    def close_about_window(self):
        if self.about_window is None:
            return

        try:
            self.about_window.grab_release()
        except Exception:
            pass

        try:
            self.about_window.destroy()
        except Exception:
            pass

        self.about_window = None

        if self.settings_window is not None:
            try:
                self.settings_window.lift()
                self.settings_window.focus_force()
            except Exception:
                pass
        else:
            self.lift()
            self.focus_force()


    def open_config_folder(self):
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            os.startfile(CONFIG_DIR)
            self.update_status("Estado: Carpeta abierta", "#a6e3a1")
        except Exception:
            self.show_warning_once(
                "Error",
                "No se pudo abrir la carpeta de configuración."
            )

    def reset_config(self):
        parent_window = (
            self.general_settings_window
            or self.settings_window
            or self
        )

        confirm = messagebox.askyesno(
            "Restablecer configuración",
            "¿Seguro que quieres borrar la configuración guardada?\n\nLa app se cerrará después de hacerlo.",
            parent=parent_window
        )

        if not confirm:
            return

        try:
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
        except Exception:
            self.show_warning_once(
                "Error",
                "No se pudo borrar la configuración."
            )
            return

        self.skip_save_on_close = True
        self.close_app()

    def close_current_hotkey_window(self):
        if self.hotkey_window is None:
            return

        try:
            self.hotkey_window.grab_release()
        except Exception:
            pass

        try:
            self.hotkey_window.destroy()
        except Exception:
            pass

        self.hotkey_window = None
        self.hotkey_status_label = None
        self.capturing_hotkey = False

        self.lift()
        self.focus_force()


    def update_hotkey_labels(self):
        self.start_button.configure(text=f"Iniciar ({self.hotkey.upper()})")
        self.stop_button.configure(text=f"Detener ({self.hotkey.upper()})")


    def create_tray_image(self):
        try:
            if ICON_PATH.exists():
                icon = Image.open(ICON_PATH).convert("RGBA")
                icon.thumbnail((64, 64), Image.LANCZOS)

                image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))

                x = (64 - icon.width) // 2
                y = (64 - icon.height) // 2

                image.paste(icon, (x, y), icon)

                return image
        except Exception:
            pass

        image = Image.new("RGBA", (64, 64), (30, 30, 46, 255))
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle(
            (8, 8, 56, 56),
            radius=12,
            fill=(137, 180, 250, 255)
        )

        draw.text(
            (17, 22),
            "M",
            fill=(30, 30, 46, 255)
        )

        return image
    
    def handle_close_request(self):
        if self.close_dialog is not None:
            try:
                self.close_dialog.lift()
                self.close_dialog.focus_force()
            except Exception:
                pass
            return

        dialog_width = 360
        dialog_height = 175

        dialog = ctk.CTkToplevel(self)
        self.close_dialog = dialog
        self.apply_icon_to_window(dialog)

        dialog.title(f"Cerrar {APP_NAME}")
        dialog.geometry(f"{dialog_width}x{dialog_height}")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#242424")

        dialog.transient(self)
        dialog.grab_set()
        dialog.attributes("-topmost", self.keep_on_top)

        title = ctk.CTkLabel(
            dialog,
            text=f"¿Qué quieres hacer con {APP_NAME}?",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(24, 6))

        subtitle = ctk.CTkLabel(
            dialog,
            text="Puedes dejarla en segundo plano o cerrarla por completo.",
            text_color="#a6adc8",
            font=ctk.CTkFont(size=12)
        )
        subtitle.pack(pady=(0, 18))

        buttons_row = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_row.pack(padx=20, pady=(0, 18), fill="x")

        def close_dialog_only():
            try:
                dialog.grab_release()
            except Exception:
                pass

            self.close_dialog = None
            dialog.destroy()

            self.lift()
            self.focus_force()

        def minimize_app():
            close_dialog_only()
            self.hide_to_tray()

        def exit_app():
            try:
                dialog.grab_release()
            except Exception:
                pass

            self.close_dialog = None
            dialog.destroy()
            self.close_app()

        exit_button = ctk.CTkButton(
            buttons_row,
            text="Salir",
            height=36,
            fg_color="#f38ba8",
            hover_color="#eba0ac",
            text_color="black",
            command=exit_app
        )
        exit_button.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        minimize_button = ctk.CTkButton(
            buttons_row,
            text="Minimizar",
            height=36,
            command=minimize_app
        )
        minimize_button.grid(row=0, column=1, padx=8, sticky="ew")

        cancel_button = ctk.CTkButton(
            buttons_row,
            text="Cancelar",
            height=36,
            fg_color="#45475a",
            hover_color="#585b70",
            command=close_dialog_only
        )
        cancel_button.grid(row=0, column=2, padx=(8, 0), sticky="ew")

        buttons_row.grid_columnconfigure(0, weight=1)
        buttons_row.grid_columnconfigure(1, weight=1)
        buttons_row.grid_columnconfigure(2, weight=1)

        dialog.protocol("WM_DELETE_WINDOW", close_dialog_only)

        self.center_window(
            dialog,
            dialog_width,
            dialog_height,
            self.center_offset_x,
            self.center_offset_y
        )

        dialog.after(100, dialog.lift)
        dialog.after(100, dialog.focus_force)

    def hide_to_tray(self):
        self.save_config()
        self.withdraw()

        if self.tray_icon is not None:
            return

        menu = pystray.Menu(
            pystray.MenuItem(
                f"Mostrar {APP_NAME}",
                lambda icon, item: self.after(0, self.show_from_tray)
            ),
            pystray.MenuItem(
                "Iniciar / Detener movimiento",
                lambda icon, item: self.after(0, self.toggle_movement)
            ),
            pystray.MenuItem(
                "Iniciar / Detener clicks",
                lambda icon, item: self.after(0, self.toggle_clicking)
            ),
            pystray.MenuItem(
                "Iniciar / Detener AutoPresser",
                lambda icon, item: self.after(0, self.toggle_pressing)
            ),
            pystray.MenuItem(
                "Iniciar / Detener ruta",
                lambda icon, item: self.after(0, self.toggle_route)
            ),
            pystray.MenuItem(
                "Iniciar / Detener rastreador",
                lambda icon, item: self.after(0, self.toggle_tracker)
            ),
            pystray.MenuItem(
                "Salir",
                lambda icon, item: self.after(0, self.exit_from_tray)
            )
        )

        self.tray_icon = pystray.Icon(
            APP_NAME,
            self.create_tray_image(),
            APP_NAME,
            menu
        )

        threading.Thread(
            target=self.tray_icon.run,
            daemon=True
        ).start()


    def show_from_tray(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", self.keep_on_top)


    def exit_from_tray(self):
        self.closing_from_tray = True

        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass

            self.tray_icon = None

        self.close_app()


    def close_app(self):
        if not self.skip_save_on_close:
            self.save_config()

        self.stop_thread = True
        self.running = False
        self.click_running = False
        self.press_running = False
        self.route_running = False
        self.route_recorder_open = False
        self.tracker_running = False
        self.stop_route_game_listeners()
        self.close_route_game_hud()

        try:
            self.close_window_selector()
        except Exception:
            pass

        try:
            if self.hotkey_window is not None:
                self.hotkey_window.destroy()
        except Exception:
            pass

        try:
            self.close_current_click_hotkey_window()
        except Exception:
            pass

        try:
            self.close_current_press_key_window()
        except Exception:
            pass

        try:
            self.close_current_press_hotkey_window()
        except Exception:
            pass

        try:
            self.close_current_route_hotkey_window()
        except Exception:
            pass

        try:
            self.close_current_route_record_key_window()
        except Exception:
            pass

        try:
            self.close_current_tracker_hotkey_window()
        except Exception:
            pass

        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass

            self.tray_icon = None

        try:
            if self.settings_window is not None:
                self.settings_window.destroy()
        except Exception:
            pass

        try:
            if self.general_settings_window is not None:
                self.general_settings_window.destroy()
        except Exception:
            pass

        try:
            if self.about_window is not None:
                self.about_window.destroy()
        except Exception:
            pass

        try:
            if self.close_dialog is not None:
                self.close_dialog.destroy()
        except Exception:
            pass

        self.destroy()

if __name__ == "__main__":
    app = AutoInputR()
    app.mainloop()