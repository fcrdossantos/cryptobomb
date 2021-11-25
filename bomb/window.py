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

    # Pegar a janela do Python primeiro
    windowList = []
    win32gui.EnumWindows(lambda hwnd, windowList: windowList.append((win32gui.GetWindowText(hwnd),hwnd)), windowList)
    pywin = [i for i in windowList if "powershell" in i[0].lower()]
    if len(pywin) > 0:
        win32gui.SetWindowPos(pywin[0][1],win32con.HWND_TOPMOST,0,0,100,500,0)



    win32gui.EnumWindows(winEnumHandler, "Bombcrypto")

    for name in found_windows:
        try:
            log(f"Colocando a janela {name} no topo do Windows")
            hwnd = win32gui.FindWindow(None, name)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 1920, 1080, 0)
        except:
            log(f"ERRO: Impossível colocar a janela {name} no topo do Windows")

    found_windows = []

    set_metamask_top_most()


def set_metamask_top_most():
    global found_windows

    win32gui.EnumWindows(winEnumHandler, "MetaMask")

    for name in found_windows:
        try:
            log(f"Colocando a janela {name} no topo do Windows")
            hwnd = win32gui.FindWindow(None, name)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 1920, 1080, 0)
        except:
            log(f"ERRO: Impossível colocar a janela {name} no topo do Windows")

    found_windows = []

