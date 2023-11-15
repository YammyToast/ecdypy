import sys
import os

import pytest
import warnings

import re

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from ecdypy.rconstructs import Variable
from ecdypy.rtypes import RTypes, Tuple, Struct

replace_pattern = r"[\n\t\s]*"

# ==============================================================================================
# ==============================================================================================


def test_variables_basic():
    variable_one = Variable("my_var_1", RTypes.i32, 10)
    assert str(variable_one) == "my_var_1"
    one_declaration = re.sub(replace_pattern, "", variable_one.get_declaration())
    assert str(one_declaration) == "letmy_var_1:i32=10;"

    variable_one_alt = Variable("my_var_1", "i32", 10)
    one_declaration_alt = re.sub(
        replace_pattern, "", variable_one_alt.get_declaration()
    )
    assert str(one_declaration_alt) == str(one_declaration)

    variable_two = Variable("my_var_2", RTypes.char, "c")
    two_declaration = re.sub(replace_pattern, "", variable_two.get_declaration())
    assert str(two_declaration) == "letmy_var_2:char='c';"

    my_struct = Struct({"A": "u8", "B": "u16"}, name="struct_one")
    variable_three = Variable("my_var_3", my_struct, {"A": 16, "B": 16})
    three_declaration = re.sub(replace_pattern, "", variable_three.get_declaration())
    assert (
        str(three_declaration) == """letmy_var_3:struct_one=struct_one{A:16,B:16,};"""
    )
