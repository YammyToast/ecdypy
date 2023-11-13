from __future__ import annotations

from abc import ABC, abstractmethod
import traceback

import re

from .codewriter import default_formatter
from .rtypes import (
    _TYPE_,
    RTypes,
    Tuple,
    Struct,
    IncorrectArgCount,
    InvalidName,
    normalize_arg_type,
)


# ==============================================================================================
# ==============================================================================================


class Variable:
    def __init__(self, *args, **kwargs) -> None:
        try:
            arg_vals = Variable._parse_args(list(args), kwargs)
            if arg_vals.get("name") == -1:
                raise InvalidName
            # There's no way on this godforsaken planet that this is good code but idc it looks funny.
            if None in (e := [arg_vals.get("name"), arg_vals.get("type")]):
                raise IncorrectArgCount([a for a in e if a == None])
            print(arg_vals)
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

    @staticmethod
    def _parse_args(__args_list, __kwargs_list):
        arg_dict = {
            "name": dict(__kwargs_list).get("name"),
            "type": dict(__kwargs_list).get("type"),
            "value": dict(__kwargs_list).get("value"),
            "test": None,
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
        """Filter out none values"""
        return {k: v for k, v in arg_dict.items() if v != None}

    @staticmethod
    def _match_value(__type, __value):
        if isinstance(__type, _TYPE_):
            return __type.value_from(__value)
        if isinstance(__type, RTypes):
            return __type.value.value_from(__value)
