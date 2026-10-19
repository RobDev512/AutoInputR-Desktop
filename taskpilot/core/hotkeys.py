"""
Hotkeys globales de TaskPilot.

Centraliza el listener global y la configuracion de la hotkey
principal de movimiento. Las hotkeys propias de cada modulo
permanecen junto a su modulo.
"""

import customtkinter as ctk
from pynput import keyboard


class HotkeysMixin:
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
