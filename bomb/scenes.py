from enum import Enum


class Scene(Enum):
    LOGIN = "Login"
    MAIN = "Menu Principal"
    PLAYING = "Jogo"
    HEROES = "Heróis"
    ERROR = "Mensagem de Erro"  # Error Screen
    NEW = "Novo Mapa"  # New Map
    LOADING = "Tela de Carregamento"
    WALLET = "Escolha da Carteira"
    METAMASK = "Assinatura da Metamask"
    NOT_FOUND = "Cena Não Identificada"
