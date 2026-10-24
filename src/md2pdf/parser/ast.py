from dataclasses import dataclass, field
from typing import TypeAlias


# ---------- Inline nodes ----------

@dataclass
class RawText:
    content: str

@dataclass
class Text:
    content: str


@dataclass
class Emphasis:
    children: list["Inline"]


@dataclass
class Strong:
    children: list["Inline"]


@dataclass
class InlineCode:
    content: str


@dataclass
class Link:
    children: list["Inline"]
    url: str
    title: str | None = None


@dataclass
class Image:
    alt: str
    src: str
    title: str | None = None


Inline: TypeAlias = (
    RawText
    | Text
    | Emphasis
    | Strong
    | InlineCode
    | Link
    | Image
)


# ---------- Block nodes ----------

@dataclass
class RawBlock:
    content: str

@dataclass
class Paragraph:
    children: list[Inline]


@dataclass
class Heading:
    level: int
    children: list[Inline]
    id: str | None = None


@dataclass
class CodeBlock:
    content: str
    language: str | None = None


@dataclass
class ListItem:
    children: list["Block"] = field(default_factory=list)
    checked: bool | None = None


@dataclass
class ListBlock:
    ordered: bool
    items: list[ListItem]
    start: int = 1


@dataclass
class BlockQuote:
    children: list["Block"]


@dataclass
class ThematicBreak:
    pass


@dataclass
class Document:
    children: list["Block"] = field(default_factory=list)


Block: TypeAlias = (
    RawBlock
    | Paragraph
    | Heading
    | CodeBlock
    | ListBlock
    | BlockQuote
    | ThematicBreak
)