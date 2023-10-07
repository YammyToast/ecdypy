from __future__ import annotations

from typing import Iterable

from collections import deque
from dataclasses import dataclass


from ._meta import __version__, __source__


@dataclass
class Formatter():
    _indent_spaces: int
    _seperator_function_chains: str 
    _seperator: str


default_formatter = Formatter(
    _indent_spaces=4,
    _seperator_function_chains="",
    _seperator="\n"
)

"""
Priority Bands:
-1 : Always last.
0 : Lowest.
1 : Regular.
2 : Highest.
"""


class CodeObject():
    def __init__(self, __priority: int = -1):
        self._priority = __priority


class CodeText(CodeObject):
    def __init__(self, __text: str | list[str] = ""):
        self._text = deque()
        self.add_text(__text)
        super().__init__(1)  

    def add_text(self, __text: str | list[str] | CodeText) -> None:
        try:
            if type(__text) == "str":
                self._text.append(__text)
            elif type(__text) == CodeText:
                self._text.extend(__text)
        except Exception as e:
            e.add_note(
                f"Cannot add type \'{type(__text)}\' to a CodeText object."
            )
            e.add_note(
                f"Type: \'{type(__text)}\' not defined for CodeText."
            )

    def __add__(self, other: str | list[str]) -> CodeText:
        return (CodeText(self._text + other))
    
    def __str__(self, __formatter: Formatter = default_formatter) -> str:
        buf = [str(x) for x in self._text]
        return __formatter._seperator.join(buf)


class CodeWriter():
    def __init__(self, __formatter: Formatter = default_formatter):
        self._indent_spaces = __formatter._indent_spaces
        self._seperate_function_chains = __formatter._seperate_function_chains
        self._seperator = __formatter._seperator

        self._code_obj_tree = deque()
    
    def add(
        self,
        __object: str | Iterable[CodeObject] | CodeText
    ):
        try:
            object = CodeText(__object)
            if __object is str:
                object = CodeText(str)
            
            self._code_obj_tree.append(object)

        except Exception as e:
            raise e

    def add_auto_gen_comment(
            self,
            __license: str,
            __author: str | list[str]
    ):
        text = CodeText("/*")
        text.add_text(
            f"This file was automatically generated using ecdypy {__version__}"
        )
        text.add_text(f"ecdypy source code is available at: {__source__}")
        text.add_text("*\\")
        
    def __str__(self):
        buf = [str(x) for x in self._code_obj_tree]
        return self._seperator.join(buf)


if __name__ == "__main__":
    print(__name__)