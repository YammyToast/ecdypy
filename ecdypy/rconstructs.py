from __future__ import annotations

from abc import ABC, abstractmethod
import traceback

from .codewriter import default_formatter
from .rtypes import _TYPE_, RTypes, Tuple, Struct

class Variable:
    def __init__(self, *args, **kwargs) -> None:
        print(args, len(args))
        print(kwargs, len(kwargs))


my_var_1 = Variable("my_var_1", RTypes.i32, 10)