from __future__ import annotations

""" Abstract Base Class """
from abc import ABC, abstractmethod


class Macro:
    def __init__(self, __text) -> None:
        self._text = str(__text)

    def get_text(self) -> str:
        return f"#[{self._text}]"

    def __str__(self) -> str:
        return self.get_text()


class Derive:
    def __init__(self, *args) -> None:
        arg_vals = list(args)
        arg_vals = [str(x) for x in arg_vals]
        self._args = arg_vals

    def get_text(self) -> str:
        return f"#[derive({','.join(self._args)})]"

    def __str__(self) -> str:
        return self.get_text()
