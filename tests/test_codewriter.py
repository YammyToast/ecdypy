import sys
import os

import pytest
import warnings

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


from ecdypy.codewriter import CodeWriter, CodeText, default_formatter

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


test_codewriter_add_autogen_comment()
