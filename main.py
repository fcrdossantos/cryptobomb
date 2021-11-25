# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta

import pyautogui
import pydirectinput

from bomb.scenes import Scene
from bomb.window import set_metamask_top_most, set_top_most
from logger.log_level import Level
from logger.logs import log, set_level
from vision.identifier import identify_scene
from vision.load_images import get_image
from vision.load_regions import regions
from vision.locator import locate, locate_click

# ----------
multi_browser = False
focus_seconds = 10
refresh_minutes = 5
play_hours = 2
set_level(Level.INFO)
click_sleep = 0.3
# ----------

changed = False

old_scene = Scene.NOT_FOUND
wait_scene = None

start = datetime.now()
focus = None

start_play = {
    "edge": None,
    "brave": None,
    "firefox": None,
    "chrome": None,
}

refresh_game = {
    "edge": None,
    "brave": None,
    "firefox": None,
    "chrome": None,
}

next_scene = {
    "edge": None,
    "brave": None,
    "firefox": None,
    "chrome": None,
}

current_browser = "edge"


def try_click(*images, region=regions()):
    tries = 0
    clicked = False

    while not clicked:
        for image in images:
            log(
                "Tentando clicar na imagem: ",
                image,
                f"| Tentativa {tries}/5",
                level=Level.INFO,
                )

            clicked = locate_click(get_image(image), region)

            if clicked:
                return True

        tries += 1

        if tries >= 5:
            break

        time.sleep(1)

    if not clicked:
        log("Impossível clicar na imagem:", *images, "Recarregando!")
        refresh()
        time.sleep(0.3)

    return clicked


def change_browser():
    global current_browser
    global changed

    log("Mudando navegador", level=Level.INFO)
    log(f"=> Atual: {current_browser}", level=Level.INFO)

    old_broswer = current_browser

    if current_browser == "chrome":
        current_browser = "brave"

    elif current_browser == "brave":
        current_browser = "edge"

    elif current_browser == "edge":
        current_browser = "firefox"

    elif current_browser == "firefox":
        current_browser = "chrome"

    log(f"=> Próximo: {current_browser}", level=Level.INFO)

    changed = True
    if not try_click(current_browser, region=regions("taskbar")):
        log(f"!!! ERRO: Não foi possível mudar para {current_browser}!!!")
        current_browser = old_broswer
        changed = False
        return

    changed = True

    time.sleep(1)



def check_focus():
    global focus
    global current_browser
    global focus_seconds

    now = datetime.now()
    focus_time = now - focus

    log("Verificando se já deu o limite de tempo de foco", level=Level.INFO)

    if focus_time.total_seconds() > focus_seconds:
        focus = None
        log(
            f"Ficamos {focus_seconds} segundos no navegador {current_browser}, alterando..."
        )
        pydirectinput.moveTo(800, 600)
        pyautogui.dragRel(0, -20, duration=1)
        time.sleep(0.3)

        pydirectinput.moveTo(800, 600)
        time.sleep(0.3)
        pyautogui.dragRel(0, -20, duration=1)

        change_browser()
        return True
    else:
        log(
            f"Estamos a {focus_time.total_seconds():.0f} segundos no {current_browser}",
            level=Level.INFO,
        )

        return False


def scene_timeout(scene, seconds=10):
    global start
    global old_scene

    if old_scene != scene:
        start = datetime.now()

    if not start:
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

    time.sleep(1)
    return Scene.WALLET


def on_wallet():
    if scene_timeout(Scene.WALLET):
        return

    if not try_click("metamask", "metamask1"):
        return

    time.sleep(1)
    return Scene.METAMASK


def on_metamask():

    set_metamask_top_most()
    if scene_timeout(Scene.METAMASK, 60):
        return

    if not try_click("assinar", region=regions("full")):
        return

    tries = 0
    while locate_click(get_image("metamask_taskbar"), region=regions("taskbar")):
        set_metamask_top_most()
        tries += 1

        if tries >= 5:
            break

        for _ in range(5):
            locate_click(get_image("assinar"), region=regions("full"))
            time.sleep(1)

        time.sleep(1)

    time.sleep(1)
    return None


def on_loading():
    if scene_timeout(Scene.LOADING, 60):
        return


def on_main_menu():
    global current_browser
    global next_scene

    if scene_timeout(Scene.MAIN, 15):
        return

    time.sleep(1)

    if next_scene[current_browser] == None:
        next_scene[current_browser] = Scene.HEROES

    if next_scene[current_browser] == Scene.HEROES:
        if not try_click("heroes"):
            return
    elif next_scene[current_browser] == Scene.PLAYING:
        if not try_click("play"):
            return

    time.sleep(1)
    return next_scene[current_browser]


def on_hero():
    global start_play
    global current_browser

    if scene_timeout(Scene.HEROES, 60 * 5):
        return

    can_select = True

    if start_play[current_browser] is not None:
        finish = start_play[current_browser] + timedelta(hours=play_hours)
        if datetime.now() < finish:
            log("Ainda não está na hora de reativar os herois")
            log(f"- Navegador atual: {current_browser}")
            log(f"- Poderá reativar em: {finish}")

            can_select = False

    if can_select:
        for _ in range(5):
            pydirectinput.moveTo(800, 600)
            pyautogui.dragRel(0, -400, duration=0.5)

        while not locate(get_image("rest_inativo")):
            log("Aguardando a tela de herois aparecer", level=Level.INFO)
            time.sleep(1)

        while locate_click(get_image("work_inativo"), confidence=0.95):
            log("Ativando heroi", level=Level.INFO)
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
    global refresh_minutes
    global play_hours
    global multi_browser

    if not focus:
        focus = datetime.now()

    if not start_play[current_browser]:
        start_play[current_browser] = datetime.now()

    if not refresh_game[current_browser]:
        refresh_game[current_browser] = datetime.now()

    need_refresh = refresh_game[current_browser] + timedelta(minutes=refresh_minutes)
    finish = start_play[current_browser] + timedelta(hours=play_hours)

    if multi_browser:
        if check_focus():
            return

    # Refresh Heroes
    if datetime.now() >= need_refresh:
        log(f"Hora de recarregar posições no navegador {current_browser}")
        refresh_game[current_browser] = None

        if not try_click("back"):
            return

        next_scene[current_browser] = Scene.PLAYING

    # Finish Game
    if datetime.now() >= finish:
        log(f"Terminou de jogar no {current_browser}")
        start_play[current_browser] = None

        if not try_click("back"):
            return

        next_scene[current_browser] = Scene.HEROES

    else:
        log(f"Jogando no {current_browser} até:", finish)




def on_new_map():
    if not try_click("new"):
        return

    return Scene.PLAYING


def on_error():
    log("Mensagem de erro encontrada, recarregando a página")
    refresh()


def on_wait(wait_scene):
    tries = 1
    scene = identify_scene()

    while scene != wait_scene:
        log("Tela Atual:", scene.value, level=Level.INFO)
        log("Aguardando a Tela:", wait_scene, level=Level.INFO)
        log(f"- Tentativa: {tries}/5", level=Level.INFO)

        if tries >= 5:
            wait_scene = scene
            break

        tries += 1
        time.sleep(1)
        scene = identify_scene()


if __name__ == "__main__":
    wallet_tries = 0
    set_top_most()
    while True:
        # Check current scene
        scene = identify_scene()
        log("Cena Atual:", scene.value, level=Level.INFO)
        set_metamask_top_most()

        if wait_scene:
            on_wait(wait_scene)

        if changed:
            time.sleep(2)
            scene = identify_scene()
            changed = False

        if scene == Scene.WALLET:
            wait_scene = on_wallet()
            time.sleep(click_sleep)

        elif scene == Scene.METAMASK:
            wait_scene = on_metamask()
            time.sleep(click_sleep)

        elif scene == Scene.LOGIN:
            set_metamask_top_most()

            if old_scene == Scene.WALLET:
                wallet_tries += 1
                log("Aguardando aparecer o MetaMask")
                if wallet_tries >= 3:
                    wallet_tries = 0
                else:
                    continue

            wait_scene = on_login()
            time.sleep(click_sleep)

        elif scene == Scene.LOADING:
            wait_scene = on_loading()
            if next_scene[current_browser] is None:
                next_scene[current_browser] = Scene.HEROES
            log("Finalizou rotina da tela do loading")
            time.sleep(click_sleep)

        elif scene == Scene.MAIN:
            wait_scene = on_main_menu()
            log("Finalizou rotina da tela do menu")
            time.sleep(click_sleep)

        elif scene == Scene.HEROES:
            wait_scene = on_hero()
            log("Finalizou rotina da tela de herois")
            next_scene[current_browser] = Scene.PLAYING
            time.sleep(click_sleep)

        elif scene == Scene.PLAYING:
            wait_scene = on_play()
            log("Finalizou rotina da tela do jogo")
            time.sleep(click_sleep)

        elif scene == Scene.NEW:
            wait_scene = on_new_map()
            time.sleep(click_sleep)

        elif scene == Scene.ERROR:
            on_error()
            time.sleep(click_sleep)

        old_scene = scene
        log("Aguardando a próxima cena")
        time.sleep(2)


# Possíveis erros:
#
# - Se não tiver logando:
# --> Verificar o botão do MetaMask (cinza)
# --> Verificar se o MetaMask está lá na taskbar
#
# Se botão for cinza então recarregar a página
# Se existir na taskbar, maximiza, fecha e recarrega apágina
#

# Alterações:
#
# - Não mudar o tempo de jogo caso dê erro
# - O tempo deve continuar até o jogo acabar por completo (2h)
#
