import threading
import time
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageTk
import customtkinter as ctk
import pyautogui

from autoinputr.core.resources import (
    APP_NAME,
    APP_VERSION,
    ICON_PATH,
    ICON_ICO_PATH,
)

from autoinputr.core.config import (
    load_config_file,
    save_config_file,
)

from autoinputr.core.target_window import TargetWindowMixin
from autoinputr.services.input_backend import (
    HAS_PYDIRECTINPUT,
    InputBackendMixin,
)

from autoinputr.modules.keypresser import KeyPresserMixin
from autoinputr.modules.clicker import ClickerMixin
from autoinputr.modules.mover import MoverMixin
from autoinputr.modules.ruta import RutaMixin
from autoinputr.modules.rastreador import RastreadorMixin
from autoinputr.core.hotkeys import HotkeysMixin
from autoinputr.ui.dialogs.window_selector import WindowSelectorMixin
from autoinputr.ui.dialogs.settings import SettingsMixin
from autoinputr.services.tray import TrayMixin

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)


class AutoInputR(RutaMixin, RastreadorMixin, KeyPresserMixin, ClickerMixin, MoverMixin, HotkeysMixin, WindowSelectorMixin, SettingsMixin, TrayMixin, TargetWindowMixin, InputBackendMixin, ctk.CTk):
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

    




    # ------------------------------------------------------------------
    # Ventana objetivo (AutoInputR v1.3)
    # ------------------------------------------------------------------



























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

    def toggle_topmost(self):
        if hasattr(self, "topmost_checkbox"):
            self.set_keep_on_top(bool(self.topmost_checkbox.get()))
