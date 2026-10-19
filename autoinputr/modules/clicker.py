"""
Modulo Clicker de AutoInputR.

Contiene la interfaz, configuracion y ciclo de ejecucion
del sistema de clicks automaticos.

Las operaciones de entrada compartidas permanecen
temporalmente en la clase principal hasta ser extraidas
a services/input_backend.py.
"""

import time
import tkinter as tk

import customtkinter as ctk
import pyautogui


class ClickerMixin:
    def create_click_section(self, parent):
        # Intervalo de click
        interval_frame = ctk.CTkFrame(parent, corner_radius=14)
        interval_frame.pack(padx=12, pady=(6, 4), fill="x")

        interval_label = ctk.CTkLabel(
            interval_frame,
            text="Intervalo de click",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        interval_label.pack(anchor="w", padx=14, pady=(7, 4))

        interval_row = ctk.CTkFrame(interval_frame, fg_color="transparent")
        interval_row.pack(padx=14, pady=(4, 5), fill="x")

        def create_click_time_input(parent_frame, default, label_text):
            group = ctk.CTkFrame(parent_frame, fg_color="transparent")
            group.pack(side="left", padx=(0, 5))

            entry = ctk.CTkEntry(group, width=52, justify="center")
            entry.insert(0, str(default))
            entry.pack(side="left", padx=(0, 4))

            label = ctk.CTkLabel(group, text=label_text)
            label.pack(side="left")

            return entry

        self.click_hours_entry = create_click_time_input(
            interval_row,
            self.click_hours,
            "horas"
        )

        self.click_minutes_entry = create_click_time_input(
            interval_row,
            self.click_minutes,
            "mins"
        )

        self.click_seconds_entry = create_click_time_input(
            interval_row,
            self.click_seconds,
            "segs"
        )

        self.click_milliseconds_entry = create_click_time_input(
            interval_row,
            self.click_milliseconds,
            "ms"
        )

        self.click_turbo_checkbox = ctk.CTkCheckBox(
            interval_frame,
            text="Modo Turbo",
            command=self.toggle_click_turbo
        )
        self.click_turbo_checkbox.pack(anchor="w", padx=14, pady=(0, 8))

        if self.click_turbo_mode:
            self.click_turbo_checkbox.select()

        # Opciones + repetición
        options_row = ctk.CTkFrame(parent, fg_color="transparent")
        options_row.pack(padx=12, pady=4, fill="x")

        click_options_frame = ctk.CTkFrame(options_row, corner_radius=14)
        click_options_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        options_title = ctk.CTkLabel(
            click_options_frame,
            text="Opciones de click",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        options_title.pack(anchor="w", padx=14, pady=(5, 3))

        button_row = ctk.CTkFrame(click_options_frame, fg_color="transparent")
        button_row.pack(padx=14, pady=4, fill="x")

        mouse_button_label = ctk.CTkLabel(
            button_row,
            text="Botón:"
        )
        mouse_button_label.pack(side="left", padx=(0, 8))

        self.click_mouse_button_option = ctk.CTkOptionMenu(
            button_row,
            values=["Izquierdo", "Derecho", "Medio"],
            width=110,
            command=self.change_click_mouse_button
        )
        self.click_mouse_button_option.pack(side="right")
        self.click_mouse_button_option.set(self.click_mouse_button)

        type_row = ctk.CTkFrame(click_options_frame, fg_color="transparent")
        type_row.pack(padx=14, pady=(4, 6), fill="x")

        click_type_label = ctk.CTkLabel(
            type_row,
            text="Tipo:"
        )
        click_type_label.pack(side="left", padx=(0, 8))

        self.click_type_option = ctk.CTkOptionMenu(
            type_row,
            values=["Simple", "Doble"],
            width=110,
            command=self.change_click_type
        )
        self.click_type_option.pack(side="right")
        self.click_type_option.set(self.click_type)

        repeat_frame = ctk.CTkFrame(options_row, corner_radius=14)
        repeat_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))

        repeat_title = ctk.CTkLabel(
            repeat_frame,
            text="Repetición",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        repeat_title.pack(anchor="w", padx=14, pady=(7, 3))

        self.click_repeat_var = tk.StringVar(value=self.click_repeat_mode)

        repeat_once_row = ctk.CTkFrame(repeat_frame, fg_color="transparent")
        repeat_once_row.pack(padx=14, pady=4, fill="x")

        repeat_radio = ctk.CTkRadioButton(
            repeat_once_row,
            text="Repetir",
            variable=self.click_repeat_var,
            value="repeat",
            command=self.save_config
        )
        repeat_radio.pack(side="left")

        self.click_repeat_entry = ctk.CTkEntry(
            repeat_once_row,
            width=55,
            justify="center"
        )
        self.click_repeat_entry.insert(0, self.click_repeat_times)
        self.click_repeat_entry.pack(side="left", padx=(8, 6))

        times_label = ctk.CTkLabel(
            repeat_once_row,
            text="veces"
        )
        times_label.pack(side="left")

        until_row = ctk.CTkFrame(repeat_frame, fg_color="transparent")
        until_row.pack(padx=14, pady=(4, 6), fill="x")

        until_radio = ctk.CTkRadioButton(
            until_row,
            text="Repetir hasta detener",
            variable=self.click_repeat_var,
            value="until_stopped",
            command=self.save_config
        )
        until_radio.pack(side="left")

        # Posición del cursor
        position_frame = ctk.CTkFrame(parent, corner_radius=14)
        position_frame.pack(padx=12, pady=4, fill="x")

        position_title = ctk.CTkLabel(
            position_frame,
            text="Posición del cursor",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        position_title.pack(anchor="w", padx=14, pady=(7, 3))

        position_row = ctk.CTkFrame(position_frame, fg_color="transparent")
        position_row.pack(padx=14, pady=(4, 6), fill="x")

        self.click_position_var = tk.StringVar(value=self.click_position_mode)

        current_radio = ctk.CTkRadioButton(
            position_row,
            text="Actual",
            variable=self.click_position_var,
            value="current",
            command=self.save_config
        )
        current_radio.pack(side="left", padx=(0, 10))

        fixed_radio = ctk.CTkRadioButton(
            position_row,
            text="Fija",
            variable=self.click_position_var,
            value="fixed",
            command=self.save_config
        )
        fixed_radio.pack(side="left", padx=(0, 10))

        self.click_pick_button = ctk.CTkButton(
            position_row,
            text="Elegir",
            width=78,
            command=self.select_click_location
        )
        self.click_pick_button.pack(side="left", padx=(0, 10))

        x_label = ctk.CTkLabel(position_row, text="X")
        x_label.pack(side="left", padx=(0, 4))

        self.click_x_entry = ctk.CTkEntry(
            position_row,
            width=48,
            justify="center"
        )
        self.click_x_entry.insert(0, self.click_x)
        self.click_x_entry.pack(side="left", padx=(0, 8))

        y_label = ctk.CTkLabel(position_row, text="Y")
        y_label.pack(side="left", padx=(0, 4))

        self.click_y_entry = ctk.CTkEntry(
            position_row,
            width=48,
            justify="center"
        )
        self.click_y_entry.insert(0, self.click_y)
        self.click_y_entry.pack(side="left")

        # Botones
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(padx=12, pady=(4, 2), fill="x")

        self.start_click_button = ctk.CTkButton(
            buttons_frame,
            text=f"Iniciar ({self.click_hotkey.upper()})",
            height=42,
            command=self.start_clicking
        )
        self.start_click_button.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="ew")

        self.stop_click_button = ctk.CTkButton(
            buttons_frame,
            text=f"Detener ({self.click_hotkey.upper()})",
            height=42,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.stop_clicking
        )
        self.stop_click_button.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="ew")

        self.click_hotkey_button = ctk.CTkButton(
            buttons_frame,
            text=f"Configuración de hotkey",
            height=42,
            command=self.open_click_hotkey_window
        )
        self.click_hotkey_button.grid(row=1, column=0, columnspan=2, pady=4, sticky="ew")

        # Evita que este botón se active con Enter o Espacio si llega a tomar foco.
        self.click_hotkey_button.bind("<Return>", lambda event: "break")
        self.click_hotkey_button.bind("<space>", lambda event: "break")
        self.click_hotkey_button.bind("<KP_Enter>", lambda event: "break")
        self.click_hotkey_button.bind("<KeyPress>", lambda event: "break")

        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        # Estado de clicks
        click_status_row = ctk.CTkFrame(parent, fg_color="transparent")
        click_status_row.pack(padx=12, pady=(0, 0), fill="x")

        self.click_speed_label = ctk.CTkLabel(
            click_status_row,
            text="Velocidad: 0 clics/s",
            text_color="#a6adc8"
        )
        self.click_speed_label.pack(side="right", padx=(12, 0), pady=(0, 0))

        self.click_status_label = ctk.CTkLabel(
            click_status_row,
            text="Estado: Clicks detenidos",
            text_color="#a6adc8"
        )
        self.click_status_label.pack(side="right", pady=(0, 0))

    def change_click_mouse_button(self, selected_button):
        self.click_mouse_button = selected_button
        self.save_config()

    def change_click_type(self, selected_type):
        self.click_type = selected_type
        self.save_config()

    def toggle_click_turbo(self):
        self.click_turbo_mode = bool(self.click_turbo_checkbox.get())

        if self.click_turbo_mode:
            self.update_click_status("Estado: Modo Turbo de clicks activado", "#a6e3a1")
        else:
            self.update_click_status("Estado: Modo Turbo de clicks desactivado", "#a6adc8")

        self.refresh_general_settings_labels()
        self.save_config()

    def update_click_status(self, text, color="#a6adc8"):
        if hasattr(self, "click_status_label"):
            self.click_status_label.configure(text=text, text_color=color)

    def update_click_speed_label(self, speed):
        self.click_current_speed = speed

        if hasattr(self, "click_speed_label"):
            self.click_speed_label.configure(
                text=f"Velocidad: {speed} clics/s"
            )

    def validate_click_fields(self):
        fields = [
            self.click_hours_entry,
            self.click_minutes_entry,
            self.click_seconds_entry,
            self.click_milliseconds_entry,
            self.click_repeat_entry,
            self.click_x_entry,
            self.click_y_entry
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

        if self.click_repeat_entry.get() == "0":
            self.click_repeat_entry.delete(0, "end")
            self.click_repeat_entry.insert(0, "1")
            corrected = True

        if corrected:
            self.update_click_status("Estado: Campos de clicks corregidos", "#f9e2af")

    def get_click_interval(self):
        try:
            hours = int(self.click_hours_entry.get() or 0)
            minutes = int(self.click_minutes_entry.get() or 0)
            seconds = int(self.click_seconds_entry.get() or 0)
            milliseconds = int(self.click_milliseconds_entry.get() or 0)

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

    def select_click_location(self):
        self.stop_clicking()

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

        canvas.create_text(
            screen_width // 2,
            50,
            text="Haz click en la ubicación exacta para los clicks | ESC para cancelar",
            fill="white",
            font=("Arial", 20, "bold")
        )

        def cancel_selection(event=None):
            try:
                overlay.destroy()
            except Exception:
                pass

            self.update_click_status("Estado: Selección cancelada", "#a6adc8")
            self.lift()
            self.focus_force()

        def pick_location(event):
            x = event.x_root
            y = event.y_root

            self.click_position_var.set("fixed")

            self.click_x_entry.delete(0, "end")
            self.click_x_entry.insert(0, str(x))

            self.click_y_entry.delete(0, "end")
            self.click_y_entry.insert(0, str(y))

            self.update_click_status(
                f"Estado: Ubicación fija X:{x} Y:{y}",
                "#a6e3a1"
            )

            self.save_config()

            try:
                overlay.destroy()
            except Exception:
                pass

            self.lift()
            self.focus_force()

        overlay.bind("<Escape>", cancel_selection)
        canvas.bind("<Escape>", cancel_selection)
        canvas.bind("<Button-1>", pick_location)

        overlay.after(100, lambda: canvas.focus_set())

    def start_clicking(self):
        self.validate_click_fields()
        self.save_config()

        self.click_counter = 0
        self.click_repeat_done = 0
        self.click_last_speed_check = time.perf_counter()
        self.update_click_speed_label(0)

        self.click_running = True

        if hasattr(self, "click_hotkey_button"):
            self.click_hotkey_button.configure(state="disabled")

        if hasattr(self, "click_pick_button"):
            self.click_pick_button.configure(state="disabled")

        self.update_click_status("Estado: Ejecutando clicks", "#a6e3a1")

        self.start_click_button.configure(
            fg_color="#a6e3a1",
            text_color="black"
        )

        self.stop_click_button.configure(
            fg_color="#45475a",
            text_color="white"
        )

    def stop_clicking(self):
        self.click_running = False
        self.target_window_paused_modules.discard("click")
        self.target_window_stop_scheduled.discard("click")

        if hasattr(self, "click_hotkey_button"):
            self.click_hotkey_button.configure(state="normal")

        if hasattr(self, "click_pick_button"):
            self.click_pick_button.configure(state="normal")

        self.update_click_status("Estado: Clicks detenidos", "#a6adc8")
        self.update_click_speed_label(0)

        if hasattr(self, "start_click_button"):
            self.start_click_button.configure(
                fg_color="#1f6aa5",
                text_color="white"
            )

        if hasattr(self, "stop_click_button"):
            self.stop_click_button.configure(
                fg_color="#f38ba8",
                text_color="black"
            )

    def toggle_clicking(self):
        if self.click_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def get_click_button_name(self):
        selected_button = self.click_mouse_button_option.get()

        if selected_button == "Derecho":
            return "right"

        if selected_button == "Medio":
            return "middle"

        return "left"

    def get_click_amount(self):
        selected_type = self.click_type_option.get()

        if selected_type == "Doble":
            return 2

        return 1

    def get_click_position(self):
        position_mode = self.click_position_var.get()

        if position_mode == "current":
            return None, None

        try:
            x = int(self.click_x_entry.get())
            y = int(self.click_y_entry.get())
            return x, y
        except ValueError:
            self.after(
                0,
                lambda: self.update_click_status(
                    "Estado: Posición de click inválida",
                    "#f38ba8"
                )
            )
            self.click_running = False
            return None, None

    def click_loop(self):
        while not self.stop_thread:
            if self.click_running:
                if not self.can_execute_for_target_window("click"):
                    time.sleep(0.05)
                    continue

                button = self.get_click_button_name()
                click_amount = self.get_click_amount()
                x, y = self.get_click_position()

                repeat_mode = self.click_repeat_var.get()
                repeat_limit = int(self.click_repeat_entry.get() or 1)

                try:
                    if x is None or y is None:
                        pyautogui.click(
                            button=button,
                            clicks=click_amount,
                            interval=0
                        )
                    else:
                        pyautogui.click(
                            x=x,
                            y=y,
                            button=button,
                            clicks=click_amount,
                            interval=0
                        )

                except pyautogui.FailSafeException:
                    self.click_running = False
                    self.after(
                        0,
                        lambda: self.update_click_status(
                            "Estado: Clicks detenidos por failsafe",
                            "#f38ba8"
                        )
                    )
                    continue

                except Exception:
                    self.click_running = False
                    self.after(
                        0,
                        lambda: self.update_click_status(
                            "Estado: Error al ejecutar clicks",
                            "#f38ba8"
                        )
                    )
                    continue

                self.click_repeat_done += 1
                self.click_counter += click_amount

                now = time.perf_counter()
                elapsed = now - self.click_last_speed_check

                if elapsed >= 1:
                    speed = int(self.click_counter / elapsed)

                    self.click_counter = 0
                    self.click_last_speed_check = now

                    self.after(
                        0,
                        lambda value=speed: self.update_click_speed_label(value)
                    )

                if repeat_mode == "repeat" and self.click_repeat_done >= repeat_limit:
                    self.after(0, self.stop_clicking)
                    continue

                if self.click_turbo_mode:
                    time.sleep(0)
                else:
                    time.sleep(self.get_click_interval())
            else:
                time.sleep(0.01)

    def open_click_hotkey_window(self):
        if self.click_running:
            self.update_click_status(
                "Estado: Detén los clicks antes de cambiar la hotkey",
                "#f9e2af"
            )
            return

        if self.capturing_click_hotkey:
            return

        if self.click_hotkey_window is not None:
            try:
                if self.click_hotkey_window.winfo_exists():
                    self.click_hotkey_window.lift()
                    self.click_hotkey_window.focus_force()
                    return
            except Exception:
                pass

            self.click_hotkey_window = None
            self.click_hotkey_status_label = None
            self.capturing_click_hotkey = False

        if (
            self.hotkey_window is not None
            or self.press_key_window is not None
            or self.press_hotkey_window is not None
        ):
            return

        self.capturing_click_hotkey = True

        window_width = 420
        window_height = 190

        window = ctk.CTkToplevel(self)
        self.click_hotkey_window = window
        self.apply_icon_to_window(window)

        window.title("Hotkey de clicks")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            window,
            text="Presiona la nueva tecla para iniciar/detener clicks",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        label.pack(pady=(28, 10))

        self.click_hotkey_status_label = ctk.CTkLabel(
            window,
            text=f"Actual: {self.click_hotkey.upper()}",
            text_color="#a6adc8"
        )
        self.click_hotkey_status_label.pack(pady=4)

        hint = ctk.CTkLabel(
            window,
            text=f"No puede ser la misma que movimiento: {self.hotkey.upper()}",
            text_color="#6c7086",
            font=ctk.CTkFont(size=12)
        )
        hint.pack(pady=(4, 0))

        close_button = ctk.CTkButton(
            window,
            text="Cancelar",
            command=self.close_current_click_hotkey_window
        )
        close_button.pack(pady=14)

        window.protocol("WM_DELETE_WINDOW", self.close_current_click_hotkey_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        def focus_window():
            try:
                if self.click_hotkey_window is window and window.winfo_exists():
                    window.lift()
                    window.focus_force()
            except Exception:
                pass

        window.after(150, focus_window)

    def close_current_click_hotkey_window(self):
        window = self.click_hotkey_window

        self.click_hotkey_window = None
        self.click_hotkey_status_label = None
        self.capturing_click_hotkey = False

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

    def set_click_turbo_value(self, value):
        self.click_turbo_mode = bool(value)

        self.set_checkbox_state(
            self.click_turbo_checkbox if hasattr(self, "click_turbo_checkbox") else None,
            self.click_turbo_mode
        )

        if self.click_turbo_mode:
            self.update_click_status("Estado: Modo Turbo de Clicker activado", "#a6e3a1")
        else:
            self.update_click_status("Estado: Modo Turbo de Clicker desactivado", "#a6adc8")

        self.refresh_general_settings_labels()
        
        self.save_config()

    def toggle_general_click_turbo(self):
        if self.general_click_turbo_checkbox is None:
            return

        self.set_click_turbo_value(bool(self.general_click_turbo_checkbox.get()))
        self.set_general_status("Modo Turbo de Clicker actualizado.", "#a6e3a1")

    def update_click_hotkey_labels(self):
        if hasattr(self, "start_click_button"):
            self.start_click_button.configure(
                text=f"Iniciar ({self.click_hotkey.upper()})"
            )

        if hasattr(self, "stop_click_button"):
            self.stop_click_button.configure(
                text=f"Detener ({self.click_hotkey.upper()})"
            )

        if hasattr(self, "click_hotkey_button"):
            self.click_hotkey_button.configure(
                text=f"Configuración de hotkey"
            )
