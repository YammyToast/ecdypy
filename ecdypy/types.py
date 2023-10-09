""" Abstract Base Class """
from abc import ABC, abstractmethod

import re


class __PrimitiveType(ABC):
    def __init__(self, __display_form: str) -> None:
        try:
            self._display_form = __display_form
        except Exception as e:
            print(e)

    @abstractmethod
    def sanitize(self, __value):
        pass

    @abstractmethod
    def is_ok(self, __value) -> bool:
        pass

    @abstractmethod
    def __str__(self):
        pass

class __U8(__PrimitiveType):
    _ok_pattern = re.compile(r"^([0-9]|[1-9][0-9]|1[0-9]{2}|(2[0-4][0-9]|25[0-5]))$")
    _lower_pattern = re.compile(r"^(-[0-9]+)$")
    _upper_pattern = re.compile(r"^(25[6-9]|2[6-9][0-9]|[3-9][0-9]{2}|[0-9]{4,})$")
    def sanitize(self, __value):
        try:
            if self.is_ok(__value):
                return __value
            elif re.search(self._lower_pattern):
                return 0
            elif re.search(self._upper_pattern):
                return 255
            else:
                raise
        except Exception:
            print(f"Cannot assign value: {__value} to type u8.")
        

    def is_ok(self, __value: str | int) -> bool:
        return re.search(self._ok_pattern, str(__value))