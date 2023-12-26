from ecdypy.macros import Macro, Derive
from ecdypy.rtypes import RTypes, Tuple, Struct
from ecdypy.rconstructs import Variable, Function, MatchStatement, Arm
from ecdypy.codewriter import CodeWriter
import sys
import os

import warnings

import re

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


replace_pattern = r"[\n\t\s]*"

# ==============================================================================================
# ==============================================================================================


def test_variables_basic():
    variable_one = Variable("my_var_1", RTypes.i32, 10)
    assert str(variable_one) == "my_var_1"
    one_declaration = re.sub(replace_pattern, "", str(variable_one.get_declaration()))
    assert str(one_declaration) == "letmy_var_1:i32=10;"

    variable_one_alt = Variable("my_var_1", "i32", 10)
    one_declaration_alt = re.sub(
        replace_pattern, "", str(variable_one_alt.get_declaration())
    )
    assert str(one_declaration_alt) == str(one_declaration)

    variable_two = Variable("my_var_2", RTypes.char, "c")
    two_declaration = re.sub(replace_pattern, "", str(variable_two.get_declaration()))
    assert str(two_declaration) == "letmy_var_2:char='c';"

    my_struct = Struct({"A": "u8", "B": "u16"}, name="struct_one")
    variable_three = Variable("my_var_3", my_struct, {"A": 16, "B": 16})
    three_declaration = re.sub(
        replace_pattern, "", str(variable_three.get_declaration())
    )
    assert (
        str(three_declaration) == """letmy_var_3:struct_one=struct_one{A:16,B:16,};"""
    )

    my_tuple = Tuple("u8", RTypes.u16, RTypes.i16)
    variable_four = Variable("my_var_4", my_tuple, [8, 16, 32])
    four_declaration = re.sub(replace_pattern, "", str(variable_four.get_declaration()))
    assert four_declaration == """letmy_var_4:(u8,u16,i16)=(8,16,32);"""


def test_variables_extra():
    macros_one = Derive("Debug", "PartialEq")
    variable_one = Variable("my_var_1", RTypes.i32, -5, macros=macros_one)
    one_declaration = re.sub(replace_pattern, "", str(variable_one.get_declaration()))
    assert one_declaration == """#[derive(Debug,PartialEq)]letmy_var_1:i32=-5;"""

    macros_two = Macro("DatabaseQuery<New>")
    variable_two = Variable("my_var_2", RTypes.i16, 127, macros=macros_two)
    two_declaration = re.sub(replace_pattern, "", str(variable_two.get_declaration()))
    assert two_declaration == """#[DatabaseQuery<New>]letmy_var_2:i16=127;"""

    variable_three = Variable("my_var_3", RTypes.i16, variable_two)
    three_declaration = re.sub(
        replace_pattern, "", str(variable_three.get_declaration())
    )
    assert three_declaration == """letmy_var_3:i16=my_var_2;"""


# ==============================================================================================
# ==============================================================================================


def test_functions_init():
    my_parameter_map = [{"name": RTypes.str, "password": RTypes.str, "age": RTypes.u8}]

    my_func = Function("login", my_parameter_map, RTypes.str)
    assert str(my_func) == "login"
    my_func_decl = re.sub(replace_pattern, "", str(my_func._get_declaration()))
    my_func_def = re.sub(replace_pattern, "", str(my_func._get_definition()))
    assert my_func_decl == "fnlogin(name:str,password:str,age:u8)->str;"
    assert my_func_def == """fnlogin(name:str,password:str,age:u8)->str{}"""

    my_alt = Function(name="alt_login", parameters=my_parameter_map, returns=RTypes.str)
    alt_func_decl = re.sub(replace_pattern, "", str(my_alt._get_declaration()))
    alt_func_def = re.sub(replace_pattern, "", str(my_alt._get_definition()))
    assert str(my_alt) == "alt_login"
    assert alt_func_decl == "fnalt_login(name:str,password:str,age:u8)->str;"
    assert alt_func_def == """fnalt_login(name:str,password:str,age:u8)->str{}"""

    my_short = Function("short")
    assert str(my_short) == "short"
    short_func_decl = re.sub(replace_pattern, "", str(my_short._get_declaration()))
    short_func_def = re.sub(replace_pattern, "", str(my_short._get_definition()))
    assert str(short_func_decl) == "fnshort();"
    assert str(short_func_def) == "fnshort(){}"


def test_functions_add():
    cwr = CodeWriter()
    variable_one = Variable("my_var_1", RTypes.i32, 10)
    cwr.add(variable_one.get_declaration())

    my_func = Function(name="my_func", returns=RTypes.str)
    my_func.add(variable_one)
    cwr.add(my_func.get_definition())

    variable_two = Variable(name="my_var_2", type="i32", value=-256, check=False)
    cwr.add(variable_two.get_declaration())

    cwr_str = re.sub(replace_pattern, "", str(cwr))
    assert (
        cwr_str
        == """letmy_var_1:i32=10;fnmy_func()->str{letmy_var_1:i32=10;}letmy_var_2:i32=-256;"""
    )

    cwr.empty()
    my_inner_func = Function(name="get_name", returns=RTypes.str)
    my_func.add(my_inner_func.get_definition())
    my_inner_func.add(variable_two.get_declaration())

    cwr.add(my_func.get_definition())
    cwr_str = re.sub(replace_pattern, "", str(cwr))
    assert (
        cwr_str
        == """fnmy_func()->str{letmy_var_1:i32=10;fnget_name()->str{letmy_var_2:i32=-256;}}"""
    )


# ==============================================================================================
# ==============================================================================================


def test_arm():
    arm_one = Arm("test")

    variable_one = Variable("my_var_1", RTypes.i32, 10)

    arm_one.add(variable_one)
    arm_one_str = re.sub(replace_pattern, "", str(arm_one))
    assert arm_one_str == """test=>{letmy_var_1:i32=10;}"""
    # =====
    arm_default = Arm()

    tuple_template = Tuple(
        ["u8", "u64", ["u16", "u32"]], "u128", ("u16", "u16"), check=True
    )
    variable_two = Variable("my_var_2", tuple_template, [1, 1, 2, 3, 4, (5, 6)])

    arm_default.add(variable_two)
    arm_default_str = re.sub(replace_pattern, "", str(arm_default))
    assert (
        arm_default_str
        == """_=>{letmy_var_2:(u8,u64,u16,u32,u128,(u16,u16))=(1,1,2,3,4,(5,6));}"""
    )


def test_match_statement():
    cwr = CodeWriter()

    my_param = Variable("my_param", RTypes.i32, 5)
    match_one = MatchStatement(my_param)
    # =====
    arm_default = Arm()
    tuple_template = Tuple(
        ["u8", "u64", ["u16", "u32"]], "u128", ("u16", "u16"), check=True
    )
    variable_two = Variable("my_var_2", tuple_template, [1, 1, 2, 3, 4, (5, 6)])
    arm_default.add(variable_two)
    # =====
    arm_one = Arm("test")
    variable_one = Variable("my_var_1", RTypes.i32, 10)
    arm_one.add(variable_one)
    # =====
    # Add default arm first to check that it is always shuffled to be last.
    match_one.add(arm_default)
    match_one.add(arm_one)
    # =====
    match_one_str = re.sub(replace_pattern, "", str(match_one))
    assert (
        match_one_str
        == """matchmy_param{test=>{letmy_var_1:i32=10;},_=>{letmy_var_2:(u8,u64,u16,u32,u128,(u16,u16))=(1,1,2,3,4,(5,6));},}"""
    )
