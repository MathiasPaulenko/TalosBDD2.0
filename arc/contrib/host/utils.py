import os
from datetime import datetime
from time import sleep

import win32con
import win32gui
import win32ui

from settings import settings


def format_date(date):
    return str(date).replace('-', '').replace(' ', '_').replace(':', '').replace('.', '')


def screenshot(hwnd=None):
    if not hwnd:
        hwnd = win32gui.GetDesktopWindow()
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    h = b - t
    w = r - l
    h_dc = win32gui.GetWindowDC(hwnd)
    my_dc = win32ui.CreateDCFromHandle(h_dc)
    new_dc = my_dc.CreateCompatibleDC()

    my_bitmap = win32ui.CreateBitmap()
    my_bitmap.CreateCompatibleBitmap(my_dc, w, h)

    new_dc.SelectObject(my_bitmap)

    win32gui.SetForegroundWindow(hwnd)
    sleep(.2)
    new_dc.BitBlt((0, 0), (w, h), my_dc, (0, 0), win32con.SRCCOPY)
    my_bitmap.Paint(new_dc)
    screenshot_name = f"{format_date(datetime.now())}.png"
    output_path = os.path.join(settings.BASE_PATH, 'output' + os.sep + 'screenshots')
    screenshot_path = os.path.join(output_path, screenshot_name)
    my_bitmap.SaveBitmapFile(new_dc, screenshot_path)
    return screenshot_path


def get_windows_by_title(windows_title):
    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

    windows = []
    win32gui.EnumWindows(_window_callback, windows)

    aux = [hwnd for hwnd, title in windows if windows_title in title]
    return aux[0]


def get_host_screenshot(windows_title):
    windows = get_windows_by_title(windows_title)
    return screenshot(windows)
