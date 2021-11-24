# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta

import pyautogui
import pydirectinput

from bomb.scenes import Scene
from logger.log_level import Level
from logger.logs import log, set_level
from vision.identifier import identify_scene
from vision.load_images import get_image
from vision.load_regions import regions
from vision.locator import locate, locate_click

set_level(Level.INFO)
click_sleep = 0.3

old_scene = Scene.NOT_FOUND
wait_scene = None
next_scene = None

start = datetime.now()
focus = None

start_play = {
    "chrome": None,
    "edge": None,
    "brave": None,
    "firefox": None,
}

refresh_game = {
    "chrome": None,
    "edge": None,
    "brave": None,
    "firefox": None,
}

current_browser = "edge"


# Falta implementar:
# - Troca de Navegadores

# Trocar navegador:
# - Cada navegador terá seu tempo de jogo
# - Cada nevagador terá seu tempo de foco
# - Dentro da tela "Playing" ficará com foco por X segundos (30)
# - Após isso irá trocar para o próximo navegador


def try_click(*images, region=regions()):
    tries = 0
    clicked = False

    while not clicked:
        for image in images:
            clicked = locate_click(get_image(image), region)

            if clicked:
                return True

        tries += 1

        if tries >= 5:
            break

        time.sleep(1)

    if not clicked:
        refresh()
        time.sleep(0.3)

    return clicked


def change_browser():
    global current_browser
    log("Mudando navegador", level=Level.INFO)
    log(f"=> Atual: {current_browser}", level=Level.INFO)

    old_broswer = current_browser

    if current_browser == "chrome":
        current_browser = "edge"

    elif current_browser == "edge":
        current_browser = "brave"

    elif current_browser == "brave":
        current_browser = "firefox"

    elif current_browser == "firefox":
        current_browser = "chrome"

    log(f"=> Próximo: {current_browser}", level=Level.INFO)

    if not try_click(current_browser, region=regions("taskbar")):
        log(f"!!! ERRO: Não foi possível mudar para {current_browser}!!!")
        current_browser = old_broswer
        return

    time.sleep(2)


def check_focus():
    global focus
    global current_browser

    now = datetime.now()
    focus_time = now - focus

    if focus_time.total_seconds() > 30:
        focus = None
        log(f"Ficamos 30 segundos no navegador {current_browser}")
        change_browser()
    else:
        log(
            f"Estamos a {focus_time.total_seconds():.0f} segundos no {current_browser}",
            level=Level.INFO,
        )


def scene_timeout(scene, seconds=10):
    global start
    global old_scene

    if old_scene != scene:
        start = datetime.now()

    now = datetime.now()
    login_time = now - start

    if login_time.total_seconds() > seconds:
        log(f"Processo travou em '{scene.value}'. Vamos recarregar a página")
        start = None
        old_scene = Scene.NOT_FOUND
        refresh()
        return True

    return False


def refresh():
    global click_sleep

    pydirectinput.click(1920 // 2, 1080 // 2)
    time.sleep(click_sleep)
    pydirectinput.keyDown("ctrl")
    pydirectinput.keyDown("shift")
    pydirectinput.press("r")
    pydirectinput.keyUp("ctrl")
    pydirectinput.keyUp("shift")
    time.sleep(click_sleep)


def on_login():
    if scene_timeout(Scene.LOGIN):
        return

    if not try_click("connect"):
        return

    return Scene.WALLET


def on_wallet():
    if scene_timeout(Scene.WALLET):
        return

    if not try_click("metamask", "metamask1"):
        return

    return Scene.METAMASK


def on_metamask():
    time.sleep(2)

    if scene_timeout(Scene.METAMASK):
        return

    if not try_click("assinar", region=regions("full")):
        return

    return Scene.LOADING


def on_loading():
    if scene_timeout(Scene.LOADING, 60):
        return


def on_main_menu(next_scene):
    if scene_timeout(Scene.MAIN, 15):
        return

    if next_scene == None:
        next_scene = Scene.HEROES

    if next_scene == Scene.HEROES:
        if not try_click("heroes"):
            return
    elif next_scene == Scene.PLAYING:
        if not try_click("play"):
            return

    return next_scene


def on_hero():
    if scene_timeout(Scene.HEROES, 60 * 5):
        return

    for _ in range(5):
        pydirectinput.moveTo(800, 600)
        pyautogui.dragRel(0, -400, duration=0.5)

    while not locate(get_image("rest_inativo")):
        time.sleep(1)

    while locate_click(get_image("work_inativo"), confidence=0.95):
        time.sleep(1)

    if not try_click("close"):
        return

    return


def on_play():
    global start_play
    global refresh_game
    global current_browser
    global next_scene
    global focus

    if not focus:
        focus = datetime.now()

    check_focus()

    if not start_play[current_browser]:
        start_play[current_browser] = datetime.now()

    if not refresh_game[current_browser]:
        refresh_game[current_browser] = datetime.now()

    need_refresh = refresh_game[current_browser] + timedelta(minutes=15)
    finish = start_play[current_browser] + timedelta(hours=2)

    # Refresh Heroes
    if datetime.now() >= need_refresh:
        log(f"Terminou de jogar no {current_browser}")

        if not try_click("back"):
            return

        next_scene = Scene.PLAYING

    # Finish Game
    if datetime.now() >= finish:
        log(f"Terminou de jogar no {current_browser}")

        if not try_click("back"):
            return

        next_scene = Scene.HEROES

    else:
        log(f"Jogando no {current_browser} até:", finish)


def on_new_map():
    if not try_click("new"):
        return

    return Scene.PLAYING


def on_error():
    log("Mensagem de erro encontrada, recarregando")
    refresh()


def on_wait(wait_scene):
    tries = 1
    scene = identify_scene()

    while scene != wait_scene:
        log("Tela Atual:", scene.value, level=Level.INFO)
        log("Aguardando a Tela:", wait_scene, level=Level.INFO)
        log(f"- Tentativa: {tries}/5")

        if tries >= 5:
            wait_scene = scene
            break

        tries += 1
        time.sleep(1)
        scene = identify_scene()


if __name__ == "__main__":
    while True:
        # Check current scene
        scene = identify_scene()
        log("Cena Atual:", scene.value, level=Level.INFO)

        if wait_scene:
            on_wait(wait_scene)

        if scene == Scene.LOGIN:
            wait_scene = on_login()
            time.sleep(click_sleep)

        elif scene == Scene.WALLET:
            wait_scene = on_wallet()
            time.sleep(click_sleep)

        elif scene == Scene.METAMASK:
            wait_scene = on_metamask()
            time.sleep(click_sleep)

        elif scene == Scene.LOADING:
            wait_scene = on_loading()
            next_scene = Scene.HEROES
            time.sleep(click_sleep)

        elif scene == Scene.MAIN:
            wait_scene = on_main_menu(next_scene)
            if not next_scene == Scene.PLAYING:
                start_play[current_browser] = None
            time.sleep(click_sleep)

        elif scene == Scene.HEROES:
            wait_scene = on_hero()
            next_scene = Scene.PLAYING
            time.sleep(click_sleep)

        elif scene == Scene.PLAYING:
            wait_scene = on_play()
            time.sleep(click_sleep)

        elif scene == Scene.NEW:
            wait_scene = on_new_map()
            time.sleep(click_sleep)

        elif scene == Scene.ERROR:
            on_error()
            time.sleep(click_sleep)

        old_scene = scene
        time.sleep(2)
