from ecdypy.rtypes import RTypes
from ecdypy.rconstructs import Variable, Function
from ecdypy.codewriter import CodeWriter, CodeText, default_formatter
import sys
import os

import pytest
import re
import warnings

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

replace_pattern = r"[\n\t\s]*"


# ==============================================================================================
# ==============================================================================================


def test_codewriter_add_autogen_comment():
    cwr = CodeWriter()
    cwr.add_auto_gen_comment(
        "MIT",
        [
            "Bingus <bingusbongus@gmail.com>",
            "Angoos <angoos@outlook.com>",
        ],
    )
    assert str(cwr)

    cwr_no_args = CodeWriter()
    cwr_no_args.add_auto_gen_comment()

    assert str(cwr_no_args)

    cwr_str_author = CodeWriter()
    cwr_str_author.add_auto_gen_comment(None, "James Hardy <cyanjamesmail@gmail.com>")

    assert str(cwr_str_author)


def test_codewriter_add_codetext():
    cwr = CodeWriter()
    text = CodeText("Sample Text 1")
    text.add_text()
    text.add_text("Paragraph 1")
    text += "Line 1"
    text = text + "Line 2"

    if default_formatter._separator == "\n":
        assert len(text) == 5
    else:
        warnings.warn(
            UserWarning(
                "'default-formatter' separator value changed and therefore cannot verify length."
            )
        )


def test_codewriter_concat():
    cwr = CodeWriter()
    cwr.add("Line 1")

    cwr2 = CodeWriter()
    cwr.add("Line 2")

    cwr3 = cwr + cwr2
    assert len(cwr3) == 2

    cwri = CodeWriter()
    cwri.add("Line 1")

    cwri2 = CodeWriter()
    cwri2.add("Line 2")

    cwri += cwri2
    assert len(cwri) == 2


def test_codewriter_container():
    cwr = CodeWriter()
    my_parameter_map = [{"name": RTypes.str, "password": RTypes.str, "age": RTypes.u8}]

    my_func = Function("login", my_parameter_map, RTypes.str)
    my_func.add("Test")

    cwr.add(my_func.get_definition())
    cwr_str = re.sub(replace_pattern, "", str(cwr))
    assert cwr_str == """fnlogin(name:str,password:str,age:u8)->str{Test}"""

    my_variable = Variable("my_var_1", RTypes.i32, 10)

    my_func.empty()
    my_func.add(my_variable)
    cwr.add(my_func.get_definition())
    cwr_str_two = re.sub(replace_pattern, "", str(cwr))

    # Lazy Loading should have it that both function definitions have the variable, rather than "Test".
    assert (
        cwr_str_two
        == """fnlogin(name:str,password:str,age:u8)->str{letmy_var_1:i32=10;}fnlogin(name:str,password:str,age:u8)->str{letmy_var_1:i32=10;}"""
    )

    cwr.empty()
    assert str(cwr) == ""
