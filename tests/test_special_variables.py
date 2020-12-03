import pytest
from realm.algorithm import Algorithm
from realm.special_variables import SpecialVariables


def test_polynomial_naming():
    sv = SpecialVariables()
    polynomial_dict = {
        "name": "triso",
        "order": 3,
        "min": -1,
        "max": 1,
        "above_x_axis": True,
    }
    var_names = sv.polynomial_naming(polynomial_dict)
    assert var_names == ["poly_triso_0", "poly_triso_1", "poly_triso_2", "poly_triso_3"]
