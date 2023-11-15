from __future__ import annotations

from abc import ABC, abstractmethod
import traceback

import re

from .codewriter import Formatter, default_formatter, _DECLARABLE_
from .rtypes import (
    _TYPE_,
    RTypes,
    Tuple,
    Struct,
    IncorrectArgCount,
    InvalidName,
    normalize_arg_type,
)


class InvalidMacroArg(Exception):
    pass


# ==============================================================================================
# ==============================================================================================


class Variable(_DECLARABLE_):
    def __init__(self, *args, **kwargs) -> None:
        try:
            arg_vals = Variable._parse_args(list(args), kwargs)
            if arg_vals.get("name") == -1:
                raise InvalidName

            name = arg_vals.get("name")
            typ = arg_vals.get("type")
            # There's no way on this godforsaken planet that this is good code but idc it looks funny.
            if None in (e := [name, type]):
                raise IncorrectArgCount([a for a in e if a == None])

            macros = arg_vals.get("macros", [])
            if None in (e := macros):
                raise InvalidMacroArg(e)

            self._name = name
            self._type = typ
            self._value = arg_vals.get("value")
            self._macros = arg_vals.get("macros")

        except IncorrectArgCount as e:
            traceback.print_stack()
            print(
                f"\nRequired Args Missing: {e.args[0]} ('name' and 'type' required).\n"
            )
        except InvalidName as e:
            traceback.print_stack()
            print(
                r"""\nInvalid 'name' argument provided in variable assignment.\n
                  https://rust-lang.github.io/api-guidelines/naming.html\n"""
            )
        except InvalidMacroArg as e:
            traceback.print_stack()
            print(f"\nInvalid Macro Argument given. (in {e.args[0]})")

    @staticmethod
    def _parse_args(__args_list, __kwargs_list):
        arg_dict = {
            "name": dict(__kwargs_list).get("name"),
            "type": dict(__kwargs_list).get("type"),
            "value": dict(__kwargs_list).get("value"),
            "attrs": dict(__kwargs_list).get("attrs"),
            "macros": dict(__kwargs_list).get("macros"),
        }
        for i, a in zip(list(arg_dict), __args_list):
            arg_dict[i] = a

        if (n := arg_dict["name"]) != None:
            arg_dict["name"] = (
                n
                if re.search(r"^([a-zA-Z\-\_]{1}[a-zA-Z\-\_0-9]*)$", n) != None
                else -1
            )
        if (t := arg_dict["type"]) != None:
            t = normalize_arg_type(t)

            if (v := arg_dict["value"]) != None:
                arg_dict["value"] = Variable._match_value(t, v)
        if (m := arg_dict["macros"]) != None:
            m = [str(m)] if not isinstance(m, list) else [str(x) for x in m]
            arg_dict["macros"] = m

        """Filter out none values"""
        return {k: v for k, v in arg_dict.items() if v != None}

    @staticmethod
    def _match_value(__type, __value):
        if isinstance(__value, Variable):
            # Change this should we want to do internal type checking?
            return __value

        if isinstance(__type, _TYPE_):
            return __type.value_from(__value)
        if isinstance(__type, RTypes):
            return __type.value.value_from(__value)

    def get_declaration(self, __formatter: Formatter = default_formatter) -> str:
        buf = ""
        if self._macros != None:
            buf = buf + "\n".join(self._macros) + "\n"

        typ = self._type.value if isinstance(self._type, RTypes) else self._type

        # This code feels awful
        val = self._value
        val_fmt = ""
        if isinstance(self._type, Struct):
            val_fmt = val
        elif self._type == RTypes.char:
            val_fmt = f"'{val}'"
        elif isinstance(val, str):
            val_fmt = f'"{val}"'
        else:
            val_fmt = str(val)

        buf = (
            buf
            + f"let {str(self._name)}: {str(typ)} = {val_fmt}{';' if val_fmt[-1] != ';' else ''}"
        )
        return buf

    def get_name(self) -> str:
        return self._name

    def get_type(self) -> _TYPE_:
        return self._type

    def __str__(self) -> str:
        return self._name
