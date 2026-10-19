import ctypes
import ctypes.wintypes
import os
import sys
from pathlib import Path


PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def is_windows():
    return sys.platform == "win32"


def configure_dpi_awareness():
    if not is_windows():
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def configure_win32_api():
    if not is_windows():
        return

    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        user32.GetForegroundWindow.restype = (
            ctypes.wintypes.HWND
        )

        user32.IsWindow.argtypes = [
            ctypes.wintypes.HWND
        ]
        user32.IsWindow.restype = (
            ctypes.wintypes.BOOL
        )

        user32.IsWindowVisible.argtypes = [
            ctypes.wintypes.HWND
        ]
        user32.IsWindowVisible.restype = (
            ctypes.wintypes.BOOL
        )

        user32.IsIconic.argtypes = [
            ctypes.wintypes.HWND
        ]
        user32.IsIconic.restype = (
            ctypes.wintypes.BOOL
        )

        user32.GetWindowTextLengthW.argtypes = [
            ctypes.wintypes.HWND
        ]
        user32.GetWindowTextLengthW.restype = (
            ctypes.c_int
        )

        user32.GetWindowTextW.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.wintypes.LPWSTR,
            ctypes.c_int,
        ]
        user32.GetWindowTextW.restype = (
            ctypes.c_int
        )

        user32.GetClassNameW.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.wintypes.LPWSTR,
            ctypes.c_int,
        ]
        user32.GetClassNameW.restype = (
            ctypes.c_int
        )

        user32.GetWindowThreadProcessId.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.POINTER(
                ctypes.wintypes.DWORD
            ),
        ]
        user32.GetWindowThreadProcessId.restype = (
            ctypes.wintypes.DWORD
        )

        kernel32.OpenProcess.argtypes = [
            ctypes.wintypes.DWORD,
            ctypes.wintypes.BOOL,
            ctypes.wintypes.DWORD,
        ]
        kernel32.OpenProcess.restype = (
            ctypes.wintypes.HANDLE
        )

        kernel32.QueryFullProcessImageNameW.argtypes = [
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.LPWSTR,
            ctypes.POINTER(
                ctypes.wintypes.DWORD
            ),
        ]
        kernel32.QueryFullProcessImageNameW.restype = (
            ctypes.wintypes.BOOL
        )

        kernel32.CloseHandle.argtypes = [
            ctypes.wintypes.HANDLE
        ]
        kernel32.CloseHandle.restype = (
            ctypes.wintypes.BOOL
        )

    except Exception:
        pass


def get_foreground_window():
    if not is_windows():
        return 0

    try:
        return int(
            ctypes.windll.user32.GetForegroundWindow()
            or 0
        )
    except Exception:
        return 0


def is_window(hwnd):
    if not is_windows() or not hwnd:
        return False

    try:
        return bool(
            ctypes.windll.user32.IsWindow(
                int(hwnd)
            )
        )
    except Exception:
        return False


def is_window_visible(hwnd):
    if not is_windows() or not hwnd:
        return False

    try:
        return bool(
            ctypes.windll.user32.IsWindowVisible(
                int(hwnd)
            )
        )
    except Exception:
        return False


def is_window_minimized(hwnd):
    if not is_windows() or not hwnd:
        return False

    try:
        return bool(
            ctypes.windll.user32.IsIconic(
                int(hwnd)
            )
        )
    except Exception:
        return False


def get_process_name_from_pid(pid):
    if not is_windows() or not pid:
        return ""

    kernel32 = ctypes.windll.kernel32

    handle = kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        int(pid),
    )

    if not handle:
        return ""

    try:
        buffer = ctypes.create_unicode_buffer(
            1024
        )

        size = ctypes.wintypes.DWORD(
            len(buffer)
        )

        ok = (
            kernel32.QueryFullProcessImageNameW(
                handle,
                0,
                buffer,
                ctypes.byref(size),
            )
        )

        if not ok:
            return ""

        return Path(buffer.value).name

    except Exception:
        return ""

    finally:
        try:
            kernel32.CloseHandle(handle)
        except Exception:
            pass


def get_window_info(hwnd):
    if not is_windows() or not hwnd:
        return None

    try:
        user32 = ctypes.windll.user32

        if not user32.IsWindow(
            int(hwnd)
        ):
            return None

        title_length = (
            user32.GetWindowTextLengthW(
                int(hwnd)
            )
        )

        title_buffer = (
            ctypes.create_unicode_buffer(
                max(
                    1,
                    title_length + 1
                )
            )
        )

        user32.GetWindowTextW(
            int(hwnd),
            title_buffer,
            len(title_buffer),
        )

        title = (
            title_buffer.value.strip()
        )

        class_buffer = (
            ctypes.create_unicode_buffer(
                256
            )
        )

        user32.GetClassNameW(
            int(hwnd),
            class_buffer,
            len(class_buffer),
        )

        class_name = (
            class_buffer.value.strip()
        )

        pid = ctypes.wintypes.DWORD()

        user32.GetWindowThreadProcessId(
            int(hwnd),
            ctypes.byref(pid),
        )

        process_name = (
            get_process_name_from_pid(
                pid.value
            )
        )

        return {
            "hwnd": int(hwnd),
            "title": title,
            "process": process_name,
            "class": class_name,
            "pid": int(pid.value),
        }

    except Exception:
        return None


def enumerate_visible_windows(
    exclude_pid=None
):
    if not is_windows():
        return []

    user32 = ctypes.windll.user32
    windows = []

    if exclude_pid is None:
        exclude_pid = os.getpid()

    WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.wintypes.HWND,
        ctypes.wintypes.LPARAM,
    )

    @WNDENUMPROC
    def enum_callback(
        hwnd,
        _lparam
    ):
        try:
            if not user32.IsWindowVisible(
                hwnd
            ):
                return True

            info = get_window_info(hwnd)

            if not info:
                return True

            if (
                exclude_pid is not None
                and info["pid"] == exclude_pid
            ):
                return True

            title = (
                info["title"].strip()
            )

            if (
                not title
                or title == "Program Manager"
            ):
                return True

            windows.append(info)

        except Exception:
            pass

        return True

    try:
        user32.EnumWindows(
            enum_callback,
            0
        )
    except Exception:
        return []

    windows.sort(
        key=lambda item: (
            item.get(
                "process",
                ""
            ).lower(),
            item.get(
                "title",
                ""
            ).lower(),
        )
    )

    return windows


configure_dpi_awareness()
configure_win32_api()
