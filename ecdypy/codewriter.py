from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from collections import deque
from dataclasses import dataclass


from ._meta import __version__, __source__


@dataclass
class Formatter:
    """Formatter Interface Class
    Provides options for determining how a CodeWriter will format its text.
    WIP.
    """

    _indent_spaces: int
    _separator_function_chains: str
    _separator: str


default_formatter = Formatter(
    _indent_spaces=4, _separator_function_chains="", _separator="\n"
)


class _DECLARABLE_(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_declaration(self, __formatter: Formatter = default_formatter):
        pass


class CodeObject(ABC):
    """Base Class for code constructs to ensure the CodeWriter can handle them correctly."""

    def __init__(self, __priority: int = -1):
        self._priority = __priority

    @abstractmethod
    def __str__(self, __formatter: Formatter):
        pass


class CodeText(CodeObject):
    """CodeObject implementation for assisting with raw-text code constructs.

    Examples:
        >>> import ecdypy as ec
        >>> cwr = ec.CodeWriter()
        >>> text = CodeText("Sample Text 1")
        >>> text.add_text()
        >>> text.add_text("Paragraph 1")
        >>> text += "Line 1"
        >>> text = text + "Line 2"
    """

    def __init__(self, __text: str | list[str] | None = None):
        """CodeText Constructor

        Examples:
            >>> import ecdypy as ec
            >>> cwr = ec.CodeWriter()
            >>> text = ec.CodeText("my_text")
            >>> cwr.add(text)
            >>> print(cwr)



        :param __text: str | list[str]. Text to add to the CodeWriter tree, defaults to None
        """
        self._text = deque()
        if __text != None:
            self.add_text(__text)
        super().__init__(1)

    def add_text(self, __text: str | list[str] | CodeText | None = None) -> None:
        """Append text to the text buffer.

        Can be used to combine CodeTexts.

        Examples:
            >>>

        :param __text: str | list[str] | CodeText. Text to be appended, defaults to None
        :type __text: str | list[str] | CodeText | None, optional
        """
        try:
            if type(__text) is str:
                self._text.append(__text)
            elif type(__text) is CodeText:
                self._text.extend(__text._text)
            elif type(__text) is deque:
                self._text += __text
            elif __text is None:
                self._text.append("")
            else:
                raise
        except Exception as e:
            print(e)
            print(f"Cannot add type '{type(__text)}' to a CodeText object.")
            print(f"Type: '{type(__text)}' not defined for CodeText.")

    def __add__(self, __other: str | list[str]) -> CodeText:
        return CodeText(self._text + __other)

    def __str__(self, __formatter: Formatter = default_formatter) -> str:
        buf = [str(x) for x in self._text]
        return __formatter._separator.join(buf)

    def __add__(self, __other):
        self.add_text(__other)
        return CodeText(self)

    def __iadd__(self, __other):
        self.add_text(__other)
        return CodeText(self)

    def __len__(self):
        return len(self._text)


class CodeWriter:
    def __init__(
        self, __init: deque | None = None, __formatter: Formatter = default_formatter
    ):
        """_summary_

        Examples:
            >>> cwr_one = ec.CodeWriter("my_text")
            >>> cwr_two = ec.CodeWriter(["my", "text"])
            >>> cwr_three = ec.CodeWriter(cwr_two)
            >>> print(cwr_one) # my_text
            >>> print(cwr_two) # my
            >>>                # text
            >>> print(cwr_three) # my
            >>>                  # text


        :param __init: _description_, defaults to None
        :type __init: deque | None, optional
        :param __formatter: _description_, defaults to default_formatter
        :type __formatter: Formatter, optional
        """
        self._formatter = __formatter
        init = __init
        if isinstance(init, CodeWriter):
            self._code_obj_tree = init._code_obj_tree
        elif isinstance(init, list):
            self._code_obj_tree = deque(init)
        elif init != None:
            self._code_obj_tree = deque([init])
        else:
            self._code_obj_tree = deque()

    def add(self, __object: str | Iterable[CodeObject] | CodeText):
        try:
            object = CodeText("")
            if type(__object) is str:
                object = CodeText(__object)
            elif type(__object) is CodeWriter:
                self._code_obj_tree.extend(__object._code_obj_tree)
                return
            elif type(__object) is CodeText:
                object = __object
            else:
                raise TypeError
            self._code_obj_tree.append(object)

        except TypeError as e:
            print(
                f"No Implementation for adding type '{type(__object)}' to CodeWriter."
            )
            raise

    def add_auto_gen_comment(
        self, __license: str | None = None, __author: str | list[str] | None = None
    ):
        text = CodeText("/*")
        text.add_text(
            f"This code was automatically generated using ecdypy {__version__}"
        )
        text.add_text(f"ecdypy source code is available at: {__source__}")
        if __author is not None:
            author = [__author] if type(__author) is str else __author
            text.add_text(f"Author(s): {', '.join(author)}")
        if __license is not None:
            text.add_text(f"This code is licensed under: {__license}")
        text.add_text("*/")

        self.add(text)

    def __str__(self):
        buf = [str(x) for x in self._code_obj_tree]
        return self._formatter._separator.join(buf)

    def __add__(self, __other: str | Iterable[CodeObject] | CodeText):
        self.add(__other)
        return self

    def __len__(self):
        return len(self._code_obj_tree)


if __name__ == "__main__":
    print(__name__)
