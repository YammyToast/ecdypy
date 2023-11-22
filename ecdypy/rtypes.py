from __future__ import annotations

""" Abstract Base Class """
from abc import ABC, abstractmethod
from enum import Enum
import traceback

from .codewriter import Formatter, default_formatter, _DECLARABLE_

import re
import copy


class UnknownTypeArgument(Exception):
    """Argument passed as a type-parameter is not recognised."""

    pass


class UnknownArgKeys(Exception):
    """Unknown key/field given in struct instantiation."""

    pass


class AttributesNotSatisfied(Exception):
    """Key/Field not satisfied in struct instantiation."""

    pass


class IncorrectArgCount(Exception):
    """Incorrect number of arguments given in object call."""

    pass


class InvalidStructAttributeName(Exception):
    """Invalid name provided for struct attribute."""

    pass


class InvalidName(Exception):
    """Invalid name provided for struct."""

    pass


class _TYPE_(ABC):
    """Generic Interface for types in ecdypy."""

    def __init__(self, __display_form: str) -> None:
        try:
            self._display_form = __display_form
        except Exception as e:
            print(e)

    @abstractmethod
    def value_from(self, __value):
        """Filter a value through the given type template."""
        pass

    @abstractmethod
    def is_ok(self, __value) -> bool:
        """Check whether a provided value obeys the types constraints."""
        pass

    @abstractmethod
    def __str__(self):
        pass


# ==============================================================================================
# ==============================================================================================


class _NUMBER_(_TYPE_):
    """Generic _TYPE_ interface-function implementations."""

    def value_from(self, __value):
        try:
            if self.is_ok(__value):
                return int(__value)
            elif int(__value) <= self.min_value:
                return int(self.min_value)
            elif int(__value) >= self.max_value:
                return int(self.max_value)
            else:
                raise
        except Exception:
            print(f"Cannot assign value: {__value} to type {self._display_form}.")

    def is_ok(self, __value: int) -> bool:
        if type(__value) is not int:
            return False
        return int(__value) <= self.max_value and int(__value) >= self.min_value

    def __str__(self) -> str:
        return self._display_form


class _U8_(_NUMBER_):
    min_value = 0
    max_value = 255


class _I8_(_NUMBER_):
    min_value = -127
    max_value = 127


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


class _BOOLEAN_(_TYPE_):
    def value_from(self, __value: bool | int | str) -> str:
        try:
            if not self.is_ok(__value):
                raise
            __value = str(__value)
            if re.search(r"^(1|true|True)$", __value) != None:
                return "true"
            elif re.search(r"^(0|false|False)$", __value) != None:
                return "false"
            else:
                raise
        except Exception as e:
            traceback.print_stack()
            print(f"Cannot assign value: {__value} to type bool.")

    def is_ok(self, __value) -> bool:
        if type(__value) is bool:
            return True
        elif __value == 0 or __value == 1:
            return True
        elif __value.lower() == "true" or __value.lower() == "false":
            return True
        else:
            return False

    def __str__(self):
        return self._display_form


class _STR_(_TYPE_):
    def value_from(self, __value: str | int | bool) -> str:
        return str(__value)

    def is_ok(self, __value: str):
        # the code of doom
        return True

    def __str__(self):
        return self._display_form


class _CHAR_(_TYPE_):
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


class RTypes(Enum):
    """Enum of Rust's Data Types as per: https://doc.rust-lang.org/book/ch03-02-data-types.html
    Examples:
        Generic Usage:
        >>> Variable("my_var_1", RTypes.u32, ...)

        Alternative "string" method of invoking RTypes.u32:
        >>> Variable("my_var_2", "u32", ...)

        Similar usage for Tuples and Structs:
        >>> # Enum and string methods within the same statements.
        >>> Struct(name="my_struct_1", {"A": "RTypes.u8", "B": "u16"})
        >>> Tuple(RTypes.i32, RTypes.char, "f32")

    Attributes:
        u8: "u8"

        u16: "u16"

        u32: "u32"

        u64: "u64"

        u128: "u128"

        usize: "usize"

        i8: "i8"

        i16: "i16"

        i32: "i32"

        i64: "i64"

        i128: "i128"

        isize: "isize"

        f32: "f32"

        f64: "f64"

        bool: "bool"

        str: "str"

        char: "char"
    """

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
    char = _CHAR_("char")


# ==============================================================================================
# ==============================================================================================


def normalize_arg_type(__type):
    new = __type
    if RTypes._member_names_.__contains__(__type):
        new = RTypes[__type]
    return new


class Tuple(_TYPE_):
    """Class for creating Rust Tuples for type declarations and value filtering.

    Used to set Rust data-types as a Tuple of existing or user-defined types.

    Tuples can be used as Type arguments in other types and constructs.
    Implementation per: https://doc.rust-lang.org/rust-by-example/primitives/tuples.html

    Examples:
    >>> import ecdypy as ec
    >>> my_tuple = ec.Tuple(ec.RTypes.u16, ec.RTypes.u16, check=True)
    >>> my_variable = ec.Variable("my_var", my_tuple)
    >>> my_value = my_variable.value_from(16, 32)
    >>> print(my_value) # (16, 32)
    >>> print(my_variable.get_declaration()) # let my_var: (u16, u16);
    >>>
    >>> complex_tuple = ec.Tuple(ec.RTypes.u8, my_tuple)
    >>> complex_variable = ec.Variable("complex", complex_tuple)
    >>> print(complex_variable.get_declaration()) # let complex: (u8, (u16, u16))
    """

    def __init__(self, *args: _TYPE_ | list[_TYPE_], **kwargs) -> None:
        """Ecdypy Tuple Constructor

        Args:
            *args:
                _TYPE_: An object that implements the _TYPE_ interface.

                list[_TYPE_]: A list of objects that implement the _TYPE_ interface.


            \\*\\*kwargs: keyword arguments in ['check']

                check: bool (default=True)

        Examples:
            >>> import ecdypy as ec
            >>> tuple_one = ec.Tuple(ec.RTypes.u16, ec.RTypes.u16) # Check = True
            >>> tuple_two = ec.Tuple([ec.RTypes.i16, ec.RTypes.i32], check=False) # Check = False
            >>> tuple_three = ec.Tuple(tuple_two, ec.RTypes.i16, [ec.RTypes.u8, ec.RTypes.usize])
            >>> tuple_four = ec.Tuple((ec.RTypes.i16, ec.RTypes.u16), ec.RTypes.i32)
            >>> \n
            >>> print(tuple_one) # (u16, u16)
            >>> print(tuple_two) # (i16, i32)
            >>> print(tuple_three) # ((i16, i32), i16, u8, usize)
            >>> print(tuple_four) # ((i16, u16), i32)

        """
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
            if type(arg) is Tuple:
                continue
            # why is contains dunder???????
            if not (RTypes._member_names_.__contains__(arg) or arg in RTypes):
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
        __list[0] = normalize_arg_type(__list[0])
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

    @staticmethod
    def _flatten_lists(__list):
        if len(__list) == 0:
            return __list
        if isinstance(__list[0], list):
            return Tuple._flatten_lists(__list[0]) + Tuple._flatten_lists(__list[1:])
        return __list[:1] + Tuple._flatten_lists(__list[1:])

    def is_ok(self, *args: _TYPE_ | list[_TYPE_]) -> bool:
        """Checks whether a given set of values fits all of the Tuple's type constraints.

        Examples:
            >>> import ecdypy as ec
            >>> tuple_one = ec.Tuple(ec.RTypes.u16, ec.RTypes.u16)
            >>> tuple_two = ec.Tuple((ec.RTypes.i16, ec.RTypes.u16), ec.RTypes.i32)
            >>> \n
            >>> assert tuple_one.is_ok(16, 16) == True
            >>> assert tuple_one.is_ok(-1, 16) == False
            >>> assert tuple_one.is_ok([16, 16]) == True # ! THROWS ERROR
            >>> assert tuple_two.is_ok((16, 16), 32) == True

        Args:
            *args:
                _TYPE_: An object that implements the _TYPE_ interface.

                list[_TYPE_]: A list of objects that implement the _TYPE_ interface.


        :return: bool. True if the given values fit within the Tuple's types constraints. False otherwise.
        :rtype: bool
        """
        arg_vals = list(args)
        # SHOULD CHECK IF ANY OF THE VALUES HAVE BEEN CHANGED. IF SO, NOT OKAY!
        if (self.get_types_count()) != (len(Tuple._flatten_args(list(arg_vals)))):
            return False
        if len(self._verify_vals(arg_vals)) != len(arg_vals):
            return False
        return True

    def _verify_vals(self, __args, __make_list: bool = False) -> list[_TYPE_]:
        if __make_list == True:
            __args = list(__args)

        out_vals = []
        for i, type_item in enumerate(self._type_tree):
            if type(type_item) is Tuple:
                out_vals.append(type_item._verify_vals(__args[i], True))
            elif type(type_item) is RTypes:
                out_vals.append(type_item.value.value_from(__args[i]))
            else:
                out_vals.append(RTypes[type_item].value.value_from(__args[i]))
        return tuple(out_vals)

    def value_from(self, *args: _TYPE_ | list[_TYPE_]) -> tuple:
        """Filter a set of input values through the contraints of the Tuple's types.

        Examples:
        >>> import ecdypy as ec
        >>> tuple_one = ec.Tuple(ec.RTypes.u16, ec.RTypes.u16)
        >>> tuple_two = ec.Tuple((ec.RTypes.i16, ec.RTypes.u16), ec.RTypes.i32)
        >>> \n
        >>> print(tuple_one.value_from(16, 32)) # (16, 32)
        >>> print(tuple_one.value_from([16, 32])) # (16, 32)
        >>> print(tuple_two.value_from((16, 32), -16)) # ((16,32), -16)
        >>> print(tuple_two.value_from([(16, 32), -16])) # ((16,32), -16)

        Args:
            *args:
                _TYPE_: An object that implements the _TYPE_ interface.

                list[_TYPE_]: A list of objects that implement the _TYPE_ interface.


        :raises IncorrectArgCount: Raised when the number of input values does not match the number of types in the tuple.
        :return: A tuple of filtered values.
        :rtype: tuple
        """
        try:
            arg_vals = Tuple._flatten_lists(list(args))
            if (x := self.get_types_count()) != (
                y := len(Tuple._flatten_args(list(arg_vals)))
            ):
                raise IncorrectArgCount

            return tuple(self._verify_vals(arg_vals))

        except IncorrectArgCount as e:
            traceback.print_stack()
            print(f"\nInvalid number of args given: {y} ({x} required).\n")

    def get_types_count(self) -> int:
        """Returns the number of types in the Tuple, including those in nested Tuples.

        :return: int. Number of types in Tuple.
        :rtype: int
        """
        count = 0
        for t in self._type_tree:
            if isinstance(t, Tuple):
                count += t.get_types_count()
            else:
                count += 1
        return count

    def get_types(self) -> list[str]:
        """Returns the type tree of the Tuple.

        :return: _description_
        :rtype: list[str]
        """
        return self._type_tree

    def __str__(self):
        """Generates the string representation of the tuple.


        :return: str. String representation of tuple.
        :rtype: str
        """
        buf = [str(x) for x in self._type_tree]
        buf = []
        for x in self._type_tree:
            if type(x) is RTypes:
                buf.append(str(x.value))
            else:
                buf.append(str(x))
        return f"({', '.join(buf)})"


# ==============================================================================================
# ==============================================================================================


class Struct(_TYPE_, _DECLARABLE_):
    """Class for creating Rust Structs. Can be used as type arguments or for writing struct declarations.

    Struct objects can be passed as a type argument into any appropriate function. Ecdypy does not automatically declare Structs,
    therefore the user must add a declaration prior to its usage as a type.

    Structs can be used as Type arguments in other types and constructs.
    Implementation per: https://doc.rust-lang.org/book/ch05-01-defining-structs.html

    Examples:
    >>> import ecdypy as ec
    >>> struct_one = ec.Struct({"A": "u8", "B": "u16"}, name="my_struct")
    >>> print(struct_one) # my_struct
    >>> print(struct_one.get_declaration())
    >>> # struct struct_one {
    >>> #   A: u8,
    >>> #    B: u16
    >>> # }

    """

    def __init__(self, *args: _TYPE_ | list[_TYPE_], **kwargs) -> Struct:
        """Ecdypy Struct Constructor

        Args:
            *args:
                _TYPE_: An object that implements the _TYPE_ interface.

                list[_TYPE_]: A list of objects that implement the _TYPE_ interface.


            \\*\\*kwargs: keyword arguments in ['check', 'name']

                check: bool (default=True)

                name: str (default=None, required=True)

        Examples:
            >>> import ecdypy as ec
            >>> struct_one = ec.Struct({"A": "u8", "B": "u16"}, name="my_struct")
            >>> print(struct_one) # my_struct
            >>> print(struct_one.get_declaration())
            >>> # struct struct_one {
            >>> #   A: u8,
            >>> #   B: u16
            >>> # }
            ____
            >>> struct_two = Struct(
            >>>     {"A": RTypes.u16, "B": RTypes.str}, {"C": RTypes.i8},
            >>>     name=split
            >>> )
            >>> print(struct_two) # split
            >>> print(struct_two.get_declaration())
            >>> # struct split {
            >>> #   A: u16,
            >>> #   B: str,
            >>> #   C: i8
            >>> # }
        """
        try:
            check = kwargs.get("check") if type(kwargs.get("check")) is bool else True
            name = kwargs.get("name")
            if name is None:
                raise InvalidName

            arg_list = list(args)

            if check == True:
                Struct._check_arg_list(arg_list)

            types = Struct._convert_arg_format(arg_list)
            types = Struct._normalize_args(types)

            self._type_list = arg_list
            self._type_tree = types
            self._name = name

        except InvalidName as e:
            traceback.print_stack()
            print(f"\nInvalid or no 'name' argument provided in struct assignment.\n")
        except UnknownTypeArgument as e:
            traceback.print_stack()
            print(f"\nUnknown type: '{e.args[0]}' provided in struct assignment.\n")
        except InvalidStructAttributeName as e:
            traceback.print_stack()
            print(
                f"\nInvalid attribute name: '{e.args[0]}' provided in struct assignment."
            )
        except Exception as e:
            traceback.print_stack()
            print(f"\nCannot assign type: {type(e.args[0])} to struct. ({e.args[0]})\n")

    @staticmethod
    def _check_arg_list(__list):
        for arg in __list:
            if type(arg) is dict:
                for key, value in arg.items():
                    if re.search(r"^([a-zA-Z_]{1}.*)$", key) is None:
                        raise InvalidStructAttributeName(key)
                    Struct._check_arg_type(value)
            # Handle Tuples
            elif type(arg) is tuple and len(arg) == 2:
                Struct._check_arg_type(arg[-1])
                if re.search(r"^([a-zA-Z_]{1}.*)$", arg[0]) is None:
                    raise InvalidStructAttributeName(arg[0])
            else:
                raise UnknownTypeArgument(arg)

    @staticmethod
    def _check_arg_type(__arg):
        if type(__arg) is Struct:
            Struct._check_arg_list(__arg._type_tree)
            return
        elif type(__arg) is Tuple:
            Tuple._check_arg_list(__arg._type_tree)
            return
        elif type(__arg) is tuple:
            for x in list(__arg):
                Struct._check_arg_type(x)
            return
        elif type(__arg) is str:
            if not RTypes._member_names_.__contains__(__arg):
                raise UnknownTypeArgument(__arg)
            return
        elif type(__arg) is not RTypes:
            raise UnknownTypeArgument(__arg)
        return

    @staticmethod
    def _convert_arg_format(__list):
        buf = []
        for arg in __list:
            if type(arg) is dict:
                buf.extend([(x, y) for x, y in arg.items()])
                pass
            else:
                buf.append(arg)
        return buf

    @staticmethod
    def _normalize_args(__list):
        buf = []
        for arg in __list:
            if type(arg[1]) is tuple:
                value = Tuple(list(arg[1]))
                buf.append((arg[0], value))
            else:
                buf.append((arg[0], normalize_arg_type(arg[1])))
        return buf

    def is_ok(self, *args: _TYPE_, **kwargs):
        """Checks whether a given set of values respectively meet the constraints of the Struct's attributes.

        Examples:
            >>> import ecdypy as ec
            >>> struct_one = ec.Struct({"A": "u8", "B": "u16"}, name="my_struct")
            >>> assert struct_one.is_ok({"A": 16, "B": 16}) == True
            ____
            >>> struct_two = Struct(
            >>>     {"A": RTypes.u16, "B": RTypes.str}, {"C": RTypes.i8},
            >>>     name=struct_two_name
            >>> )
            >>> assert struct_two.is_ok({"A": 32, "B": "foo", "C": -10}) == True

        Args:
            *args:
                _TYPE_: An object that implements the _TYPE_ interface.

                list[_TYPE_]: A list of objects that implement the _TYPE_ interface.


        :return: bool. True if the given values fit within the Struct's types constraints. False otherwise.
        :rtype: bool
        """
        try:
            arg_vals = Struct._convert_arg_format(list(args))
            if len(arg_vals) != len(self._type_tree):
                return False
            out = self._verify_vals(arg_vals)
            if len(out[1]) > 0:
                return False
            return True
        except Exception as e:
            raise e

    def _verify_vals(self, __args: list):
        arg_vals = __args
        arg_ids = [x[0] for x in arg_vals]
        arg_values = [x[1] for x in arg_vals]
        tree_ids = [x[0] for x in self._type_tree]
        tree_types = [x[1] for x in self._type_tree]
        # Deep copy or else lists share pointer.
        satisy_list = copy.deepcopy(tree_ids)
        seen_list = []
        out_vals = []
        for i, arg in enumerate(arg_ids):
            if arg in seen_list:
                continue
            seen_list.append(arg)
            if not arg in tree_ids:
                continue
            satisy_list.remove(arg)

            target_type = tree_types[tree_ids.index(arg)]
            if type(target_type) is Struct:
                out = target_type._verify_vals(arg_values[i])
                if len(out[1]) > 0:
                    raise AttributesNotSatisfied(out[1], arg_values[i])
                out_vals.append((arg, str(target_type)))
            elif type(target_type) is Tuple:
                out = target_type.value_from(list(arg_values[i]))
                out_vals.append((arg, out))

            else:
                out_vals.append((arg, target_type.value.value_from(arg_values[i])))

        return out_vals, satisy_list

    def value_from(self, *args: _TYPE_ | list[_TYPE_]) -> str:
        """Filters a given set of values through their constraints of their respective type in the Struct's attributes.

        Examples:
        >>> import ecdypy as ec
        >>> struct_one = ec.Struct({"A": "u8", "B": "u16"}, name="my_struct")
        >>> print(struct_one.value_from({"A": 16, "B": 16}))
        >>> # struct_one {A: 16,B: 16,};
        ____
        >>> struct_two = Struct(
        >>>     {"A": RTypes.u16, "B": RTypes.str}, {"C": RTypes.i8},
        >>>     name=struct_two_name
        >>> )
        >>> print(struct_two.value_from({"A": 32, "B": "foo", "C": -10}))
        >>> # struct_two {A: 32,B: 'foo',C: -10,};


        Args:
            *args:
                _TYPE_: An object that implements the _TYPE_ interface.

                list[_TYPE_]: A list of objects that implement the _TYPE_ interface.


        :raises UnknownArgKeys: Unknown key/field given in struct instantiation.
        :raises AttributesNotSatisfied: Key/Field not satisfied in struct instantiation.
        :return: Initialization string for Struct with the given values.
        :rtype: str
        """
        try:
            arg_vals = Struct._convert_arg_format(list(args))
            out = self._verify_vals(arg_vals)
            if len(out[1]) > 0:
                raise AttributesNotSatisfied(out[1], arg_vals)
            if len(out[0]) < len(arg_vals):
                dif = list(set(arg_vals) - set(out[0]))
                raise UnknownArgKeys(dif)

            buf = f"{self.get_name()} {{"
            for pair in out[0]:
                val = f"'{pair[1]}'" if isinstance(pair[1], str) else pair[1]
                buf = buf + f"{pair[0]}: {val},"
            buf = buf + "};"

            return buf
        except UnknownArgKeys as e:
            traceback.print_stack()
            print(f"Unknown Key: '{e.args[0]}' provided. ({list(args)})'")
        except AttributesNotSatisfied as e:
            traceback.print_stack()
            print(
                f"Attributes with keys: {e.args[0]} not satisfied by input values. ({list(args)})"
            )

    def get_types(self) -> list[str]:
        """Returns the type tree of the Struct.

        :return: List of type names as str.
        :rtype: list[str]
        """
        return self._type_tree

    def get_name(self) -> str:
        """Returns the name of the Struct.

        :return: Name of Struct object as str.
        :rtype: str
        """
        return self._name

    def get_declaration(self, __formatter: Formatter = default_formatter) -> str:
        """Get the string representation of the Struct's declaration.

        Examples:
        >>> import ecdypy as ec
        >>> struct_one = ec.Struct({"A": "u8", "B": "u16"}, name="my_struct")
        >>> print(struct_one.get_declaration())
        >>> # struct struct_one {
        >>> #   A: u8,
        >>> #   B: u16
        >>> # }
        ____
        >>> struct_two = Struct(
        >>>     {"A": RTypes.u16, "B": RTypes.str}, {"C": RTypes.i8},
        >>>     name=split
        >>> )
        >>> print(struct_two.get_declaration())
        >>> # struct split {
        >>> #   A: u16,
        >>> #   B: str,
        >>> #   C: i8
        >>> # }

        :param __formatter: _description_, defaults to default_formatter
        :type __formatter: Formatter, optional
        :return: _description_
        :rtype: str
        """
        buf = []
        for x, y in self._type_tree:
            type_text = y
            if type(y) is RTypes:
                type_text = str(y.value)
            elif type(y) is Struct:
                type_text = y.get_name()
            elif type(y) is tuple:
                type_text = f"({','.join([str(z.value) for z in y])})"
            buf.append(f"{__formatter._indent_spaces*' '}{str(x)}: {str(type_text)}")
        return "struct {0} {{\n{1}\n}}".format(self._name, f",\n".join(buf))

    def __str__(self, __formatter: Formatter = default_formatter) -> str:
        """Generates the string representation of the struct.
        This is equivalent to returning the Struct's name.


        :return: str. Struct's name.
        :rtype: str
        """
        return self.get_name()
