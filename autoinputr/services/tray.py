"""
Integracion de AutoInputR con la bandeja del sistema y cierre.
"""

import threading

import customtkinter as ctk
import pystray  # type: ignore
from PIL import Image, ImageDraw

from autoinputr.core.resources import APP_NAME, ICON_PATH


class TrayMixin:
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
