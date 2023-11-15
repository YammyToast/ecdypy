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
    assert str(variable_one.get_declaration()) == "let my_var_1: RTypes.i32"
    print(variable_one.get_declaration())