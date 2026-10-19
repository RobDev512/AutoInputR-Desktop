"""
Modulo Mover de TaskPilot.

Contiene la interfaz y la logica especifica para el
movimiento automatizado del cursor dentro de una zona.

Las operaciones de entrada compartidas con otros modulos
permanecen temporalmente en la clase principal hasta ser
extraidas a services/input_backend.py.
"""

import random
import time
import tkinter as tk

import customtkinter as ctk
import pyautogui


class MoverMixin:
    def create_interval_section(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=14)
        frame.pack(padx=12, pady=(7, 4), fill="x")

        title = ctk.CTkLabel(
            frame,
            text="Velocidad de movimiento",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        title.pack(anchor="w", padx=16, pady=(10, 4))

        speed_header = ctk.CTkFrame(frame, fg_color="transparent")
        speed_header.pack(padx=16, pady=(4, 4), fill="x")

        speed_name = ctk.CTkLabel(
            speed_header,
            text="Velocidad"
        )
        speed_name.pack(side="left")

        self.movement_speed_label = ctk.CTkLabel(
            speed_header,
            text=f"x{self.movement_speed}",
            text_color="#a6e3a1",
            width=70
        )
        self.movement_speed_label.pack(side="right")

        self.movement_speed_slider = ctk.CTkSlider(
            frame,
            from_=0,
            to=1000,
            number_of_steps=1000,
            command=self.change_movement_speed
        )
        self.movement_speed_slider.pack(padx=16, pady=(2, 6), fill="x")
        self.movement_speed_slider.set(self.movement_speed)

        info = ctk.CTkLabel(
            frame,
            text="0 = muy lento y suave · 1000 = máximo posible.",
            text_color="#a6adc8",
            font=ctk.CTkFont(size=12)
        )
        info.pack(anchor="w", padx=16, pady=(0, 12))

    def create_time_input(self, parent, default, text):
        group = ctk.CTkFrame(parent, fg_color="transparent")
        group.pack(side="left", padx=(0, 8))

        entry = ctk.CTkEntry(group, width=52, justify="center")
        entry.insert(0, default)
        entry.pack(side="left", padx=(0, 4))

        label = ctk.CTkLabel(group, text=text)
        label.pack(side="left")

        return entry

    def create_area_section(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=14)
        frame.pack(padx=12, pady=8, fill="x")

        label = ctk.CTkLabel(
            frame,
            text="Zona del cursor",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        label.pack(anchor="w", padx=16, pady=(10, 8))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(padx=16, pady=(0, 12), fill="x")

        pick_button = ctk.CTkButton(
            row,
            text="Elegir zona",
            width=150,
            command=self.select_area
        )
        pick_button.pack(side="left", padx=(0, 16))

        clear_button = ctk.CTkButton(
            row,
            text="Limpiar zona",
            width=130,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.clear_area
        )
        clear_button.pack(side="left", padx=(0, 16))


        self.area_label = ctk.CTkLabel(
            row,
            text="Zona no seleccionada",
            text_color="#a6adc8"
        )
        self.area_label.pack(side="left")

        mode_row = ctk.CTkFrame(frame, fg_color="transparent")
        mode_row.pack(padx=16, pady=(0, 12), fill="x")

        mode_label = ctk.CTkLabel(
            mode_row,
            text="Modo de movimiento:"
        )
        mode_label.pack(side="left", padx=(0, 12))

        self.mode_option = ctk.CTkOptionMenu(
            mode_row,
            values=["Aleatorio", "Horizontal", "Vertical", "Rebote", "Suave"],
            command=self.change_movement_mode,
            width=180
        )
        self.mode_option.pack(side="left")

        self.mode_option.set(self.movement_mode)

    def create_buttons_section(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(padx=12, pady=(5, 5), fill="x")

        self.start_button = ctk.CTkButton(
            frame,
            text=f"Iniciar ({self.hotkey.upper()})",
            height=46,
            command=self.start_movement
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(
            frame,
            text=f"Detener ({self.hotkey.upper()})",
            height=46,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.stop_movement
        )
        self.stop_button.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

        hotkey_button = ctk.CTkButton(
            frame,
            text="Configuración de hotkey",
            height=46,
            command=self.open_hotkey_window
        )
        hotkey_button.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        bottom_row = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_row.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        self.speed_label = ctk.CTkLabel(
            bottom_row,
            text="Velocidad: 0 mov/s",
            text_color="#a6adc8"
        )
        self.speed_label.pack(side="right", padx=(12, 0))

        self.status_label = ctk.CTkLabel(
            bottom_row,
            text="Estado: Detenido",
            text_color="#a6adc8"
        )
        self.status_label.pack(side="right")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def update_status(self, text, color="#a6adc8"):
        if hasattr(self, "status_label"):
            self.status_label.configure(text=text, text_color=color)

    def update_speed_label(self, speed):
        self.current_speed = speed

        if hasattr(self, "speed_label"):
            self.speed_label.configure(
                text=f"Velocidad: {speed} mov/s"
            )

    def load_saved_area(self):
        saved_area = self.config.get("area")

        if (
            isinstance(saved_area, list)
            and len(saved_area) == 4
            and all(isinstance(value, int) for value in saved_area)
        ):
            self.area = tuple(saved_area)

            x1, y1, x2, y2 = self.area

            self.area_label.configure(
                text=f"X1: {x1}  Y1: {y1}   X2: {x2}  Y2: {y2}",
                text_color="#a6e3a1"
            )

            self.update_status("Estado: Zona cargada", "#a6e3a1")

    def clear_area(self):
        self.stop_movement()
        self.area = None
        self.current_x = None
        self.current_y = None
        self.direction_x = 1
        self.direction_y = 1

        self.area_label.configure(
            text="Zona no seleccionada",
            text_color="#a6adc8"
        )

        self.update_status("Estado: Zona limpia", "#f9e2af")
        self.save_config()

    def change_movement_mode(self, selected_mode):
        self.movement_mode = selected_mode

        self.current_x = None
        self.current_y = None
        self.direction_x = 1
        self.direction_y = 1

        self.update_status(f"Estado: Modo {selected_mode}", "#a6adc8")
        self.refresh_general_settings_labels()
        self.save_config()

    def toggle_turbo(self):
        self.turbo_mode = bool(self.turbo_checkbox.get())

        if self.turbo_mode:
            self.update_status("Estado: Modo Turbo activado", "#a6e3a1")
        else:
            self.update_status("Estado: Modo Turbo desactivado", "#a6adc8")

        self.refresh_general_settings_labels()
        self.save_config()

    def validate_interval_fields(self):
        fields = [
            self.hours_entry,
            self.minutes_entry,
            self.seconds_entry,
            self.milliseconds_entry
        ]

        corrected = False

        for entry in fields:
            value = entry.get().strip()

            try:
                number = int(value)
            except ValueError:
                number = 0
                corrected = True

            if number < 0:
                number = 0
                corrected = True

            if value != str(number):
                entry.delete(0, "end")
                entry.insert(0, str(number))

        if corrected:
            self.update_status("Estado: Intervalo corregido", "#f9e2af")

    def get_interval(self):
        try:
            hours = int(self.hours_entry.get() or 0)
            minutes = int(self.minutes_entry.get() or 0)
            seconds = int(self.seconds_entry.get() or 0)
            milliseconds = int(self.milliseconds_entry.get() or 0)

            total = (
                hours * 3600 +
                minutes * 60 +
                seconds +
                milliseconds / 1000
            )

            if total <= 0:
                return 0.001

            return total

        except ValueError:
            return 0.001

    def select_area(self, after_callback=None):
        self.stop_movement()

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
            text="Arrastra para seleccionar la zona de movimiento | ESC para cancelar",
            fill="white",
            font=("Arial", 20, "bold")
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

            self.lift()
            self.focus_force()

            if after_callback is not None:
                after_callback(False)

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

            canvas.itemconfig(
                instruction,
                text="Arrastra para seleccionar la zona de movimiento | ESC para cancelar",
                fill="white"
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

            if x2 - x1 < 30 or y2 - y1 < 30:
                if data["rectangle"]:
                    canvas.delete(data["rectangle"])
                    data["rectangle"] = None

                canvas.itemconfig(
                    instruction,
                    text="Zona demasiado pequeña. Intenta de nuevo | ESC para cancelar",
                    fill="#f38ba8"
                )
                return

            self.area = (x1, y1, x2, y2)

            self.current_x = None
            self.current_y = None
            self.direction_x = 1
            self.direction_y = 1

            self.area_label.configure(
                text=f"X1: {x1}  Y1: {y1}   X2: {x2}  Y2: {y2}",
                text_color="#a6e3a1"
            )
            self.update_status("Estado: Zona seleccionada", "#a6e3a1")
            self.save_config()

            overlay.destroy()
            self.lift()
            self.focus_force()

            if after_callback is not None:
                after_callback(True)

        overlay.bind("<Escape>", cancel_selection)
        canvas.bind("<Escape>", cancel_selection)

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

        overlay.after(100, lambda: canvas.focus_set())

    def change_movement_speed(self, value):
        self.movement_speed = int(round(float(value)))
        self.movement_speed = max(0, min(1000, self.movement_speed))

        if self.movement_speed_label is not None:
            self.movement_speed_label.configure(
                text=f"x{self.movement_speed}"
            )

        self.refresh_general_settings_labels()
        self.save_config()

    def get_movement_loop_delay(self):
        speed = max(0, min(1000, int(self.movement_speed)))

        if speed >= 1000:
            return 0

        slow_factor = 1 - (speed / 1000)

        return max(
            0.001,
            0.20 * (slow_factor ** 2)
        )

    def start_movement(self):
        if not self.area:
            self.update_status("Estado: Falta elegir zona", "#f38ba8")

            self.show_warning_once(
                "Zona no seleccionada",
                "Primero elige una zona donde mover el cursor."
            )
            return

        self.save_config()

        self.movement_counter = 0
        self.last_speed_check = time.perf_counter()
        self.update_speed_label(0)
        self.schedule_next_movement_random_click()

        self.running = True

        self.update_status("Estado: Moviendo cursor", "#a6e3a1")

        self.start_button.configure(
            fg_color="#a6e3a1",
            text_color="black"
        )

        self.stop_button.configure(
            fg_color="#45475a",
            text_color="white"
        )

    def stop_movement(self):
        self.running = False
        self.target_window_paused_modules.discard("movement")
        self.target_window_stop_scheduled.discard("movement")
        self.update_status("Estado: Detenido", "#a6adc8")
        self.update_speed_label(0)

        self.start_button.configure(
            fg_color="#1f6aa5",
            text_color="white"
        )

        self.stop_button.configure(
            fg_color="#f38ba8",
            text_color="black"
        )

    def toggle_movement(self):
        if self.running:
            self.stop_movement()
        else:
            self.start_movement()

    def get_next_position(self):
        x1, y1, x2, y2 = self.area

        mode = self.movement_mode

        if self.current_x is None or self.current_y is None:
            self.current_x = random.randint(x1, x2)
            self.current_y = random.randint(y1, y2)

        if mode == "Aleatorio":
            return random.randint(x1, x2), random.randint(y1, y2)

        if mode == "Horizontal":
            step = 18

            self.current_x += step * self.direction_x

            if self.current_x >= x2:
                self.current_x = x2
                self.direction_x = -1
            elif self.current_x <= x1:
                self.current_x = x1
                self.direction_x = 1

            return int(self.current_x), int(self.current_y)

        if mode == "Vertical":
            step = 18

            self.current_y += step * self.direction_y

            if self.current_y >= y2:
                self.current_y = y2
                self.direction_y = -1
            elif self.current_y <= y1:
                self.current_y = y1
                self.direction_y = 1

            return int(self.current_x), int(self.current_y)

        if mode == "Rebote":
            step = 16

            self.current_x += step * self.direction_x
            self.current_y += step * self.direction_y

            if self.current_x >= x2:
                self.current_x = x2
                self.direction_x = -1
            elif self.current_x <= x1:
                self.current_x = x1
                self.direction_x = 1

            if self.current_y >= y2:
                self.current_y = y2
                self.direction_y = -1
            elif self.current_y <= y1:
                self.current_y = y1
                self.direction_y = 1

            return int(self.current_x), int(self.current_y)

        if mode == "Suave":
            step = 10

            target_x = random.randint(x1, x2)
            target_y = random.randint(y1, y2)

            if target_x > self.current_x:
                self.current_x += step
            elif target_x < self.current_x:
                self.current_x -= step

            if target_y > self.current_y:
                self.current_y += step
            elif target_y < self.current_y:
                self.current_y -= step

            self.current_x = max(x1, min(x2, self.current_x))
            self.current_y = max(y1, min(y2, self.current_y))

            return int(self.current_x), int(self.current_y)

        return random.randint(x1, x2), random.randint(y1, y2)

    def schedule_next_movement_random_click(self):
        min_seconds = max(5, float(self.movement_random_click_min_seconds))
        max_seconds = max(min_seconds, float(self.movement_random_click_max_seconds))

        self.movement_next_random_click_time = (
            time.perf_counter() + random.uniform(min_seconds, max_seconds)
        )

    def move_cursor_to_smooth_for_movement(self, target_x, target_y):
        target_x = int(target_x)
        target_y = int(target_y)

        try:
            start_x, start_y = pyautogui.position()
        except Exception:
            self.move_cursor_to(target_x, target_y)
            return True

        dx = target_x - start_x
        dy = target_y - start_y

        distance = max(abs(dx), abs(dy))

        if distance <= 2:
            self.move_cursor_to(target_x, target_y)
            return True

        speed = max(0, min(1000, int(self.movement_speed)))
        speed_factor = speed / 1000

        if speed >= 1000:
            steps = 1
            delay = 0
        else:
            step_divisor = 7 + (speed_factor * 70)
            steps = max(2, min(90, int(distance / step_divisor)))
            delay = 0.010 * (1 - speed_factor)

        for step in range(1, steps + 1):
            if not self.running or self.stop_thread:
                return False

            next_x = start_x + (dx * step / steps)
            next_y = start_y + (dy * step / steps)

            self.move_cursor_to(next_x, next_y)

            if delay > 0:
                time.sleep(delay)

        return True

    def maybe_do_movement_random_click(self):
        if not self.movement_random_click_enabled:
            return

        if not self.running or not self.area:
            return

        now = time.perf_counter()

        if now < self.movement_next_random_click_time:
            return

        x1, y1, x2, y2 = self.area

        click_x = random.randint(x1, x2)
        click_y = random.randint(y1, y2)

        moved = self.move_cursor_to_smooth_for_movement(click_x, click_y)

        if not moved:
            return

        self.click_mouse(
            x=click_x,
            y=click_y,
            button="left",
            clicks=1
        )

        self.schedule_next_movement_random_click()

    def movement_loop(self):
        while not self.stop_thread:
            if self.running and self.area:
                if not self.can_execute_for_target_window("movement"):
                    time.sleep(0.05)
                    continue

                x, y = self.get_next_position()

                try:
                    if self.movement_smooth_enabled:
                        moved = self.move_cursor_to_smooth_for_movement(x, y)

                        if not moved:
                            continue
                    else:
                        self.move_cursor_to(x, y)

                    self.maybe_do_movement_random_click()

                except pyautogui.FailSafeException:
                    self.running = False
                    self.after(
                        0,
                        lambda: self.update_status(
                            "Estado: Movimiento detenido por failsafe",
                            "#f38ba8"
                        )
                    )
                    continue

                except Exception:
                    self.running = False
                    self.after(
                        0,
                        lambda: self.update_status(
                            "Estado: Error al mover cursor",
                            "#f38ba8"
                        )
                    )
                    continue

                self.movement_counter += 1

                now = time.perf_counter()
                elapsed = now - self.last_speed_check

                if elapsed >= 1:
                    speed = int(self.movement_counter / elapsed)

                    self.movement_counter = 0
                    self.last_speed_check = now

                    self.after(0, lambda value=speed: self.update_speed_label(value))

                time.sleep(self.get_movement_loop_delay())
            else:
                time.sleep(0.01)

    def get_area_text(self):
        if not self.area:
            return "Zona no seleccionada"

        x1, y1, x2, y2 = self.area
        return f"X1: {x1}  Y1: {y1}   X2: {x2}  Y2: {y2}"

    def set_movement_turbo_value(self, value):
        self.turbo_mode = bool(value)

        self.set_checkbox_state(
            self.turbo_checkbox if hasattr(self, "turbo_checkbox") else None,
            self.turbo_mode
        )

        if self.turbo_mode:
            self.update_status("Estado: Modo Turbo de Mover activado", "#a6e3a1")
        else:
            self.update_status("Estado: Modo Turbo de Mover desactivado", "#a6adc8")

        self.refresh_general_settings_labels()
        self.save_config()

    def toggle_general_movement_turbo(self):
        if self.general_movement_turbo_checkbox is None:
            return

        self.set_movement_turbo_value(bool(self.general_movement_turbo_checkbox.get()))
        self.set_general_status("Modo Turbo de Mover actualizado.", "#a6e3a1")

    def change_general_movement_speed(self, value):
        self.movement_speed = int(round(float(value)))
        self.movement_speed = max(0, min(1000, self.movement_speed))

        if self.movement_speed_slider is not None:
            self.movement_speed_slider.set(self.movement_speed)

        if self.movement_speed_label is not None:
            self.movement_speed_label.configure(
                text=f"x{self.movement_speed}"
            )

        self.refresh_general_settings_labels()
        self.save_config()
        self.set_general_status("Velocidad de Mover actualizada.", "#a6e3a1")

    def change_general_movement_mode(self, selected_mode):
        self.movement_mode = selected_mode

        self.current_x = None
        self.current_y = None
        self.direction_x = 1
        self.direction_y = 1

        try:
            if hasattr(self, "mode_option"):
                self.mode_option.set(selected_mode)
        except Exception:
            pass

        self.update_status(f"Estado: Modo {selected_mode}", "#a6adc8")
        self.refresh_general_settings_labels()
        self.save_config()
        self.set_general_status("Tipo de movimiento actualizado.", "#a6e3a1")

    def choose_area_from_general_settings(self):
        window = self.general_settings_window

        try:
            if window is not None and window.winfo_exists():
                window.grab_release()
                window.withdraw()
        except Exception:
            pass

        def after_select(selected):
            try:
                if window is not None and window.winfo_exists():
                    window.deiconify()
                    window.grab_set()
                    window.lift()
                    window.focus_force()
            except Exception:
                pass

            self.refresh_general_settings_labels()

            if selected:
                self.set_general_status("Zona de Mover actualizada.", "#a6e3a1")
            else:
                self.set_general_status("Selección de zona cancelada.", "#a6adc8")

        self.select_area(after_callback=after_select)

    def clear_area_from_general_settings(self):
        self.clear_area()
        self.refresh_general_settings_labels()
        self.set_general_status("Zona de Mover limpiada.", "#f9e2af")
