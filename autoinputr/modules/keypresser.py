"""
Modulo KeyPresser de AutoInputR.

Contiene la interfaz, configuracion y ciclo de ejecucion
del sistema de presion automatica de teclas.

La captura global de teclado y las hotkeys compartidas
permanecen temporalmente fuera de este modulo.
"""

import time
import tkinter as tk

import customtkinter as ctk
import pyautogui


class KeyPresserMixin:
    def create_press_section(self, parent):
        # Intervalo de tecla
        interval_frame = ctk.CTkFrame(parent, corner_radius=14)
        interval_frame.pack(padx=12, pady=(6, 4), fill="x")

        interval_label = ctk.CTkLabel(
            interval_frame,
            text="Intervalo de tecla",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        interval_label.pack(anchor="w", padx=14, pady=(7, 4))

        interval_row = ctk.CTkFrame(interval_frame, fg_color="transparent")
        interval_row.pack(padx=14, pady=(4, 8), fill="x")

        def create_press_time_input(parent_frame, default, label_text):
            group = ctk.CTkFrame(parent_frame, fg_color="transparent")
            group.pack(side="left", padx=(0, 5))

            entry = ctk.CTkEntry(group, width=52, justify="center")
            entry.insert(0, str(default))
            entry.pack(side="left", padx=(0, 4))

            label = ctk.CTkLabel(group, text=label_text)
            label.pack(side="left")

            return entry

        self.press_hours_entry = create_press_time_input(
            interval_row,
            self.press_hours,
            "horas"
        )

        self.press_minutes_entry = create_press_time_input(
            interval_row,
            self.press_minutes,
            "mins"
        )

        self.press_seconds_entry = create_press_time_input(
            interval_row,
            self.press_seconds,
            "segs"
        )

        self.press_milliseconds_entry = create_press_time_input(
            interval_row,
            self.press_milliseconds,
            "ms"
        )

        self.press_turbo_checkbox = ctk.CTkCheckBox(
            interval_frame,
            text="Modo Turbo",
            command=self.toggle_press_turbo
        )
        self.press_turbo_checkbox.pack(anchor="w", padx=14, pady=(8, 16))

        if self.press_turbo_mode:
            self.press_turbo_checkbox.select()

        # Tecla + repetición
        options_row = ctk.CTkFrame(parent, fg_color="transparent")
        options_row.pack(padx=12, pady=4, fill="x")

        key_frame = ctk.CTkFrame(options_row, corner_radius=14)
        key_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        key_title = ctk.CTkLabel(
            key_frame,
            text="Tecla a presionar",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        key_title.pack(anchor="w", padx=14, pady=(7, 6))

        self.press_key_label = ctk.CTkLabel(
            key_frame,
            text=f"Actual: {self.press_key.upper()}",
            text_color="#a6adc8"
        )
        self.press_key_label.pack(anchor="w", padx=14, pady=(0, 8))

        self.press_key_button = ctk.CTkButton(
            key_frame,
            text="Elegir tecla",
            height=36,
            command=self.open_press_key_window
        )
        self.press_key_button.pack(padx=14, pady=(0, 12), fill="x")

        self.press_key_button.bind("<Return>", lambda event: "break")
        self.press_key_button.bind("<space>", lambda event: "break")
        self.press_key_button.bind("<KP_Enter>", lambda event: "break")
        self.press_key_button.bind("<KeyPress>", lambda event: "break")

        repeat_frame = ctk.CTkFrame(options_row, corner_radius=14)
        repeat_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))

        repeat_title = ctk.CTkLabel(
            repeat_frame,
            text="Repetición",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        repeat_title.pack(anchor="w", padx=14, pady=(7, 3))

        self.press_repeat_var = tk.StringVar(value=self.press_repeat_mode)

        repeat_once_row = ctk.CTkFrame(repeat_frame, fg_color="transparent")
        repeat_once_row.pack(padx=14, pady=4, fill="x")

        repeat_radio = ctk.CTkRadioButton(
            repeat_once_row,
            text="Repetir",
            variable=self.press_repeat_var,
            value="repeat",
            command=self.save_config
        )
        repeat_radio.pack(side="left")

        self.press_repeat_entry = ctk.CTkEntry(
            repeat_once_row,
            width=55,
            justify="center"
        )
        self.press_repeat_entry.insert(0, self.press_repeat_times)
        self.press_repeat_entry.pack(side="left", padx=(8, 6))

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
            variable=self.press_repeat_var,
            value="until_stopped",
            command=self.save_config
        )
        until_radio.pack(side="left")

        # Botones
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(padx=12, pady=(8, 2), fill="x")

        self.start_press_button = ctk.CTkButton(
            buttons_frame,
            text=f"Iniciar ({self.press_hotkey.upper()})",
            height=42,
            command=self.start_pressing
        )
        self.start_press_button.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="ew")

        self.stop_press_button = ctk.CTkButton(
            buttons_frame,
            text=f"Detener ({self.press_hotkey.upper()})",
            height=42,
            fg_color="#45475a",
            hover_color="#585b70",
            command=self.stop_pressing
        )
        self.stop_press_button.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="ew")

        self.press_hotkey_button = ctk.CTkButton(
            buttons_frame,
            text="Configuración de hotkey",
            height=42,
            command=self.open_press_hotkey_window
        )
        self.press_hotkey_button.grid(row=1, column=0, columnspan=2, pady=4, sticky="ew")

        self.press_hotkey_button.bind("<Return>", lambda event: "break")
        self.press_hotkey_button.bind("<space>", lambda event: "break")
        self.press_hotkey_button.bind("<KP_Enter>", lambda event: "break")
        self.press_hotkey_button.bind("<KeyPress>", lambda event: "break")

        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        # Estado
        press_status_row = ctk.CTkFrame(parent, fg_color="transparent")
        press_status_row.pack(padx=12, pady=(4, 0), fill="x")

        self.press_speed_label = ctk.CTkLabel(
            press_status_row,
            text="Velocidad: 0 teclas/s",
            text_color="#a6adc8"
        )
        self.press_speed_label.pack(side="right", padx=(12, 0), pady=(42, 0))

        self.press_status_label = ctk.CTkLabel(
            press_status_row,
            text="Estado: AutoPresser detenido",
            text_color="#a6adc8"
        )
        self.press_status_label.pack(side="right", pady=(42, 0))

    def toggle_press_turbo(self):
        self.press_turbo_mode = bool(self.press_turbo_checkbox.get())

        if self.press_turbo_mode:
            self.update_press_status("Estado: Modo Turbo de KeyPresser activado", "#a6e3a1")
        else:
            self.update_press_status("Estado: Modo Turbo de KeyPresser desactivado", "#a6adc8")

        self.save_config()

    def update_press_status(self, text, color="#a6adc8"):
        if hasattr(self, "press_status_label"):
            self.press_status_label.configure(text=text, text_color=color)

    def update_press_speed_label(self, speed):
        self.press_current_speed = speed

        if hasattr(self, "press_speed_label"):
            self.press_speed_label.configure(
                text=f"Velocidad: {speed} teclas/s"
            )

    def update_press_labels(self):
        if hasattr(self, "press_key_label"):
            self.press_key_label.configure(
                text=f"Actual: {self.press_key.upper()}"
            )

        if hasattr(self, "start_press_button"):
            self.start_press_button.configure(
                text=f"Iniciar ({self.press_hotkey.upper()})"
            )

        if hasattr(self, "stop_press_button"):
            self.stop_press_button.configure(
                text=f"Detener ({self.press_hotkey.upper()})"
            )

        if hasattr(self, "press_hotkey_button"):
            self.press_hotkey_button.configure(
                text=f"Configuración de hotkey"
            )

    def validate_press_fields(self):
        fields = [
            self.press_hours_entry,
            self.press_minutes_entry,
            self.press_seconds_entry,
            self.press_milliseconds_entry,
            self.press_repeat_entry
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

        if self.press_repeat_entry.get() == "0":
            self.press_repeat_entry.delete(0, "end")
            self.press_repeat_entry.insert(0, "1")
            corrected = True

        if corrected:
            self.update_press_status("Estado: Campos corregidos", "#f9e2af")

    def get_press_interval(self):
        try:
            hours = int(self.press_hours_entry.get() or 0)
            minutes = int(self.press_minutes_entry.get() or 0)
            seconds = int(self.press_seconds_entry.get() or 0)
            milliseconds = int(self.press_milliseconds_entry.get() or 0)

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

    def start_pressing(self):
        self.validate_press_fields()

        blocked_keys = {
            self.hotkey,
            self.click_hotkey,
            self.press_hotkey,
            self.route_hotkey,
            self.tracker_hotkey
        }

        if self.press_key in blocked_keys:
            self.update_press_status(
                "Estado: La tecla a presionar no puede ser una hotkey",
                "#f38ba8"
            )
            return

        self.save_config()

        self.press_counter = 0
        self.press_repeat_done = 0
        self.press_last_speed_check = time.perf_counter()
        self.update_press_speed_label(0)

        self.press_running = True

        if hasattr(self, "press_key_button"):
            self.press_key_button.configure(state="disabled")

        if hasattr(self, "press_hotkey_button"):
            self.press_hotkey_button.configure(state="disabled")

        self.update_press_status("Estado: Presionando tecla", "#a6e3a1")

        self.start_press_button.configure(
            fg_color="#a6e3a1",
            text_color="black"
        )

        self.stop_press_button.configure(
            fg_color="#45475a",
            text_color="white"
        )

    def stop_pressing(self):
        self.press_running = False
        self.target_window_paused_modules.discard("press")
        self.target_window_stop_scheduled.discard("press")

        if hasattr(self, "press_key_button"):
            self.press_key_button.configure(state="normal")

        if hasattr(self, "press_hotkey_button"):
            self.press_hotkey_button.configure(state="normal")

        self.update_press_status("Estado: AutoPresser detenido", "#a6adc8")
        self.update_press_speed_label(0)

        if hasattr(self, "start_press_button"):
            self.start_press_button.configure(
                fg_color="#1f6aa5",
                text_color="white"
            )

        if hasattr(self, "stop_press_button"):
            self.stop_press_button.configure(
                fg_color="#f38ba8",
                text_color="black"
            )

    def toggle_pressing(self):
        if self.press_running:
            self.stop_pressing()
        else:
            self.start_pressing()

    def press_loop(self):
        while not self.stop_thread:
            if self.press_running:
                if not self.can_execute_for_target_window("press"):
                    time.sleep(0.05)
                    continue

                repeat_mode = self.press_repeat_var.get()
                repeat_limit = int(self.press_repeat_entry.get() or 1)

                try:
                    pyautogui.press(self.press_key)

                except pyautogui.FailSafeException:
                    self.press_running = False
                    self.after(
                        0,
                        lambda: self.update_press_status(
                            "Estado: AutoPresser detenido por failsafe",
                            "#f38ba8"
                        )
                    )
                    continue

                except Exception:
                    self.press_running = False
                    self.after(
                        0,
                        lambda: self.update_press_status(
                            "Estado: Error al presionar tecla",
                            "#f38ba8"
                        )
                    )
                    continue

                self.press_repeat_done += 1
                self.press_counter += 1

                now = time.perf_counter()
                elapsed = now - self.press_last_speed_check

                if elapsed >= 1:
                    speed = int(self.press_counter / elapsed)

                    self.press_counter = 0
                    self.press_last_speed_check = now

                    self.after(
                        0,
                        lambda value=speed: self.update_press_speed_label(value)
                    )

                if repeat_mode == "repeat" and self.press_repeat_done >= repeat_limit:
                    self.after(0, self.stop_pressing)
                    continue

                if self.press_turbo_mode:
                    time.sleep(0)
                else:
                    time.sleep(self.get_press_interval())
            else:
                time.sleep(0.01)

    def open_press_key_window(self):
        if self.press_running:
            self.update_press_status(
                "Estado: Detén AutoPresser antes de cambiar la tecla",
                "#f9e2af"
            )
            return

        if self.capturing_press_key:
            return

        if self.press_key_window is not None:
            try:
                if self.press_key_window.winfo_exists():
                    self.press_key_window.lift()
                    self.press_key_window.focus_force()
                    return
            except Exception:
                pass

            self.press_key_window = None
            self.press_key_status_label = None
            self.capturing_press_key = False

        if (
            self.hotkey_window is not None
            or self.click_hotkey_window is not None
            or self.press_hotkey_window is not None
        ):
            return

        self.capturing_press_key = True

        window_width = 420
        window_height = 190

        window = ctk.CTkToplevel(self)
        self.press_key_window = window
        self.apply_icon_to_window(window)

        window.title("Tecla de AutoPresser")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            window,
            text="Presiona la tecla que AutoPresser repetirá",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        label.pack(pady=(28, 10))

        self.press_key_status_label = ctk.CTkLabel(
            window,
            text=f"Actual: {self.press_key.upper()}",
            text_color="#a6adc8"
        )
        self.press_key_status_label.pack(pady=4)

        hint = ctk.CTkLabel(
            window,
            text="No puede ser igual a una hotkey de inicio/detención.",
            text_color="#6c7086",
            font=ctk.CTkFont(size=12)
        )
        hint.pack(pady=(4, 0))

        close_button = ctk.CTkButton(
            window,
            text="Cancelar",
            command=self.close_current_press_key_window
        )
        close_button.pack(pady=14)

        window.protocol("WM_DELETE_WINDOW", self.close_current_press_key_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(150, window.focus_force)

    def close_current_press_key_window(self):
        window = self.press_key_window

        self.press_key_window = None
        self.press_key_status_label = None
        self.capturing_press_key = False

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

    def open_press_hotkey_window(self):
        if self.press_running:
            self.update_press_status(
                "Estado: Detén AutoPresser antes de cambiar la hotkey",
                "#f9e2af"
            )
            return

        if self.capturing_press_hotkey:
            return

        if self.press_hotkey_window is not None:
            try:
                if self.press_hotkey_window.winfo_exists():
                    self.press_hotkey_window.lift()
                    self.press_hotkey_window.focus_force()
                    return
            except Exception:
                pass

            self.press_hotkey_window = None
            self.press_hotkey_status_label = None
            self.capturing_press_hotkey = False

        if (
            self.hotkey_window is not None
            or self.click_hotkey_window is not None
            or self.press_key_window is not None
        ):
            return

        self.capturing_press_hotkey = True

        window_width = 420
        window_height = 190

        window = ctk.CTkToplevel(self)
        self.press_hotkey_window = window
        self.apply_icon_to_window(window)

        window.title("Hotkey de AutoPresser")
        window.geometry(f"{window_width}x{window_height}")
        window.resizable(False, False)
        window.configure(fg_color="#242424")

        window.transient(self)
        window.grab_set()
        window.attributes("-topmost", True)

        label = ctk.CTkLabel(
            window,
            text="Presiona la nueva tecla para iniciar/detener AutoPresser",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        label.pack(pady=(28, 10))

        self.press_hotkey_status_label = ctk.CTkLabel(
            window,
            text=f"Actual: {self.press_hotkey.upper()}",
            text_color="#a6adc8"
        )
        self.press_hotkey_status_label.pack(pady=4)

        hint = ctk.CTkLabel(
            window,
            text=(
                f"No puede ser movimiento: {self.hotkey.upper()} "
                f"ni clicks: {self.click_hotkey.upper()}"
            ),
            text_color="#6c7086",
            font=ctk.CTkFont(size=12)
        )
        hint.pack(pady=(4, 0))

        close_button = ctk.CTkButton(
            window,
            text="Cancelar",
            command=self.close_current_press_hotkey_window
        )
        close_button.pack(pady=14)

        window.protocol("WM_DELETE_WINDOW", self.close_current_press_hotkey_window)

        self.center_window(
            window,
            window_width,
            window_height,
            self.center_offset_x,
            self.center_offset_y
        )

        window.after(150, window.focus_force)

    def close_current_press_hotkey_window(self):
        window = self.press_hotkey_window

        self.press_hotkey_window = None
        self.press_hotkey_status_label = None
        self.capturing_press_hotkey = False

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

    def set_press_turbo_value(self, value):
        self.press_turbo_mode = bool(value)

        self.set_checkbox_state(
            self.press_turbo_checkbox if hasattr(self, "press_turbo_checkbox") else None,
            self.press_turbo_mode
        )

        if self.press_turbo_mode:
            self.update_press_status("Estado: Modo Turbo de KeyPresser activado", "#a6e3a1")
        else:
            self.update_press_status("Estado: Modo Turbo de KeyPresser desactivado", "#a6adc8")

        self.refresh_general_settings_labels()
        self.save_config()

    def toggle_general_press_turbo(self):
        if self.general_press_turbo_checkbox is None:
            return

        self.set_press_turbo_value(bool(self.general_press_turbo_checkbox.get()))
        self.set_general_status("Modo Turbo de KeyPresser actualizado.", "#a6e3a1")
