"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret, Scalar


# Example test, you can adapt it to your needs.
def test_expr_construction():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b) * c * Scalar(4) + Scalar(3)
    assert repr(expr) == "((Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3))"

def test_expr_construction_example():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = a * b + c
    assert repr(expr) == "(Secret(1) * Secret(2) + Secret(3))"

def test_expr_construction1():
    a = Secret(1)
    b = Secret(2)
    expr = a - b
    assert repr(expr) == "(Secret(1) - Secret(2))"

def test_expr_construction2():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b + c) * Scalar(4)
    assert repr(expr) == "((Secret(1) + Secret(2)) + Secret(3)) * Scalar(4)"

def test_expr_construction3():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b + c) + Scalar(4)
    assert repr(expr) == "(((Secret(1) + Secret(2)) + Secret(3)) + Scalar(4))"

def test_expr_construction4():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a * Scalar(3) + b - c) + Scalar(4)
    assert repr(expr) == "(((Secret(1) * Scalar(3) + Secret(2)) - Secret(3)) + Scalar(4))"

def test_expr_construction5():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    d = Secret(4)
    expr = a + b + c + d
    assert repr(expr) == "(((Secret(1) + Secret(2)) + Secret(3)) + Secret(4))"

def test_expr_construction6():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    d = Secret(4)
    expr = a + b + c + d
    assert repr(expr) == "(((Secret(1) + Secret(2)) + Secret(3)) + Secret(4))"

def test_expr_construction7():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a * b) + (b * c) + (c * a)
    assert repr(expr) == "((Secret(1) * Secret(2) + Secret(2) * Secret(3)) + Secret(3) * Secret(1))"

def test_expr_construction8():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    d = Secret(4)
    e = Secret(5)
    expr = ((a + Scalar(3)) + b * Scalar(4) - c) * (d + e)
    assert repr(expr) == "(((Secret(1) + Scalar(3)) + Secret(2) * Scalar(4)) - Secret(3)) * (Secret(4) + Secret(5))"
