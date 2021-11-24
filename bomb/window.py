import win32con
import win32gui
from logger.logs import log

found_windows = []


def winEnumHandler(hwnd, name_to_find):
    global found_windows

    if win32gui.IsWindowVisible(hwnd):
        win_name = win32gui.GetWindowText(hwnd)
        # print(hex(hwnd), "=>", win_name)
        if name_to_find in win_name:
            found_windows.append(win_name)


def set_top_most():
    global found_windows

    win32gui.EnumWindows(winEnumHandler, "Bombcrypto")

    for name in found_windows:
        try:
            log(f"Colocando a janela {name} no topo do Windows")
            hwnd = win32gui.FindWindow(None, name)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 1920, 1080, 0)
        except:
            log(f"ERRO: Impossível colocar a janela {name} no topo do Windows")

    found_windows = []


set_top_most()
