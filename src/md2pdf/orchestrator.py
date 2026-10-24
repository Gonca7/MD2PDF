# ========================
#    Orchestrator class
# ========================
from collections import deque
from dataclasses import fields, is_dataclass

from md2pdf.parser.ast import *
from md2pdf.parser.block_parser import BlockParser
from md2pdf.parser.inline_parser import InlineParser
from md2pdf.parser.scanner import Scanner


class Orchestrator:
    """
        Coordinates the Markdown parsing pipeline.
    """

    def __init__(self) -> None:
        self.block_parser = BlockParser()

    def parse(self, source: str) -> Document:
        document = self.block_parser.parse(source)

        # Each entry contains the child list and the node to process.
        queue = deque(
            (document.children, node)
            for node in document.children
        )


        while queue:
            siblings, node = queue.popleft()

            # The node may have been replaced by an earlier operation.
            if not any(child is node for child in siblings):
                continue
            
            if isinstance(node, RawBlock):
                parsed_document = self.block_parser.parse(node.content)
                new_blocks = parsed_document.children

                # Prevent the same unfinished content from being
                # returned indefinitely by the block parser.
                if (
                    len(new_blocks) == 1
                    and isinstance(new_blocks[0], RawBlock)
                    and new_blocks[0].content == node.content
                ):
                    raise ValueError(
                        "BlockParser could not resolve RawBlock: "
                        f"{node.content!r}"
                    )

                index = next(
                    i for i, child in enumerate(siblings)
                    if child is node
                )

                # Replace the unfinished block with its parsed blocks.
                siblings[index:index + 1] = new_blocks

                # Process every newly discovered block.
                queue.extend(
                    (siblings, child)
                    for child in new_blocks
                )

            elif isinstance(node, (Paragraph, Heading)):
                self._parse_inline_children(node.children)

            elif isinstance(node, BlockQuote):
                queue.extend(
                    (node.children, child)
                    for child in node.children
                )

            elif isinstance(node, ListBlock):
                for item in node.items:
                    queue.extend(
                        (item.children, child)
                        for child in item.children
                    )


        self._validate(document)
        return document

    @staticmethod
    def _parse_inline_children(children: list[Inline]) -> None:
        index = 0

        while index < len(children):
            node = children[index]

            if isinstance(node, RawText):
                tokens = Scanner(node.content).scan_tokens()
                parsed_nodes = InlineParser(tokens).parse()

                children[index:index + 1] = parsed_nodes
                index += len(parsed_nodes)
            else:
                index += 1

    
    @staticmethod
    def _validate(document: Document) -> None:
        """Raise an error if intermediate nodes remain."""

        queue = deque([document])

        while queue:
            node = queue.popleft()

            if isinstance(node, (RawText, RawBlock)):
                raise ValueError(
                    f"Unprocessed {type(node).__name__}: "
                    f"{node.content!r}"
                )

            if not is_dataclass(node):
                continue

            for field in fields(node):
                value = getattr(node, field.name)

                if isinstance(value, list):
                    queue.extend(value)
                elif is_dataclass(value):
                    queue.append(value)