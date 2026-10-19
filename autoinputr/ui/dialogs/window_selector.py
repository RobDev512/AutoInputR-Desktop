"""
Interfaz del selector de ventana objetivo de AutoInputR.
"""

import customtkinter as ctk

from autoinputr.core.resources import APP_NAME


class WindowSelectorMixin:
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
