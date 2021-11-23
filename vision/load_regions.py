# Regions that will be used to analyse the screen
def regions(region="game"):
    if region == "icon_mask":
        return (0, 0, 1920, 100)

    if region == "mask_open":
        return (1000, 0, 920, 900)

    if region == "button_unlock":
        return (1000, 150, 920, 750)

    if region == "full":
        return (0, 0, 1920, 1080)

    if region == "game":
        return (450, 200, 1550, 950)

    return False
