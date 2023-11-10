from pathlib import Path
import sys
import os
import re

import pytest
import warnings

from ecdypy.rtypes import RTypes, Tuple, Struct

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


def test_type_u8():
    t = RTypes.u8.value
    assert t.value_from(0) == 0
    assert t.value_from(1) == 1
    assert t.value_from(2) == 2
    assert t.value_from(255) == 255
    assert t.value_from(256) == 255
    assert t.value_from(-1) == 0
    assert t.value_from(-100) == 0

    assert t.is_ok(0) == True
    assert t.is_ok(1) == True
    assert t.is_ok(2) == True
    assert t.is_ok(255) == True
    assert t.is_ok(256) == False
    assert t.is_ok(-1) == False
    assert t.is_ok(-100) == False


def test_type_i8():
    t = RTypes.i8.value
    assert t.value_from(127) == 127
    assert t.value_from(128) == 127
    assert t.value_from(-1) == -1
    assert t.value_from(-2) == -2
    assert t.value_from(-127) == -127
    assert t.value_from(-128) == -127

    assert t.is_ok(127) == True
    assert t.is_ok(128) == False
    assert t.is_ok(-1) == True
    assert t.is_ok(-2) == True
    assert t.is_ok(-127) == True
    assert t.is_ok(-128) == False


def test_type_u16():
    t = RTypes.u16.value
    assert t.value_from(65535) == 65535
    assert t.value_from(65536) == 65535
    assert t.value_from(-1) == 0

    assert t.is_ok(65535) == True
    assert t.is_ok(65536) == False
    assert t.is_ok(-1) == False


def test_type_i16():
    t = RTypes.i16.value
    assert t.value_from(32767) == 32767
    assert t.value_from(32768) == 32767
    assert t.value_from(-32767) == -32767
    assert t.value_from(-32768) == -32767

    assert t.is_ok(32767) == True
    assert t.is_ok(32768) == False
    assert t.is_ok(-32767) == True
    assert t.is_ok(-32768) == False


def test_type_u32():
    t = RTypes.u32.value
    assert t.value_from(4294967295) == 4294967295
    assert t.value_from(4294967296) == 4294967295
    assert t.value_from(-1) == 0

    assert t.is_ok(4294967295) == True
    assert t.is_ok(4294967296) == False
    assert t.is_ok(-1) == False


def test_type_i32():
    t = RTypes.i32.value
    assert t.value_from(2147483647) == 2147483647
    assert t.value_from(2147483648) == 2147483647
    assert t.value_from(-2147483647) == -2147483647
    assert t.value_from(-2147483648) == -2147483647

    assert t.is_ok(2147483647) == True
    assert t.is_ok(2147483648) == False
    assert t.is_ok(-2147483647) == True
    assert t.is_ok(-2147483648) == False


def test_type_u64():
    t = RTypes.u64.value
    const = (2**64) - 1
    assert t.value_from(const) == const
    assert t.value_from(const + 1) == const
    assert t.value_from(-1) == 0

    assert t.is_ok(const) == True
    assert t.is_ok(const + 1) == False
    assert t.is_ok(-1) == False


def test_type_i64():
    t = RTypes.i64.value
    const = (2**63) - 1
    assert t.value_from(const) == const
    assert t.value_from(const + 1) == const
    assert t.value_from(-const) == -const
    assert t.value_from(-const - 1) == -const

    assert t.is_ok(const) == True
    assert t.is_ok(const + 1) == False
    assert t.is_ok(-const) == True
    assert t.is_ok(-const - 1) == False


def test_type_u128():
    t = RTypes.u128.value
    const = (2**128) - 1
    assert t.value_from(const) == const
    assert t.value_from(const + 1) == const
    assert t.value_from(-1) == 0

    assert t.is_ok(const) == True
    assert t.is_ok(const + 1) == False
    assert t.is_ok(-1) == False


def test_type_i128():
    t = RTypes.i128.value
    const = (2**127) - 1
    assert t.value_from(const) == const
    assert t.value_from(const + 1) == const
    assert t.value_from(-const) == -const
    assert t.value_from(-const - 1) == -const

    assert t.is_ok(const) == True
    assert t.is_ok(const + 1) == False
    assert t.is_ok(-const) == True
    assert t.is_ok(-const - 1) == False


# ==============================================================================================
# ==============================================================================================


def test_tuple_basic_assignment():
    tuple_one = Tuple(["u8", "u64", ["u16", "u32"]], "u128", ("u16", "u16"), check=True)
    assert str(tuple_one) == "(u8, u64, u16, u32, u128, (u16, u16))"
    tuple_one_vals = tuple_one.value_from(1, 1, 2, 3, 4, (5, 6))
    assert tuple_one_vals == (1, 1, 2, 3, 4, (5, 6))

    tuple_two = Tuple(("u16", "u8", "char", ("u16", "u8")), "bool", check=True)
    assert str(tuple_two) == "((u16, u8, char, (u16, u8)), bool)"
    tuple_two_vals = tuple_two.value_from((1, 1, "c", (1, 1)), 1)
    assert tuple_two_vals == ((1, 1, "c", (1, 1)), "true")

    tuple_three = Tuple(RTypes.u8, RTypes.u16)
    assert str(tuple_three) == "(u8, u16)"
    tuple_three_vals = tuple_three.value_from(16, 16)
    assert tuple_three_vals == (16, 16)


def test_tuple_compound_assignment():
    tuple_one = Tuple(RTypes.u8, RTypes.char)
    assert str(tuple_one) == "(u8, char)"

    tuple_two = Tuple(tuple_one, RTypes.i16)
    assert str(tuple_two) == "((u8, char), i16)"

    tuple_three = Tuple(tuple_one, tuple_two, RTypes.u8)
    assert str(tuple_three) == "((u8, char), ((u8, char), i16), u8)"

    assert tuple_one.value_from(8, "A") == (8, "A")
    assert tuple_two.value_from((8, "A"), -10) == ((8, "A"), -10)
    assert tuple_three.value_from((8, "A"), ((8, "A"), -10), 8)


# ==============================================================================================
# ==============================================================================================


def test_struct_basic_assignment():
    replace_pattern = r"[\n\t\s]*"
    struct_one = Struct({"A": "u8", "B": "u16"}, name="struct_one")
    assert str(struct_one) == "struct_one"
    assert struct_one.is_ok({"A": 16, "B": 16}) == True
    assert struct_one.value_from({"A": 16, "B": 16}) == [("A", 16), ("B", 16)]

    one_declaration = re.sub(replace_pattern, "", struct_one.get_declaration())
    assert one_declaration == r"structstruct_one{A:u8,B:u16}"

    struct_two_name = "struct_two"
    struct_two = Struct(
        {"A": RTypes.u16, "B": RTypes.str}, {"C": RTypes.i8}, name=struct_two_name
    )
    assert str(struct_two) == "struct_two"
    assert struct_two.is_ok({"A": 32, "B": "Burger", "C": -10}) == True
    struct_two_value = struct_two.value_from({"A": 32, "B": "Burger", "C": -10}) 
    assert struct_two_value == [
        ("A", 32),
        ("B", "Burger"),
        ("C", -10),
    ]

    struct_three = Struct(
        ("A", RTypes.u8),
        ("B", "u8"),
        ("C", struct_two),
        ("D", ("u8", RTypes.u8)),
        name="struct_three",
    )
    print(struct_three.is_ok({"A": 8, "B": 8, "C": struct_two_value, "D": (8, 8)}))

    # print(struct_three.get_declaration())
