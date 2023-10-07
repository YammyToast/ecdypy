from pathlib import Path
import sys
import os

import pytest
import warnings

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from ecdypy.codewriter import CodeWriter, CodeText, default_formatter


def test_codewriter_add_autogen_comment():
    cwr = CodeWriter()
    cwr.add_auto_gen_comment(
        "MIT",
        [
            "James Hardy <cyanjamesmail@gmail.com>",
            "Nathan Webb <nathanwebb02@outlook.com>",
        ],
    )
    x = str(cwr)


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


def test_codewriter_add():
    cwr = CodeWriter()
    cwr.add("Line 1")

    cwr2 = CodeWriter()
    cwr.add("Line 2")
    
    cwr3 = cwr + cwr2
    assert len(cwr3) == 2

def test_codewriter_iadd():
    

test_codewriter_iadd()
