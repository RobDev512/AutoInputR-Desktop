"""
Modulo Rastreador de AutoInputR.

Agrupa la interfaz, captura de plantilla, deteccion visual,
seguimiento del cursor y opciones del rastreador.
"""

import random
import time
import tkinter as tk

import customtkinter as ctk
import mss
import pyautogui

from autoinputr.core.resources import TRACKER_TEMPLATE_FILE
from autoinputr.services.vision import (
    capture_bgr_region,
    load_bgr_image,
    match_template,
    save_bgr_image,
)


class RastreadorMixin:
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
                    template = capture_bgr_region(
                        sct,
                        x1,
                        y1,
                        width,
                        height,
                    )

                if template is None or template.size == 0:
                    raise RuntimeError("captura vacía")

                saved_ok = save_bgr_image(
                    TRACKER_TEMPLATE_FILE,
                    template,
                )

                if not saved_ok:
                    raise RuntimeError("no se pudo guardar tracker_template.png")

                saved_template = load_bgr_image(
                    TRACKER_TEMPLATE_FILE
                )

                if saved_template is None:
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

                        screen = capture_bgr_region(
                            sct,
                            x1,
                            y1,
                            width,
                            height,
                        )

                        max_value, max_location = match_template(
                            screen,
                            template,
                        )

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
                template = load_bgr_image(
                    TRACKER_TEMPLATE_FILE
                )

                if template is not None:
                    self.tracker_template = template
                    self.update_tracker_labels()
        except Exception:
            self.tracker_template = None

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
