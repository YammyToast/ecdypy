""" Abstract Base Class """
from abc import ABC, abstractmethod

from re import compile


class __PrimitiveType(ABC):
    def __init__(self, __display_form: str, __value_pattern: str) -> None:
        try:
            self._display_form = __display_form
            self._value_pattern = compile(__value_pattern)
        except Exception as e:
            print(e)

    @abstractmethod
    def check_new(self, __value):
        pass

    @abstractmethod
    def __str__(self):
        pass
