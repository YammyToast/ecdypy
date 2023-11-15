import sys
import os

import pytest
import warnings

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from ecdypy.rconstructs import Variable
from ecdypy.rtypes import RTypes, Tuple, Struct

# ==============================================================================================
# ==============================================================================================

def test_variables_basic():
    variable_one = Variable("my_var_1", RTypes.i32, 10)
    assert str(variable_one) == "my_var_1"
    assert str(variable_one.get_declaration()) == "let my_var_1: i32 = 10;"

    variable_one_alt = Variable("my_var_1", "i32", 10)
    assert str(variable_one_alt.get_declaration()) == str(variable_one.get_declaration())

    variable_two = Variable("my_var_2", RTypes.char, "c")
    print(variable_two.get_declaration())