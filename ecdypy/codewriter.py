from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from collections import deque
from dataclasses import dataclass
import traceback

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
    """Base Class Interface for CodeObjects that can be declared separately from their normal representation."""

    def __init__(self):
        pass

    @abstractmethod
    def get_declaration(self, __formatter: Formatter = default_formatter):
        pass


class _DEFINABLE_(ABC):
    """Base Class Interface for CodeObjects that can be declared separately from their normal representation."""

    def __init__(self):
        pass

    @abstractmethod
    def get_definition(self, __formatter: Formatter = default_formatter):
        pass


class _CONTAINER_(object):
    def __init__(self, __init=None):
        init = __init
        if isinstance(init, CodeWriter):
            self._code_obj_tree = init._code_obj_tree
        elif isinstance(init, list):
            self._code_obj_tree = deque(init)
        elif init != None:
            self._code_obj_tree = deque([init])
        else:
            self._code_obj_tree = deque()

    def add(self, __other: str | _CODEOBJECT_ | list[_CODEOBJECT_] | _CONTAINER_):
        """Add a CodeObject to the Container's tree.

        Items must be implementations of CodeObject, or be plain text.

        Examples:
            >>> import ecdypy as ec
            >>> cwr = ec.CodeWriter()
            >>> text = ec.CodeText("Sample Text 1")
            >>> cwr.add([text, "More Text"])
            >>> print(cwr)

        :param __object: Item(s) to add to the CodeWriter tree.
        :type __object: str | Iterable[CodeObject] | CodeText
        :raises TypeError: Type of item(s) cannot be added to the CodeWriter tree.
        """
        try:

            if isinstance(__other, list):
                for item in __other:
                    self.add(item)
                return

            if isinstance(__other, _DECLARABLE_):
                self._code_obj_tree.append(__other.get_declaration())

            if isinstance(__other, _DEFINABLE_):
                self._code_obj_tree.append(__other.get_definition())
            elif isinstance(__other, _CONTAINER_):
                self._code_obj_tree.extend(__other._code_obj_tree)

            if isinstance(__other, str):
                self._code_obj_tree.append(CodeText(__other))
            if (
                isinstance(__other, CodeText)
                or isinstance(__other, _CODEOBJECT_)
                or isinstance(__other, LazyString)
            ):
                self._code_obj_tree.append(__other)

        except TypeError as e:
            print(f"No Implementation for adding type '{type(__other)}' to CodeWriter.")
            raise

    def empty(self: _CONTAINER_):
        """Empty the container's tree.
        :return: True if the function executed successfully.
        :rtype: True
        """
        self._code_obj_tree.clear()
        return True

    def __str__(self):
        """Output the contents of the Container's tree.
        The generated string will be the code representation of all CodeObjects added to the Container.
        :return: String containing lines seperated with the formatting line seperator that is the code representation of all CodeObjects stored in the container.
        :rtype: str
        """
        buf = [str(x) for x in self._code_obj_tree]
        return self._formatter._separator.join(buf)


class _CODEOBJECT_(ABC):
    """Base Class Interface for generated CodeObjects to ensure the CodeWriter can handle them correctly."""

    def __init__(self, __priority: int = -1):
        self._priority = __priority

    @abstractmethod
    def __str__(self, __formatter: Formatter):
        pass


@dataclass
class LazyString(_CODEOBJECT_):
    _obj: _DECLARABLE_ | _DEFINABLE_
    _method: function

    def __str__(self) -> str:
        return self._method()


# ==============================================================================================
# ==============================================================================================


class CodeText(_CODEOBJECT_, _CONTAINER_):
    """CodeObject implementation for assisting with raw-text code constructs.

    Examples:
        >>> import ecdypy as ec
        >>> text = ec.CodeText("Sample Text 1")
        >>> text.add_text()
        >>> text.add_text("Paragraph 1")
        >>> text += "Line 1"
        >>> text = text + "Line 2"
        >>> print(text)
        >>> # Sample Text 1
        >>> #
        >>> # Paragraph 1
        >>> # Line 1
        >>> # Line 2
    """

    def __init__(self, __text: str | list[str] | None = None):
        """CodeText Constructor

        Examples:
            >>> import ecdypy as ec
            >>> cwr = ec.CodeWriter()
            >>> text = ec.CodeText("my_text")
            >>> cwr.add(text)
            >>> print(cwr)
            >>> # my_text

        :param __text: str | list[str]. Text to add to the CodeWriter tree, defaults to None
        """
        self._text = deque()
        if __text != None:
            self.add_text(__text)
        # super(_CODEOBJECT_, self).__init__(1)
        _CODEOBJECT_.__init__(self, 1)
        _CONTAINER_.__init__(self)
        # super(_CONTAINER_, self).__init__()

    def add_text(self, __text: str | list[str] | CodeText | None = None) -> None:
        """Append text to the text buffer.

        Can be used to combine CodeTexts.

        Examples:
            >>> import ecdypy as ec
            >>> text = CodeText("Sample Text 1")
            >>> text.add_text()
            >>> text.add_text("Paragraph 1")
            >>> text += "Line 1"
            >>> text = text + "Line 2"
            >>> print(text)
            >>> # Sample Text 1
            >>> #
            >>> # Paragraph 1
            >>> # Line 1
            >>> # Line 2

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
        """Add text to the CodeText"""
        return CodeText(self._text + __other)

    def __str__(self, __formatter: Formatter = default_formatter) -> str:
        """Read from the CodeText buffer."""
        buf = [str(x) for x in self._text]
        return __formatter._separator.join(buf)

    def __add__(self, __other):
        """Add text to the CodeText"""
        self.add_text(__other)
        return CodeText(self)

    def __iadd__(self, __other):
        """Append text to the CodeText"""
        self.add_text(__other)
        return CodeText(self)

    def __len__(self):
        """Return the number of lines in the buffer."""
        return len(self._text)


# ==============================================================================================
# ==============================================================================================


class CodeWriter(_CONTAINER_):
    """Container class for ecdypy CodeObjects.

    :class:`CodeWriter`

    Examples:
        >>> import ecdypy as ec
        >>> cwr = ec.CodeWriter()
        >>> text = CodeText("Sample Text 1")
        >>> text.add_text()
        >>> text.add_text("Paragraph 1")
        >>> text += "Line 1"
        >>> text = text + "Line 2"
    """

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
            >>> assert str(cwr_two) == str(cwr_three)

        :param __init: _description_, defaults to None
        :type __init: deque | None, optional
        :param __formatter: _description_, defaults to default_formatter
        :type __formatter: Formatter, optional
        """
        self._formatter = __formatter
        _CONTAINER_.__init__(self)

    def add_auto_gen_comment(
        self, __license: str | None = None, __author: str | list[str] | None = None
    ):
        """Add a comment indicating that the code was autogenerated by a script.

        This can include the license that the generated code falls under, as well as the authors
        of the generating script.

        Examples:
            >>> import ecdypy as ec
            >>> cwr = ec.CodeWriter()
            >>> cwr.add_auto_gen_comment(
            >>>     "MIT",
            >>>     [
            >>>         "Author_1 <author@mail.com>",
            >>>         "Author 2 <author2@book.com>",
            >>>     ],
            >>> )
            >>> print(cwr)
            >>> # /*
            >>> # This code was automatically generated using ecdypy 0.1
            >>> # ecdypy source code is available at: https://github.com/YammyToast/ecdypy
            >>> # Author(s): Author_1 <author@mail.com>, Author 2 <author2@book.com>
            >>> # This code is licensed under: MIT
            >>> # */

        :param __license: package license, defaults to None
        :type __license: str | None, optional
        :param __author: author or list of authors (and emails), defaults to None
        :type __author: str | list[str] | None, optional
        """
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

    def __add__(self, __other: str | Iterable[_CODEOBJECT_] | CodeText):
        self.add(__other)
        return self

    def __len__(self):
        return len(self._code_obj_tree)


if __name__ == "__main__":
    print(__name__)
