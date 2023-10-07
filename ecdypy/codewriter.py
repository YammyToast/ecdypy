from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from ._meta import __version__, __source__

@dataclass
class Formatter():
    _indent_spaces: int
    _seperator_function_chains: str 
    _seperator: str

default_formatter = Formatter(
    _indent_spaces = 4,
    _seperator_function_chains = "",
    _seperator = "\n"
)

"""
Priority Bands:
-1 : Always last.
0 : Lowest.
1 : Regular.
2 : Highest.
"""

"""
IDs:
Lower First.
"""

class CodeObject():
    def __init__(
        self,
        __priority: int = -1,
        __id: int = -1
    ):
        self._priority = __priority
        self._id = __id

class CodeText(CodeObject):
    def __init__(
        self,
        __text: str | list[str] = ""
    ):
        self._text = deque()
        self.add_text(__text)
        super().__init__(1)  

    def add_text(
        self,
        __text: str | list[str]
    ) -> None:
        if type(__text) == "str":
            self._text.append(__text)
        elif type(__text) == CodeText:
            self._text.extend(__text)
    
    def __add__(
        self,
        __other: str | list[str]
    ) -> CodeText:
        return(CodeText(self._text + __other))
    
    def __str__(
        self,
        __formatter: Formatter = default_formatter
    ) -> str:
        buf = [str(x) for x in self._text]
        return __formatter._seperator.join(buf)

class CodeWriter():
    def __init__(
        self,
        __formatter: Formatter = default_formatter
    ):
        self._formatter = __formatter

        self._code_obj_tree = deque()
    
    def add(
            self,
            __object: CodeText
    ):
        self._code_obj_tree.append(__object)

    def add_auto_gen_comment(
        self,
        __license: str,
        __author: str | list[str]
    ):
        author = [__author] if type(__author) == "str" else __author

        text = CodeText("/*")
        text.add_text(f"This file was automatically generated using ecdypy {__version__}.")
        text.add_text(f"This implementation is licensed under: {__license}.")
        text.add_text(f"Authors: {','.join(author)}")
        text.add_text(f"ecdypy source code is available at: {__source__}.")
        text.add_text("*\\")
        
    def __str__(
        self
    ):
        buf = [str(x) for x in self._code_obj_tree]
        return self._seperator.join(buf)

    def __add__(
        self,
        __other: CodeWriter | CodeText | str
    ):
        try:
            other = CodeText("")
            if __other is str:
                other = CodeText(__other)
            elif __other is CodeWriter:
                print("test") 
        except Exception as e:
            print(e)
        

if __name__ == "__main__":
    print(__name__)
