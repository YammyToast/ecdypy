from __future__ import annotations

from abc import ABC, abstractmethod
import traceback

from collections import deque

import re

from .codewriter import (
    Formatter,
    default_formatter,
    _DECLARABLE_,
    _DEFINABLE_,
    _CONTAINER_,
    LazyString,
)
from .rtypes import (
    _TYPE_,
    RTypes,
    Tuple,
    Struct,
    IncorrectArgCount,
    InvalidName,
    _normalize_arg_type,
)


class InvalidMacroArg(Exception):
    pass


class InvalidParameterArgument(Exception):
    pass


# ==============================================================================================
# ==============================================================================================


class Variable(_DECLARABLE_):
    """Class for creating Rust Variables.

    Variables can be declared/initialized as well as be used as any 'value' argument.

    Examples:
        >>> import ecdypy as ec
        >>> variable_one = ec.Variable("my_var_1", ec.RTypes.i32, 10)
        >>> print(variable_one) # my_var_1
        >>> print(variable_one.get_declaration())
        >>> # let my_var_1: i32 = 10;

    """

    def __init__(self, *args, **kwargs) -> None:
        """Ecdypy Variable Constructor

        Args:
            *args:
                name {str}: In-code name of the variable. I.e. let my_var_one

                type {_TYPE_ | RTypes}: The type of the variable. It is required that the type implements the _TYPE_ interface.

                value: Initial value of the variable.

                attrs: List of attributes to assign to the variable.

                macros {list[Macro | Derive]}: List of macros to assign to the variable. Macros should be instances of, or inherit from, the Macro class.
            \\*\\*kwargs: keyword arguments in ['name', 'type', 'value', 'attrs', 'macros']
                See *args.

        Examples:
            >>> import ecdypy as ec
            >>> variable_one = ec.Variable("my_var_1", ec.RTypes.i32, 10)
            >>> print(variable_one.get_declaration())
            >>> # let my_var_1: i32 = 10;
            >>> print(variable_one)
            >>> # my_var_1
            >>> \n
            >>> derives = ec.Derive("Debug", "PartialEq")
            >>> variable_two = ec.Variable("macro_variable", RTypes.u64, 0, macros=derives)
            >>> print(variable_two.get_declaration())
            >>> #[derive(Debug,PartialEq)]
            >>> #let macro_variable: u64 = 0;
            >>> \n
            >>> my_tuple = ec.Tuple("u8", ec.RTypes.u16, ec.RTypes.i16)
            >>> variable_three = ec.Variable("tuple_variable", my_tuple, [8, 16, 32])
            >>> print(variable_three.get_declaration())
            >>> # let tuple_variable: (u8, u16, i16) = (8, 16, 32);


        """
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
        kwargs_list = dict(__kwargs_list)
        arg_dict = {
            "name": kwargs_list.get("name"),
            "type": kwargs_list.get("type"),
            "value": kwargs_list.get("value"),
            "attrs": kwargs_list.get("attrs"),
            "macros": kwargs_list.get("macros"),
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
            t = _normalize_arg_type(t)

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

    def get_declaration(self, __formatter: Formatter = default_formatter) -> LazyString:
        """Get the string representation of the variable declaration.

        Examples:
            >>> import ecdypy as ec
            >>> variable_one = Variable("my_var_1", RTypes.i32, 10)
            >>> print(variable_one.get_declaration())
            >>> # let my_var_1: i32 = 10;
            >>> \n
            >>> cwr = CodeWriter(...)
            >>> cwr.add(variable_one)
            >>> print(cwr)
            >>> # let my_var_1: i32 = 10;

        :return: LazyString which can be evaluated to retrieve the variable's declaration.
        :rtype: LazyString
        """
        return LazyString(self, getattr(self, "_get_declaration"))

    def _get_declaration(self, __formatter: Formatter = default_formatter) -> str:
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
        """Returns the set name of the variable as a string. This is equivalent to casting the variable as a string.

        Examples:
            >>> import ecdypy as ec
            >>> variable_one = Variable("my_var_1", RTypes.i32, 10)
            >>> print(variable_one.get_name())
            >>> # my_var_1
            >>> \n
            >>> assert variable_one.get_name() == str(variable_one)

        :return: Name given to the variable.
        :rtype: str
        """
        return self._name

    def get_type(self) -> _TYPE_:
        """Returns the object instance used as the variable's type.

        Examples:
            >>> import ecdypy as ec
            >>> variable_one = Variable("my_var_1", RTypes.i32, 10)
            >>> print(variable_one.get_type())
            >>> # i32
            >>> \n
            >>> assert isinstance(variable_one.get_type(), ec._TYPE_) == True

        :return: Type given to the variable.
        :rtype: _TYPE_
        """
        if type(self._type) is RTypes:
            return self._type.value
        return self._type

    def __str__(self) -> str:
        """
        Examples:
            >>> import ecdypy as ec
            >>> variable_one = Variable("my_var_1", RTypes.i32, 10)
            >>> print(str(variable_one))
            >>> # my_var_1
            >>> \n
            >>> assert str(variable_one) == variable_one.get_name()
        """
        return self.get_name()


# ==============================================================================================
# ==============================================================================================


class Function(_CONTAINER_, _DECLARABLE_, _DEFINABLE_):
    """Class for creating Rust Function.

    Functions can have other CodeObjects added to their closure, including other Functions.

    Examples:
        >>> import ecdypy as ec
        >>> my_parameter_map = [{"name": ec.RTypes.str, "password": ec.RTypes.str, "age": ec.RTypes.u8}]
        >>> my_func = ec.Function("login", my_parameter_map, ec.RTypes.str)
        >>> print(my_func.get_declaration())
        >>> # fn login(name: str, password: str, age: u8) -> str;
        >>> \n
        >>> variable_one = ec.Variable("my_var_1", ec.RTypes.i32, 10)
        >>> my_func.add(variable_one)
        >>> print(my_func.get_definition())
        >>> # fn login(name: str, password: str, age: u8) -> str {
        >>> #     let my_var_1: i32 = 10;
        >>> # }
    """

    def __init__(self, *args, **kwargs) -> None:
        """Ecdypy Function Constructor

        Args:
            *args:
                name {str}: In-code name of the variable. I.e. let my_var_one

                parameters {dict[str, _TYPE_]}: Dictionary of parameters. Where each key is the in-code name of the parameter and value is its type.

                returns {_TYPE_}: Return type of the function.

                attrs: List of attributes to assign to the variable.

                macros {list[Macro | Derive]}: List of macros to assign to the function. Macros should be instances of, or inherit from, the Macro class.
            \\*\\*kwargs: keyword arguments in ['name', 'parameters', 'returns', 'attrs', 'macros']
                See *args.

        Examples:
            >>> import ecdypy as ec
            >>> my_parameter_map = [{"name": ec.RTypes.str, "password": ec.RTypes.str, "age": ec.RTypes.u8}]
            >>> my_func = ec.Function("login", my_parameter_map, ec.RTypes.str)
            >>> print(my_func.get_declaration())
            >>> # fn login(name: str, password: str, age: u8) -> str;
            >>> \n
            >>> my_kwarg_func = ec.Function(name="alt_login", parameters=my_parameter_map, returns=ec.RTypes.str)
            >>> print(my_kwarg_func.get_declaration())
            >>> # fn alt_login(name: str, password: str, age: u8) -> str;
        """
        try:
            arg_vals = Function._parse_args(list(args), kwargs)

            name = arg_vals.get("name")
            parameters = arg_vals.get("parameters")
            returns = arg_vals.get("returns")

            if name == -1:
                raise InvalidName

            self._name = name
            self._parameters = parameters
            self._returns = returns
            super().__init__()

        except InvalidName as e:
            traceback.print_stack()
            print(
                f"""\nInvalid 'name' argument provided in function creation.\n
                  https://rust-lang.github.io/api-guidelines/naming.html\n"""
            )
        except InvalidParameterArgument as e:
            traceback.print_stack()
            print(
                f"""\nInvalid argument provided in function parameters: {e.args[0]}"""
            )

    @staticmethod
    def _parse_args(__args_list, __kwargs_list):
        kwargs_list = dict(__kwargs_list)
        arg_dict = {
            "name": kwargs_list.get("name"),
            "parameters": kwargs_list.get("parameters"),
            "returns": kwargs_list.get("returns"),
            "attrs": kwargs_list.get("attrs"),
            "macros": kwargs_list.get("macros"),
        }

        for i, a in zip(list(arg_dict), __args_list):
            arg_dict[i] = a

        if (n := arg_dict["name"]) != None:
            arg_dict["name"] = (
                n
                if re.search(r"^([a-zA-Z\-\_]{1}[a-zA-Z\-\_0-9]*)$", n) != None
                else -1
            )

        if (p := arg_dict["parameters"]) != None:
            p = [p] if not isinstance(p, list) else p
            param_map = Function._normalize_parameter_map(p)
            arg_dict["parameters"] = param_map
        return {k: v for k, v in arg_dict.items() if v != None}

    @staticmethod
    def _normalize_parameter_map(__parameter_map):
        buf = []
        for param in __parameter_map:
            if isinstance(param, dict):
                buf.extend((x, _normalize_arg_type(y)) for x, y in param.items())
            elif isinstance(param, tuple):
                buf.append((param[0], _normalize_arg_type(param[1])))
            elif isinstance(param, list):
                buf.extend(Function._normalize_parameter_map(param))
            else:
                raise InvalidParameterArgument(param)
        return buf

    def get_definition(self, __formatter: Formatter = default_formatter) -> LazyString:
        """Get the string representation of the variable definition.

        Examples:
            >>> import ecdypy as ec
            >>> my_parameter_map = [{"name": ec.RTypes.str, "password": ec.RTypes.str, "age": ec.RTypes.u8}]
            >>> my_func = ec.Function("login", my_parameter_map, ec.RTypes.str)
            >>> print(my_func.get_definition())
            >>> # fn login(name: str, password: str, age: u8) -> str {}
            >>> \n
            >>> variable_one = Variable("my_var_1", RTypes.i32, 10)
            >>> my_func.add(variable_one)
            >>> print(my_func.get_definition())
            >>> # fn login(name: str, password: str, age: u8) -> str {
            >>> # let my_var_1: i32 = 10;
            >>> # }

        :return: LazyString which can be evaluated to retrieve the variable's definition.
        :rtype: LazyString
        """
        return LazyString(self, getattr(self, "_get_definition"))

    def get_declaration(self, __formatter: Formatter = default_formatter) -> LazyString:
        """Get the string representation of the variable declaration.

        Examples:
            >>> import ecdypy as ec
            >>> my_parameter_map = [{"name": ec.RTypes.str, "password": ec.RTypes.str, "age": ec.RTypes.u8}]
            >>> my_func = ec.Function("login", my_parameter_map, ec.RTypes.str)
            >>> print(my_func.get_declaration())
            >>> # fn login(name: str, password: str, age: u8) -> str;
            
        :return: LazyString which can be evaluated to retrieve the variable's declaration.
        :rtype: LazyString
        """
        return LazyString(self, getattr(self, "_get_declaration"))

    def _get_definition(self, __formatter: Formatter = default_formatter):
        """THIS LOOKS SO GOOD, GOOD JOB ME FOR SURE!"""
        indent_spaces = " " * __formatter._indent_spaces * self._indent
        # Start with name of function, parameters and return type.
        # Add open curly bracket to start function closure
        buf = [self._get_declaration().strip(";") + f" {{"]

        # Iterate over lines in the closure.
        for line in self._code_obj_tree:
            # If line is a container we should tell it to increase its indent amount.
            if isinstance(line, LazyString):
                if isinstance(line._obj, _CONTAINER_):
                    line._obj._indent = self._indent + 1
            # Add the line to the buffer
            buf.append(f"{indent_spaces}{str(line)}")

        # Close open curly bracket
        # Have one less indent as it looks nicer :)
        buf.append(f"{' '*__formatter._indent_spaces*(self._indent-1)}}}")
        return "\n".join(buf)

    def _get_declaration(self, __formatter: Formatter = default_formatter):
        """THIS LOOKS SO GOOD, GOOD JOB ME FOR SURE!"""
        buf = f"fn {self._name}("
        if self._parameters != None:
            for param in self._parameters:
                typ = param[1].value if isinstance(param[1], RTypes) else param[1]
                buf += f"{str(param[0])}: {str(typ)}, "
            buf = buf.strip(", ")
        buf += f")"

        if self._returns != None:
            typ = (
                self._returns.value
                if isinstance(self._returns, RTypes)
                else self._returns
            )
            buf += f" -> {typ}"
        buf += f";"
        return buf

    def __str__(self):
        return self._name


# ==============================================================================================
# ==============================================================================================


class MatchStatement:
    pass
