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
                return __value
            elif re.search(self._lower_pattern, str(__value)):
                return self.min_value
            elif re.search(self._upper_pattern, str(__value)):
                return self.max_value
            else:
                raise
        except Exception:
            print(f"Cannot assign value: {__value} to type u8.")

    def is_ok(self, __value: str | int) -> bool:
        return re.search(self._ok_pattern, str(__value))

    def __str__(self) -> str:
        return self._display_form


class _U8_(_INTEGER_):
    _ok_pattern = re.compile(r"^([0-9]|[1-9][0-9]|1[0-9]{2}|(2[0-4][0-9]|25[0-5]))$")
    _lower_pattern = re.compile(r"^(-[0-9]+)$")
    _upper_pattern = re.compile(r"^(25[6-9]|2[6-9][0-9]|[3-9][0-9]{2}|[0-9]{4,})$")
    min_value = 0
    max_value = 255


class _I8_(_PrimitiveType_):
    _ok_pattern = re.compile(r"^-?(1[0-1][0-9]|12[0-7]|[0-9]{0,2})$")
    _lower_pattern = re.compile(r"^-([0-9]{4,}|12[8-9]|1[3-9][0-9])$")
    _upper_pattern = re.compile(r"^([0-9]{4,}|12[8-9]|1[3-9][0-9])$")
    min_value = -127
    max_value = 128

u8 = _U8_("u8")
print(u8.value_from(-100000))