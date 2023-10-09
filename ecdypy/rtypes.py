""" Abstract Base Class """
from abc import ABC, abstractmethod

import re


class _PrimitiveType_(ABC):
    def __init__(self, __display_form: str) -> None:
        try:
            self._display_form = __display_form
        except Exception as e:
            print(e)

    @abstractmethod
    def value_from(self, __value):
        pass

    @abstractmethod
    def is_ok(self, __value) -> bool:
        pass

    @abstractmethod
    def __str__(self):
        pass


class _INTEGER_(_PrimitiveType_):
    def value_from(self, __value):
        try:
            if self.is_ok(__value):
                return int(__value)
            elif int(__value) < self.min_value:
                return int(self.min_value)
            elif int(__value) > self.max_value:
                return int(self.max_value)
            else:
                raise
        except Exception:
            print(f"Cannot assign value: {__value} to type u8.")

    def is_ok(self, __value: str | int) -> bool:
        return int(__value) > self.max_value and int(__value) < self.min_value

    def __str__(self) -> str:
        return self._display_form


class _U8_(_INTEGER_):
    min_value = 0
    max_value = 255


class _I8_(_PrimitiveType_):

    min_value = -127
    max_value = 128

# d
class _U16_(_PrimitiveType_):
    min_value = -127
    max_value = 128
#d
class _I16_(_PrimitiveType_):

    min_value = -127
    max_value = 128





u8 = _U8_("u8")
print(u8.value_from(256))
