# ========================
#   Get Node Type Helper
# ========================
from md2pdf.parser.ast import Inline
from md2pdf.parser.tokens import Tokens,TokenType

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