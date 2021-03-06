# Copyright (C) 2004 Sami Hangaslammi
# Copyright (C) 2009 Mark A. Matienzo
#
# This file is part of worldcat, the Python WorldCat API module.
#
# worldcat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# worldcat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with worldcat.  If not, see <http://www.gnu.org/licenses/>.

# util/safeeval.py - Safe evaluation of python constants and expressions

# modified from http://code.activestate.com/recipes/286134/

import dis
import sys

_const_codes = map(dis.opmap.__getitem__, [
    'POP_TOP', 'ROT_TWO', 'ROT_THREE', 'ROT_FOUR', 'DUP_TOP',
    'BUILD_LIST', 'BUILD_MAP', 'BUILD_TUPLE',
    'LOAD_CONST', 'RETURN_VALUE', 'STORE_SUBSCR'])

_pyversion = sys.version.split()[0].split('.')

if map(int, _pyversion) >= [2, 6]:
    _const_codes.append(dis.opmap['STORE_MAP'])

_expr_codes = _const_codes + map(dis.opmap.__getitem__, [
    'UNARY_POSITIVE', 'UNARY_NEGATIVE', 'UNARY_NOT',
    'UNARY_INVERT', 'BINARY_POWER', 'BINARY_MULTIPLY',
    'BINARY_DIVIDE', 'BINARY_FLOOR_DIVIDE', 'BINARY_TRUE_DIVIDE',
    'BINARY_MODULO', 'BINARY_ADD', 'BINARY_SUBTRACT',
    'BINARY_LSHIFT', 'BINARY_RSHIFT', 'BINARY_AND', 'BINARY_XOR',
    'BINARY_OR'])


def _get_opcodes(codeobj):
    """_get_opcodes(codeobj) -> [opcodes]

    Extract the actual opcodes as a list from a code object

    >>> c = compile("[1 + 2, (1,2)]", "", "eval")
    >>> _get_opcodes(c)
    [100, 100, 23, 100, 100, 102, 103, 83]
    """
    i = 0
    opcodes = []
    s = codeobj.co_code
    while i < len(s):
        code = ord(s[i])
        opcodes.append(code)
        if code >= dis.HAVE_ARGUMENT:
            i += 3
        else:
            i += 1
    return opcodes


def test_expr(expr, allowed_codes):
    """test_expr(expr) -> codeobj

    Test that the expression contains only the listed opcodes.
    If the expression is valid and contains only allowed codes,
    return the compiled code object. Otherwise raise a ValueError
    """
    try:
        c = compile(expr, "", "eval")
    except:
        raise ValueError, "%s is not a valid expression" % expr
    codes = _get_opcodes(c)
    for code in codes:
        if code not in allowed_codes:
            raise ValueError, "opcode %s not allowed" % dis.opname[code]
    return c


def const_eval(expr):
    """const_eval(expression) -> value

    Safe Python constant evaluation

    Evaluates a string that contains an expression describing
    a Python constant. Strings that are not valid Python expressions
    or that contain other code besides the constant raise ValueError.

    >>> const_eval("10")
    10
    >>> const_eval("[1,2, (3,4), {'foo':'bar'}]")
    [1, 2, (3, 4), {'foo': 'bar'}]
    >>> const_eval("1+2")
    Traceback (most recent call last):
    ...
    ValueError: opcode BINARY_ADD not allowed
    """
    c = test_expr(expr, _const_codes)
    return eval(c)


def expr_eval(expr):
    """expr_eval(expression) -> value

    Safe Python expression evaluation

    Evaluates a string that contains an expression that only
    uses Python constants. This can be used to e.g. evaluate
    a numerical expression from an untrusted source.

    >>> expr_eval("1+2")
    3
    >>> expr_eval("[1,2]*2")
    [1, 2, 1, 2]
    >>> expr_eval("__import__('sys').modules")
    Traceback (most recent call last):
    ...
    ValueError: opcode LOAD_NAME not allowed
    """
    c = test_expr(expr, _expr_codes)
    return eval(c)
