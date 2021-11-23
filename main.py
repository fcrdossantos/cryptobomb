# -*- coding: utf-8 -*-
# print("Wallet:", locate(get_image("wallet")))
# print("Metamask:", locate(get_image("metamask")))
# print("Metamask1:", locate(get_image("metamask1")))
# print("Assinar:", locate(get_image("assinar")))
# print("Assinar1:", locate(get_image("assinar1")))
# -*- coding: utf-8 -*-
import os
import time
from datetime import date, datetime, timedelta

import pyautogui
import pydirectinput
from numpy import logical_not, sign

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

start_play = {
    "chrome": None,
    "edge": None,
    "brave": None,
    "firefox": None,
}

current_browser = "edge"

# Trocar navegador ao estar jogando
# Se todos estiverem jogando, então troca de navegador a cada 15 minutos
# Loading 1 minuto
# Next Mission


def scene_timeout(scene, seconds=10):
    global start
    global old_scene

    if old_scene != scene:
        start = datetime.now()

    now = datetime.now()
    login_time = now - start

    if login_time.total_seconds() > seconds:
        log(f"Processo travou em '{scene.value}'. Vamos recarregar a página")
        refresh()


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
    scene_timeout(Scene.LOGIN)

    clicked = False
    while not clicked:
        clicked = locate_click(get_image("connect"))

    return Scene.WALLET


def on_wallet():
    scene_timeout(Scene.WALLET)

    selected = False
    while not selected:
        if locate_click(get_image("metamask")):
            selected = True
        elif locate_click(get_image("metamask1")):
            selected = True
        else:
            time.sleep(1)

    return Scene.METAMASK


def on_metamask():
    scene_timeout(Scene.METAMASK)

    signed = False
    while not signed:
        if locate_click(get_image("assinar"), region=regions("full")):
            signed = True
        else:
            time.sleep(1)

    return Scene.LOADING


def on_loading():
    scene_timeout(Scene.LOADING, 120)


def on_main_menu(next_scene):
    scene_timeout(Scene.MAIN, 15)
    pressed = False

    if next_scene == None:
        next_scene = Scene.HEROES

    while not pressed:
        if next_scene == Scene.HEROES:
            pressed = locate_click(get_image("heroes"))
        elif next_scene == Scene.PLAYING:
            pressed = locate_click(get_image("play"))

    return next_scene


def on_hero():
    scene_timeout(Scene.HEROES, 60 * 5)

    pydirectinput.moveTo(800, 600)
    pyautogui.scroll(10000)

    while not locate(get_image("rest_inativo")):
        time.sleep(1)

    while locate_click(get_image("work_inativo"), confidence=0.95):
        time.sleep(1)

    closed = False
    while not closed:
        closed = locate_click(get_image("close"))

    return None


def on_play():
    global start_play
    global current_browser
    global next_scene

    if not start_play[current_browser]:
        start_play[current_browser] = datetime.now()

    finish = start_play[current_browser] + timedelta(minutes=2)

    if datetime.now() >= finish:
        log(f"Terminou de jogar no {current_browser}")

        pressed = False
        while not pressed:
            pressed = locate_click(get_image("back"))
            next_scene = Scene.HEROES

    else:
        log(f"Jogando no {current_browser} até:", finish)


def on_new_map():
    pressed = False
    while not pressed:
        pressed = locate_click(get_image("new"))
        return Scene.PLAYING


def on_error():
    log("Mensagem de erro encontrada, recarregando")
    refresh()


def on_wait(wait_scene):
    tries = 0
    scene = identify_scene()
    while scene != wait_scene:
        log("Tela Atual:", scene.value, level=Level.INFO)
        log("Aguardando a Tela:", wait_scene, level=Level.INFO)

        if tries == 5:
            wait_scene = None
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
