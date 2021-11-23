# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

from logger.log_level import Level

MIN_LEVEL = Level.LOG


def set_level(level):
    global MIN_LEVEL
    MIN_LEVEL = level


def log(*args, level=Level.LOG):
    args_unicode = []

    if not isinstance(level, Level):
        try:
            level = Level[level]
        except:
            print("||Invalid log level!")
            print("|| => Valids: DEBUG, INFO, LOG, IMPORTANT, ERROR")

    if level.value < MIN_LEVEL.value:
        return

    for arg in args:
        if type(arg) == str:
            args_unicode.append(arg.encode().decode("utf-8", "ignore"))
        else:
            args_unicode.append(arg)

    if os.getenv("DEBUG", "FALSE").lower() in ("false", "1"):
        sys.stdout.reconfigure(encoding="utf-8")

    now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    print(f"|| [{now}]", *args_unicode)
