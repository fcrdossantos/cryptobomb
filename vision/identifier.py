import os
from datetime import datetime

from bomb.scenes import Scene
from logger.logs import log

from vision.load_images import get_image
from vision.load_regions import regions
from vision.locator import locate, take_ss

consecutive_errors = 0


def check_presence(*identifiers, region=regions()):
    for identifier in identifiers:
        if locate(get_image(identifier), region):
            return True

    return False


def identify_scene():
    global consecutive_errors
    log("Identificando a cena atual", level="INFO")

    if check_presence("error"):
        return Scene.ERROR
    elif check_presence("new"):
        return Scene.NEW
    elif check_presence("heroes"):
        return Scene.MAIN
    elif check_presence("character"):
        return Scene.HEROES
    elif check_presence("back"):
        return Scene.PLAYING
    elif check_presence("wallet"):
        return Scene.WALLET
    elif check_presence("assinar", region=regions("full")):
        return Scene.METAMASK
    elif check_presence("connect", "logo"):
        return Scene.LOGIN
    elif check_presence("loading", "loading1", "logo"):
        return Scene.LOADING

    global consecutive_errors
    consecutive_errors += 1

    if consecutive_errors >= 3:
        if not os.path.exists("errors") or not os.path.isdir("errors"):
            os.makedirs("errors")

        folder = "errors"
        scene = f"scene_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.png"

        path = os.path.join(folder, scene)
        take_ss(regions("full"), path)
        log(
            f"Impossível de reconhecer a cena atual, verifique em: {path}",
            level="ERROR",
        )

        consecutive_errors = 0

    return Scene.NOT_FOUND
