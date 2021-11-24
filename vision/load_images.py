import cv2

IMAGES = {}


def load_images():
    images = {
        # Assinar Metamask
        "wallet": cv2.imread("images/wallet.png"),
        "metamask": cv2.imread("images/metamask.png"),
        "metamask1": cv2.imread("images/metamask1.png"),
        "assinar": cv2.imread("images/assinar.png"),
        "assinar1": cv2.imread("images/assinar1.png"),
        "metamask_taskbar": cv2.imread("images/metamask_taskbar.png"),
        # Navegadores
        "brave": cv2.imread("images/brave.png"),
        "chrome": cv2.imread("images/chrome.png"),
        "edge": cv2.imread("images/edge.png"),
        "firefox": cv2.imread("images/firefox.png"),
        # Menu de Login
        "connect": cv2.imread("images/connect.png"),
        "logo": cv2.imread("images/logo.png"),
        # Novo mapa
        "new": cv2.imread("images/new.png"),
        # Jogando
        "engine": cv2.imread("images/engrenagem.png"),
        "back": cv2.imread("images/voltar.png"),
        # Menu Principal
        "heroes": cv2.imread("images/heroes.png"),
        "play": cv2.imread("images/play.png"),
        # Erros
        "error": cv2.imread("images/error.png"),
        "ok": cv2.imread("images/ok.png"),
        "overload": cv2.imread("images/overload.png"),
        # Heróis
        "character": cv2.imread("images/character.png"),
        "work_inativo": cv2.imread("images/work_inativo.png"),
        "rest_inativo": cv2.imread("images/rest_inativo.png"),
        "close": cv2.imread("images/close.png"),
        # Loading:
        "loading": cv2.imread("images/loading.png"),
        "loading1": cv2.imread("images/loading1.png"),
        "loading2": cv2.imread("images/loading2.png"),
    }

    return images


def get_image(image_name):
    global IMAGES

    if not IMAGES:
        IMAGES = load_images()

    return IMAGES[image_name]
