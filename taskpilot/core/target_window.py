"""
Logica de proteccion por ventana objetivo de TaskPilot.

Este mixin mantiene el estado y las reglas de la ventana
seleccionada, mientras que las operaciones Win32 de bajo
nivel viven en taskpilot.services.windows.
"""

import os
import sys
import time

from taskpilot.services.windows import (
    enumerate_visible_windows,
    get_foreground_window,
    get_process_name_from_pid as win_get_process_name_from_pid,
    get_window_info as win_get_window_info,
    is_window,
    is_window_minimized,
)


class TargetWindowMixin:
    def has_target_window(self):
        return bool(
            self.target_window_title
            or self.target_window_process
            or self.target_window_class
        )

    def get_process_name_from_pid(self, pid):
        return win_get_process_name_from_pid(pid)

    def get_window_info(self, hwnd):
        return win_get_window_info(hwnd)

    def enumerate_target_windows(self):
        windows = enumerate_visible_windows(
            exclude_pid=os.getpid()
        )

        label_map = {}

        for info in windows:
            title = info.get(
                "title",
                "Ventana"
            )

            process_name = (
                info.get(
                    "process",
                    ""
                )
                or "Proceso desconocido"
            )

            if len(title) > 58:
                title = (
                    title[:55]
                    + "..."
                )

            base_label = (
                f"{title}  ·  "
                f"{process_name}"
            )

            label = base_label

            if label in label_map:
                label = (
                    f"{base_label}  "
                    f"[{info['hwnd']}]"
                )

            info["label"] = label
            label_map[label] = info

        self.available_target_windows = (
            windows
        )

        self.target_window_label_map = (
            label_map
        )

        return windows

    def target_window_matches(self, info):
        if not info or not self.has_target_window():
            return False

        saved_process = self.target_window_process.lower().strip()
        saved_class = self.target_window_class.lower().strip()
        saved_title = self.target_window_title.strip()

        current_process = str(info.get("process", "")).lower().strip()
        current_class = str(info.get("class", "")).lower().strip()
        current_title = str(info.get("title", "")).strip()

        if saved_process and saved_class:
            if saved_process == current_process and saved_class == current_class:
                if not saved_title or saved_title == current_title:
                    return True

        if saved_process and saved_title:
            if saved_process == current_process and saved_title == current_title:
                return True

        if saved_title and saved_title == current_title:
            return True

        return False

    def resolve_saved_target_window(self, force=False):
        if not self.has_target_window():
            self.target_window_hwnd = 0
            return 0

        try:
            if sys.platform == "win32" and self.target_window_hwnd:
                if is_window(self.target_window_hwnd):
                    info = self.get_window_info(self.target_window_hwnd)

                    if self.target_window_matches(info):
                        return int(self.target_window_hwnd)
        except Exception:
            pass

        self.target_window_hwnd = 0

        now = time.perf_counter()

        if (
            not force
            and now - self.target_window_last_resolve_attempt < 1.0
        ):
            return 0

        self.target_window_last_resolve_attempt = now
        windows = self.enumerate_target_windows()

        # Coincidencia exacta primero.
        for info in windows:
            if self.target_window_matches(info):
                self.target_window_hwnd = int(info["hwnd"])
                return self.target_window_hwnd

        # Si el título cambió, intenta recuperar por proceso + clase.
        saved_process = self.target_window_process.lower().strip()
        saved_class = self.target_window_class.lower().strip()

        if saved_process and saved_class:
            for info in windows:
                if (
                    str(info.get("process", "")).lower().strip() == saved_process
                    and str(info.get("class", "")).lower().strip() == saved_class
                ):
                    self.target_window_hwnd = int(info["hwnd"])
                    self.target_window_title = str(info.get("title", ""))
                    return self.target_window_hwnd

        return 0

    def set_target_window(self, info, status_message=True):
        if not info:
            return

        self.target_window_hwnd = int(info.get("hwnd", 0) or 0)
        self.target_window_last_resolve_attempt = time.perf_counter()
        self.target_window_title = str(info.get("title", "") or "")
        self.target_window_process = str(info.get("process", "") or "")
        self.target_window_class = str(info.get("class", "") or "")
        self.target_window_paused_modules.clear()
        self.target_window_stop_scheduled.clear()

        self.save_config()
        self.refresh_target_window_controls()
        self.refresh_target_window_state()

        if status_message:
            self.set_general_status(
                f"Ventana objetivo: {self.get_target_window_display_name()}",
                "#a6e3a1"
            )

    def clear_target_window(self):
        self.target_window_hwnd = 0
        self.target_window_last_resolve_attempt = 0.0
        self.target_window_title = ""
        self.target_window_process = ""
        self.target_window_class = ""
        self.target_window_paused_modules.clear()
        self.target_window_stop_scheduled.clear()

        self.save_config()
        self.refresh_target_window_controls()
        self.refresh_target_window_state()
        self.set_general_status("Ventana objetivo eliminada.", "#f9e2af")

    def get_target_window_display_name(self):
        if not self.has_target_window():
            return "Sin ventana seleccionada"

        title = self.target_window_title or self.target_window_process

        if len(title) > 42:
            title = title[:39] + "..."

        return title

    def get_selected_target_label(self):
        if not self.has_target_window():
            return "Selecciona una ventana..."

        for label, info in self.target_window_label_map.items():
            if self.target_window_matches(info):
                return label

        process_name = self.target_window_process or "Proceso desconocido"
        return f"{self.get_target_window_display_name()}  ·  {process_name}"

    def get_target_window_state(self):
        if not self.has_target_window():
            return True, "none", "Sin ventana objetivo"

        if sys.platform != "win32":
            return False, "unsupported", "Selector disponible solo en Windows"

        hwnd = self.resolve_saved_target_window()

        if not hwnd:
            return False, "unavailable", "Ventana objetivo no disponible"

        try:
            if is_window_minimized(hwnd):
                return False, "minimized", "Ventana objetivo minimizada"

            if self.target_window_focus_only:
                foreground = get_foreground_window()

                if foreground != int(hwnd):
                    return False, "inactive", "Ventana objetivo sin foco"

                return True, "active", "Ventana objetivo activa"

            return True, "available", "Protección por foco desactivada"
        except Exception:
            return False, "unavailable", "No se pudo comprobar la ventana"

    def refresh_target_window_state(self):
        ready, state_code, state_text = self.get_target_window_state()
        self.target_window_state_code = state_code
        self.target_window_state_text = state_text

        button = self.window_selector_button

        if button is not None:
            try:
                if state_code == "none":
                    button.configure(
                        fg_color="#45475a",
                        hover_color="#585b70",
                        text_color="white"
                    )
                elif state_code == "available":
                    button.configure(
                        fg_color="#1f6aa5",
                        hover_color="#2f7db7",
                        text_color="white"
                    )
                elif ready:
                    button.configure(
                        fg_color="#a6e3a1",
                        hover_color="#94d89a",
                        text_color="black"
                    )
                elif state_code in {"inactive", "minimized"}:
                    button.configure(
                        fg_color="#f9e2af",
                        hover_color="#eed49f",
                        text_color="black"
                    )
                else:
                    button.configure(
                        fg_color="#f38ba8",
                        hover_color="#eba0ac",
                        text_color="black"
                    )
            except Exception:
                pass

        status_text = state_text

        if self.has_target_window():
            status_text = f"{self.get_target_window_display_name()} · {state_text}"

        for label in [
            self.window_selector_status_label,
            self.general_target_window_status_label
        ]:
            try:
                if label is not None:
                    label.configure(
                        text=status_text,
                        text_color=(
                            "#a6e3a1" if ready and state_code != "none"
                            else "#a6adc8" if state_code == "none"
                            else "#f9e2af" if state_code in {"inactive", "minimized"}
                            else "#f38ba8"
                        )
                    )
            except Exception:
                pass

        return ready

    def refresh_target_window_state_loop(self):
        if self.stop_thread:
            return

        self.refresh_target_window_state()

        try:
            self.after(500, self.refresh_target_window_state_loop)
        except Exception:
            pass

    def refresh_target_window_list(self):
        self.enumerate_target_windows()
        values = list(self.target_window_label_map.keys())

        if not values:
            values = ["No hay ventanas visibles disponibles"]

        selected_label = self.get_selected_target_label()

        for option in [
            self.window_selector_option,
            self.general_target_window_option
        ]:
            try:
                if option is not None:
                    option.configure(values=values)
                    option.set(selected_label)
            except Exception:
                pass

        self.refresh_target_window_state()

    def refresh_target_window_controls(self):
        self.refresh_target_window_list()

        self.set_checkbox_state(
            self.window_selector_focus_checkbox,
            self.target_window_focus_only
        )
        self.set_checkbox_state(
            self.window_selector_auto_resume_checkbox,
            self.target_window_auto_resume
        )
        self.set_checkbox_state(
            self.general_target_focus_checkbox,
            self.target_window_focus_only
        )
        self.set_checkbox_state(
            self.general_target_auto_resume_checkbox,
            self.target_window_auto_resume
        )

    def choose_target_window_from_label(self, selected_label):
        info = self.target_window_label_map.get(selected_label)

        if info is None:
            return

        self.set_target_window(info)

    def toggle_target_focus_only(self):
        checkbox = (
            self.window_selector_focus_checkbox
            if self.window_selector_focus_checkbox is not None
            else self.general_target_focus_checkbox
        )

        if checkbox is None:
            return

        self.target_window_focus_only = bool(checkbox.get())
        self.target_window_paused_modules.clear()
        self.target_window_stop_scheduled.clear()
        self.save_config()
        self.refresh_target_window_controls()
        self.set_general_status("Protección por foco actualizada.", "#a6e3a1")

    def toggle_target_auto_resume(self):
        checkbox = (
            self.window_selector_auto_resume_checkbox
            if self.window_selector_auto_resume_checkbox is not None
            else self.general_target_auto_resume_checkbox
        )

        if checkbox is None:
            return

        self.target_window_auto_resume = bool(checkbox.get())
        self.target_window_paused_modules.clear()
        self.target_window_stop_scheduled.clear()
        self.save_config()
        self.refresh_target_window_controls()
        self.set_general_status("Reanudación automática actualizada.", "#a6e3a1")

    def capture_foreground_target_window(self):
        if sys.platform != "win32":
            self.set_general_status("Esta función solo está disponible en Windows.", "#f38ba8")
            return

        selector = self.window_selector_window
        general = self.general_settings_window

        try:
            if selector is not None:
                selector.grab_release()
                selector.withdraw()
        except Exception:
            pass

        try:
            if general is not None:
                general.grab_release()
                general.withdraw()
        except Exception:
            pass

        try:
            self.attributes("-topmost", False)
            self.withdraw()
        except Exception:
            pass

        def capture_now():
            info = None

            try:
                hwnd = get_foreground_window()
                info = self.get_window_info(hwnd)

                if info and info.get("pid") == os.getpid():
                    info = None
            except Exception:
                info = None

            try:
                self.deiconify()
                self.attributes("-topmost", self.keep_on_top)
                self.lift()
            except Exception:
                pass

            try:
                if selector is not None and selector.winfo_exists():
                    selector.deiconify()
                    selector.grab_set()
                    selector.lift()
                    selector.focus_force()
            except Exception:
                pass

            try:
                if general is not None and general.winfo_exists():
                    general.deiconify()
                    general.grab_set()
                    general.lift()
                    general.focus_force()
            except Exception:
                pass

            if info and info.get("title"):
                self.set_target_window(info)
            else:
                self.set_general_status(
                    "No se pudo capturar una ventana externa.",
                    "#f38ba8"
                )

        self.after(2500, capture_now)

    def get_target_pause_reason(self):
        _ready, state_code, state_text = self.get_target_window_state()

        if state_code == "inactive":
            return f"activa {self.get_target_window_display_name()}"
        if state_code == "minimized":
            return "restaura la ventana objetivo"
        if state_code == "unavailable":
            return "abre la ventana objetivo"

        return state_text.lower()

    def update_module_window_pause_status(self, module_name, stopped=False):
        prefix = "Detenido" if stopped else "Pausado"
        reason = self.get_target_pause_reason()
        text = f"Estado: {prefix} · {reason}"
        color = "#f38ba8" if stopped else "#f9e2af"

        if module_name == "movement":
            self.update_status(text, color)
            self.update_speed_label(0)
        elif module_name == "click":
            self.update_click_status(text, color)
            self.update_click_speed_label(0)
        elif module_name == "press":
            self.update_press_status(text, color)
            self.update_press_speed_label(0)
        elif module_name == "route":
            self.update_route_status(text, color)
            self.update_route_play_speed_label(0)
        elif module_name == "tracker":
            self.update_tracker_status(text, color)
            self.update_tracker_speed_label(0)

    def update_module_window_resume_status(self, module_name):
        if module_name == "movement" and self.running:
            self.update_status("Estado: Moviendo cursor", "#a6e3a1")
        elif module_name == "click" and self.click_running:
            self.update_click_status("Estado: Ejecutando clicks", "#a6e3a1")
        elif module_name == "press" and self.press_running:
            self.update_press_status("Estado: Presionando tecla", "#a6e3a1")
        elif module_name == "route" and self.route_running:
            self.update_route_status("Estado: Reproduciendo ruta", "#a6e3a1")
        elif module_name == "tracker" and self.tracker_running:
            self.update_tracker_status("Estado: Buscando objetivo", "#a6e3a1")

    def stop_module_for_target_window(self, module_name):
        if module_name == "movement":
            self.stop_movement()
        elif module_name == "click":
            self.stop_clicking()
        elif module_name == "press":
            self.stop_pressing()
        elif module_name == "route":
            self.stop_route()
        elif module_name == "tracker":
            self.stop_tracker()

        self.update_module_window_pause_status(module_name, stopped=True)
        self.target_window_stop_scheduled.discard(module_name)

    def can_execute_for_target_window(self, module_name):
        if not self.has_target_window() or not self.target_window_focus_only:
            if module_name in self.target_window_paused_modules:
                self.target_window_paused_modules.discard(module_name)
                self.after(
                    0,
                    lambda name=module_name: self.update_module_window_resume_status(name)
                )
            return True

        ready, _state_code, _state_text = self.get_target_window_state()

        if ready:
            self.target_window_stop_scheduled.discard(module_name)

            if module_name in self.target_window_paused_modules:
                self.target_window_paused_modules.discard(module_name)
                self.after(
                    0,
                    lambda name=module_name: self.update_module_window_resume_status(name)
                )

            return True

        if self.target_window_auto_resume:
            if module_name not in self.target_window_paused_modules:
                self.target_window_paused_modules.add(module_name)
                self.after(
                    0,
                    lambda name=module_name: self.update_module_window_pause_status(name)
                )

            return False

        if module_name not in self.target_window_stop_scheduled:
            self.target_window_stop_scheduled.add(module_name)
            self.after(
                0,
                lambda name=module_name: self.stop_module_for_target_window(name)
            )

        return False
