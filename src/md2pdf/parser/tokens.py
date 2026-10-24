from dataclasses import dataclass
from enum import Enum, auto
from typing import Final

from md2pdf.parser.ast import Inline, Strong, Emphasis

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


Tokens: Final[tuple[tuple[str, TokenType, type[Inline]], ...]] = (
    ("**", TokenType.STRONG_DELIMITER, Strong),
    ("*", TokenType.EMPHASIS_DELIMITER, Emphasis),
)