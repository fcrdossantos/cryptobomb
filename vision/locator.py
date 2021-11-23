# -*- coding: utf-8 -*-
import os

import cv2
import mss
import numpy as np
import pyautogui
import pydirectinput
from logger.logs import log

from vision.load_regions import regions

pyautogui.PAUSE = 1


# Take Screen Shot on a fast way
def take_ss(region, name=None):
    with mss.mss() as sct:
        sct_img = sct.grab(region)

        # save image if pass a name as parameter
        if name is not None:
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=name)

        return sct_img


#
# Locate the most similar image on screen
def locate(needle, region=regions(), grayscale=False, confidence=0.8):

    with mss.mss() as sct:

        ss = np.array(sct.grab(region))
        ss = ss[:, :, :3]

        if grayscale:
            ss = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)
            needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)

        needle_h, needle_w = needle.shape[:2]
        log(
            f"Dimensões do Needle (imagem a ser buscada): \nAltura - {needle_h}\nLargura - {needle_w}",
            level="DEBUG",
        )

        result = cv2.matchTemplate(ss, needle, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        min_loc = (min_loc[0] + region[0], min_loc[1] + region[1])
        max_loc = (max_loc[0] + region[0], max_loc[1] + region[1])

        log(
            f"Valores de debug:\nValor Mínimo - {min_val}\nValor Máximo - {max_val}\nPior Local - {min_loc}\nMelhor Local - {max_loc}",
            level="DEBUG",
        )

        if max_val > confidence:
            position_x = max_loc[0] + needle_w // 2
            position_y = max_loc[1] + needle_h // 2
            return position_x, position_y

        return False


# Also locate the image but also perform a click
def locate_click(needle, region=regions(), grayscale=False, confidence=0.75):
    pos = locate(needle, region, grayscale, confidence)

    if pos is not None and pos is not False:
        pos_x = pos[0]
        pos_y = pos[1]

        pydirectinput.moveTo(pos_x, pos_y)
        pydirectinput.click(pos_x, pos_y)
        log(f"Clicando na posição: ({pos_x},{pos_y})", level="DEBUG")

        return True

    return False


# DEBUG - Print Screenshots
if os.getenv("DEBUG", "FALSE").lower() in ("true", "1"):
    if not os.path.exists("print") or not os.path.isdir("print"):
        os.makedirs("print")
    pyautogui.screenshot("print/icon.png", region=regions("icon_mask"))
    pyautogui.screenshot("print/mask.png", region=regions("mask_open"))
    pyautogui.screenshot("print/unlock.png", region=regions("button_unlock"))
