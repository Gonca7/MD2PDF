from dataclasses import dataclass
from enum import Enum, auto
from typing import Final

from md2pdf.parser.ast import Inline, Strong, Emphasis

class TokenType(Enum):
    TEXT = auto()
    STRONG_DELIMITER = auto()
    EMPHASIS_DELIMITER = auto()
    CODE_DELIMITER = auto()

    BOLD_ITALIC_DELIMITER = auto()
    STRIKETHROUGH_DELIMITER = auto()
    INLINE_CODE = auto()

    INLINE_HTML = auto()

    # Complete inline constructs
    INLINE_LINK = auto()
    IMAGE = auto()
    AUTOLINK = auto()

    LINK_TEXT = auto()
    LINK_DESTINATION = auto()
    
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int


Tokens: Final[tuple[tuple[str, TokenType, type[Inline]], ...]] = (
    ("***", TokenType.BOLD_ITALIC_DELIMITER, Strong),
    ("___", TokenType.BOLD_ITALIC_DELIMITER, Strong),
    ("**", TokenType.STRONG_DELIMITER, Strong),
    ("__", TokenType.STRONG_DELIMITER, Strong),
    ("~~", TokenType.STRIKETHROUGH_DELIMITER, Emphasis),
    ("*", TokenType.EMPHASIS_DELIMITER, Emphasis),
    ("_", TokenType.EMPHASIS_DELIMITER, Emphasis),
)