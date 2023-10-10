""" Abstract Base Class """
from abc import ABC, abstractmethod
from enum import Enum

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


class _NUMBER_(_PrimitiveType_):
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
            print(f"Cannot assign value: {__value} to type {self._display_form}.")

    def is_ok(self, __value: str | int) -> bool:
        return int(__value) > self.max_value and int(__value) < self.min_value

    def __str__(self) -> str:
        return self._display_form


class _U8_(_NUMBER_):
    min_value = 0
    max_value = 255


class _I8_(_NUMBER_):
    min_value = -127
    max_value = 128


class _U16_(_NUMBER_):
    min_value = 0
    max_value = 65535


class _I16_(_NUMBER_):
    min_value = -32767
    max_value = 32767


class _U32_(_NUMBER_):
    min_value = 0
    max_value = (2**32) - 1


class _I32_(_NUMBER_):
    min_value = -((2**31) - 1)
    max_value = (2**31) - 1


class _U64_(_NUMBER_):
    min_value = 0
    max_value = (2**64) - 1


class _I64_(_NUMBER_):
    min_value = -((2**63) - 1)
    max_value = (2**63) - 1


class _U128_(_NUMBER_):
    min_value = 0
    max_value = (2**128) - 1


class _I128_(_NUMBER_):
    min_value = -((2**127) - 1)
    max_value = (2**127) - 1


class _USIZE_(_NUMBER_):
    min_value = 0
    max_value = (2**64) - 1


class _ISIZE_(_NUMBER_):
    min_value = -((2**63) - 1)
    max_value = (2**63) - 1


class _F32_(_NUMBER_):
    ok_pattern = r"([0-9]*\.[0-9]*_f32)"
    min_value = 0
    max_value = (2**32) - 1

    def is_ok(self, __value: str | int) -> bool:
        return int(__value) > self.max_value and int(__value) < self.min_value and re.search(self.ok_pattern, __value) != None


class _F64_(_NUMBER_):
    ok_pattern = r"([0-9]*\.[0-9]*_f64)"
    min_value = 0
    max_value = (2**64) - 1

    def is_ok(self, __value: str | int) -> bool:
        return int(__value) > self.max_value and int(__value) < self.min_value and re.search(self.ok_pattern, __value) != None

class _BOOLEAN_(_PrimitiveType_):

    def value_from(self, __value: bool | int | str) -> str:
        try:
            if not self.is_ok(__value):
                raise
            if re.search(r"^(1|true|True)$", __value):
                return "true"
            elif re.search(r"^(0|false|False)$", __value):
                return "false"
            else:
                raise
        except Exception as e:
            print(f"Cannot assign value: {__value} to type u8.")

    def is_ok(self, __value) -> bool:
        if type(__value) is bool:
            return True
        elif __value == 0 or __value == 1:
            return True
        elif __value == "true" or __value == "false":
            return True        
        else:
            return False

    def __str__(self):
        return self._display_form


class PTypes(Enum):
    u8 = _U8_("u8")
    i8 = _I8_("i8")
    u16 = _U16_("u16")
    i16 = _I16_("i16")
    u32 = _U32_("u32")
    i32 = _I32_("i32")
    u64 = _U64_("u64")
    i64 = _I64_("i64")
    u128 = _U128_("u128")
    i128 = _I128_("i128")
    usize = _USIZE_("usize")
    isize = _ISIZE_("isize")
    f32 = _F32_("f32")
    f64 = _F64_("f64")
    
