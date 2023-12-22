from __future__ import annotations

""" Abstract Base Class """
from abc import ABC, abstractmethod


class Macro:
    """Helper Class for creating generic Macro definitions.

    Examples:
        >>> macros_one = Macro("DatabaseQuery<New>")
        >>> variable_one = Variable("my_var_1", RTypes.i16, 127, macros=macros_one)
        >>> print(variable_one.get_declaration())
        >>> # #[DatabaseQuery<New>]
        >>> # let my_var_2: i16 = 127;
    """

    def __init__(self, __text) -> None:
        self._text = str(__text)

    def get_text(self) -> str:
        """Get the code denoting the created Macro.

        This method is equivalent to the Macro __str__.

        Examples:
            >>> import ecdypy as ec
            >>> macro = ec.Macro("DatabaseQuery<New>")
            >>> print(macro.get_text())
            >>> # #[DatabaseQuery<New>]

        :return: Text denoting the Macro.
        :rtype: str
        """
        return f"#[{self._text}]"

    def __str__(self) -> str:
        return self.get_text()


class Derive:
    """Helper Class for quickly creating Derive Macros

    Examples:
        >>> import ecdypy as ec
        >>> macros_one = Derive("Debug", "PartialEq")
        >>> variable_one = Variable("my_var_1", RTypes.i32, -5, macros=macros_one)
        >>> print(variable_one.get_declaration())
        >>> # #[derive(Debug,PartialEq)]
        >>> # let my_var_1: i32 = -5;
    """

    def __init__(self, *args) -> None:
        arg_vals = list(args)
        arg_vals = [str(x) for x in arg_vals]
        self._args = arg_vals

    def get_text(self) -> str:
        """Get the code denoting the created Derive Macro.

        This method is equivalent to the Derive __str__.


        Examples:
            >>> import ecdypy as ec
            >>> macros_one = Derive("Debug", "PartialEq")
            >>> print(macros_one.get_text())
            >>> # #[derive(Debug,PartialEq)]

        :return: Text denoting the Macro.
        :rtype: str
        """
        return f"#[derive({','.join(self._args)})]"

    def __str__(self) -> str:
        return self.get_text()
