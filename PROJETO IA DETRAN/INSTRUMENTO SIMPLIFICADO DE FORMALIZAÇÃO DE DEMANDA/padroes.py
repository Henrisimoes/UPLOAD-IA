import json
import locale as lc
from enum import IntEnum, auto
from dataclasses import dataclass, asdict

from num2words import num2words

from utils import LogLevel, log

USAR_IA = "GERAR ESTE TEXTO POR IA"


class TD(IntEnum):  # TipoDespesa
    # fmt: off
    CAP         = auto(0)
    EQUIP_APOIO = auto()
    EQUIP_TI    = auto()
    CAA         = auto()
    CUSTEIO     = auto()
    CONSUMO     = auto()
    OBRAS       = auto()
    # fmt: on


@dataclass
class Itens:
    # fmt: off
    item     : int
    cod_siag : int
    unidade  : str
    qtd      : int
    descricao: str
    valor_un : float
    # fmt: on

    def to_dict(self):
        return asdict(self)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)


def int_para_string(num: int | float) -> str:
    return num2words(num, lang="pt_BR")


def dinheiro_para_string(num: int | float) -> str:
    return num2words(num, lang="pt_BR", to="currency")


def format_by(value: int | float, by: str):
    return format(value, by)


def fmt_real(real):
    return lc.currency(real, grouping=True)


def readIntInput(msg: str) -> int:
    while True:
        try:
            user_input = input(msg).strip()
            if user_input == "":
                return 0
            result = int(user_input)
        except Exception as e:
            log(LogLevel.ERROR, f"Valor Invalido: {e}")
            continue
        return result
