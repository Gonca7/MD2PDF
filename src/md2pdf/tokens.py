from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    TEXT = auto()
    STRONG_DELIMITER = auto()
    EMPHASIS_DELIMITER = auto()
    CODE_DELIMITER = auto()
    LINK_TEXT = auto()
    LINK_DESTINATION = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int