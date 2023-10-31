from pathlib import Path
import sys
import os

import pytest
import warnings

from ecdypy.rtypes import RTypes

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
    const = (2**64)-1
    assert t.value_from(const) == const
    assert t.value_from(const+1) == const
    assert t.value_from(-1) == 0

    assert t.is_ok(const) == True
    assert t.is_ok(const+1) == False
    assert t.is_ok(-1) == False

def test_type_i64():
    t = RTypes.i64.value
    const = (2**63)-1
    assert t.value_from(const) == const
    assert t.value_from(const+1) == const
    assert t.value_from(-const) == -const
    assert t.value_from(-const-1) == -const

    assert t.is_ok(const) == True
    assert t.is_ok(const+1) == False
    assert t.is_ok(-const) == True
    assert t.is_ok(-const-1) == False

def test_type_u128():
    t = RTypes.u128.value
    const = (2**128)-1
    assert t.value_from(const) == const
    assert t.value_from(const+1) == const
    assert t.value_from(-1) == 0

    assert t.is_ok(const) == True
    assert t.is_ok(const+1) == False
    assert t.is_ok(-1) == False

def test_type_i128():
    t = RTypes.i128.value
    const = (2**127)-1
    assert t.value_from(const) == const
    assert t.value_from(const+1) == const
    assert t.value_from(-const) == -const
    assert t.value_from(-const-1) == -const

    assert t.is_ok(const) == True
    assert t.is_ok(const+1) == False
    assert t.is_ok(-const) == True
    assert t.is_ok(-const-1) == False
    