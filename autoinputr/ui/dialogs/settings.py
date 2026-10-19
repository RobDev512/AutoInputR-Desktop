"""
Dialogos de configuracion y acerca de AutoInputR.
"""

import os
from tkinter import messagebox

import customtkinter as ctk

from autoinputr.core.resources import (
    APP_NAME,
    APP_VERSION,
    CONFIG_DIR,
    CONFIG_FILE,
)


class SettingsMixin:
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
