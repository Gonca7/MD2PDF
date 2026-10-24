# ========================
#   Get Node Type Helper
# ========================
from md2pdf.ast import Inline
from md2pdf.tokens import Tokens,TokenType

def tt2node(token_type: TokenType) -> type[Inline] | None:

    '''
    Converts TokenType onto an actual Node object for the ast
    Returns the node class or None if not found
    '''

    for _, ttype, n in Tokens:
        if token_type == ttype:
            return n

    return None

# ========================


# ========================
# Parse inline crap Helper
# ========================

from md2pdf.ast import Inline
from md2pdf.inline_parser import InlineParser
from md2pdf.scanner import Scanner

def parse_inline(source: str) -> list[Inline]:

    tokens = Scanner(source).scan_tokens()
    parser = InlineParser(tokens)

    return parser.parse()

# ========================