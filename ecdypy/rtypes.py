from __future__ import annotations

""" Abstract Base Class """
from abc import ABC, abstractmethod
from enum import Enum
import traceback

import re


class UnknownTypeArgument(Exception):
    pass


class IncorrectArgCount(Exception):
    pass


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
        return int(__value) < self.max_value and int(__value) > self.min_value

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
        return (
            int(__value) > self.max_value
            and int(__value) < self.min_value
            and re.search(self.ok_pattern, __value) != None
        )


class _F64_(_NUMBER_):
    ok_pattern = r"([0-9]*\.[0-9]*_f64)"
    min_value = 0
    max_value = (2**64) - 1

    def is_ok(self, __value: str | int) -> bool:
        return (
            int(__value) > self.max_value
            and int(__value) < self.min_value
            and re.search(self.ok_pattern, __value) != None
        )


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


class _STR_(_PrimitiveType_):
    def value_from(self, __value: str | int | bool) -> str:
        return str(__value)

    def is_ok(self, __value: str):
        # the code of doom
        return True

    def __str__(self):
        return self._display_form


class _CHAR_(_PrimitiveType_):
    """
    Valid Integer Values under: https://www.unicode.org/glossary/#unicode_scalar_value
    """

    unicode_scalar_value_pattern = r"^(0x([0-9A-Fa-f]{0,3}|[0-9A-Fa-f]{5}|[0-9A-Da-d][0-7][0-9A-Fa-f]{2}|[E-Fe-f][0-9]{3}|10[0-9A-Fa-f]{4}))$"

    def value_from(self, __value: str | int) -> str:
        try:
            if not self.is_ok(__value):
                raise e
            if (
                re.search(self.unicode_scalar_value_pattern, __value)
                or type(__value) is int
            ):
                return chr(__value)
            else:
                return __value
        except Exception as e:
            traceback.print_stack()
            print(e)

    def is_ok(self, __value: str | int):
        if type(__value) is int and chr(__value):
            if __value > 0 and __value < 55295:
                return True
            elif __value > 57344 and __value < 1114111:
                return True
        elif type(__value) is str:
            if len(__value) == 1:
                return True
            elif re.search(self.unicode_scalar_value_pattern, __value) != None:
                return True
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
    bool = _BOOLEAN_("bool")
    str = _STR_("str")
    char = _CHAR_("")


# ==============================================================================================
# ==============================================================================================


class Tuple:
    def __init__(
        self, *args: _PrimitiveType_ | list[_PrimitiveType_], **kwargs
    ) -> self:
        try:
            check = kwargs.get("check") if type(kwargs.get("check")) is bool else True
            arg_list = Tuple._flatten_args(list(args))
            if check == True:
                Tuple._check_arg_list(arg_list)
            types = Tuple._convert_recursive_objects(list(args))

            self._type_tree = types
            self._type_list = arg_list
            self._check = check

        except UnknownTypeArgument as e:
            traceback.print_stack()
            print(f"\nUnknown type: '{e.args[0]}' provided in tuple assignment.\n")

    @staticmethod
    def _check_arg_list(__list):
        for arg in __list:
            # why is contains dunder???????
            if not (PTypes._member_names_.__contains__(arg) or arg in PTypes) and type(arg) is not Tuple:
                raise UnknownTypeArgument(arg)
            if type(arg) is Tuple:
                Tuple._check_arg_list(arg._type_tree)

    @staticmethod
    def _convert_recursive_objects(__list):
        if len(__list) == 0:
            return __list
        if isinstance(__list[0], tuple):
            return [Tuple(list(__list[0]))] + Tuple._convert_recursive_objects(
                __list[1:]
            )
        elif isinstance(__list[0], list):
            return Tuple._convert_recursive_objects(
                __list[0]
            ) + Tuple._convert_recursive_objects(__list[1:])
        return __list[:1] + Tuple._convert_recursive_objects(__list[1:])

    @staticmethod
    def _flatten_args(__list):
        """
        Recursive Method Derived from:
        https://stackabuse.com/python-how-to-flatten-list-of-lists/
        """
        if len(__list) == 0:
            return __list
        if isinstance(__list[0], list):
            return Tuple._flatten_args(__list[0]) + Tuple._flatten_args(__list[1:])
        if isinstance(__list[0], Tuple):
            return __list[0].get_types() + Tuple._flatten_args(__list[1:])
        if isinstance(__list[0], tuple):
            return Tuple._flatten_args(list(__list[0])) + Tuple._flatten_args(
                __list[1:]
            )
        return __list[:1] + Tuple._flatten_args(__list[1:])

    def value_from(self, *args: _PrimitiveType_, **kwargs):
        try:
            arg_vals = list(args) if kwargs.get("l") == None else list(kwargs.get("l"))

            out_vals = []
            if (x := self.get_types_count()) != (
                y := len(Tuple._flatten_args(list(arg_vals)))
            ):
                raise IncorrectArgCount

            for i, type_item in enumerate(self._type_tree):
                if type(type_item) is Tuple:
                    out_vals.append(type_item.value_from(l=arg_vals[i]))
                elif type(type_item) is PTypes:
                    out_vals.append(type_item.value.value_from(arg_vals[i]))
                else:
                    out_vals.append(PTypes[type_item].value.value_from(arg_vals[i]))

            return tuple(out_vals)

        except IncorrectArgCount as e:
            traceback.print_stack()
            print(f"\nInvalid number of args given: {y} ({x} required).\n")

    def get_types_count(self) -> int:
        count = 0
        for t in self._type_tree:
            if isinstance(t, Tuple):
                count += t.get_types_count()
            else:
                count += 1
        return count

    def get_types(self) -> list[str]:
        return self._type_tree

    def __str__(self):
        buf = [str(x) for x in self._type_tree]
        return f"({', '.join(buf)})"


# tuple_one = Tuple(["u8", "u64", ["u16", "u32"]], "u128", ("u16", "u16"), check=True)
# tuple_one_vals = tuple_one.value_from(1, 1, 2, 3, 4, (5, 6))

# tuple_two = Tuple(("u16", "u8", "char", ("u16", "u8")), "char", check=True)
# tuple_two_vals = tuple_two.value_from((1, 1, "c", (1, 1)), "d")

# tuple_three = Tuple(PTypes.u8, PTypes.u16)
# tuple_three_vals = tuple_three.value_from(16, 16)
# print(tuple_three_vals)

# ==============================================================================================
# ==============================================================================================


class Struct:
    def __init__(
        self, *args: _PrimitiveType_ | list[_PrimitiveType_], **kwargs
    ) -> Struct:
        try:
            check = kwargs.get("check") if type(kwargs.get("check")) is bool else True
            arg_list = list(args)

            if check == True:
                Struct._check_arg_list(arg_list)

            self._type_list = arg_list
        except UnknownTypeArgument as e:
            traceback.print_stack()
            print(f"\nUnknown type: '{e.args[0]}' provided in struct assignment.\n")

    @staticmethod
    def _check_arg_list(__list):
        for arg in __list:
            if type(arg) is dict:
                print("Dict time")
            elif type(arg) is tuple and len(arg) == 2:
                print(f"HERE: {arg[-1]}")
    @staticmethod
    def _convert_recursive_objects():
        print("CONVERT")

    # def get_types(self) -> list[str]:
    #     return self._type_tree

    # def __str__(self):
    #     buf = [str(x) for x in self._type_tree]
    #     return f"({', '.join(buf)})"


struct_one = Struct({"A": "u16", "B": "u8"})
print(struct_one)

struct_two = Struct({"A": PTypes.u16, "B": PTypes.str})
print(struct_two)

struct_three = Struct(("A", PTypes.u8), ("B", "u8"))
print(struct_three)