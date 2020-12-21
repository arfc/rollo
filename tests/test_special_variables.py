import pytest, random
from realm.special_variables import SpecialVariables
from deap import base, creator, tools, algorithms

poly_dict = {
    "name": "triso",
    "order": 3,
    "min": 1,
    "max": 1,
    "above_x_axis": True,
}


def test_polynomial_naming():
    sv = SpecialVariables()
    var_names = sv.polynomial_naming(poly_dict)
    assert var_names == ["poly_triso_0", "poly_triso_1", "poly_triso_2", "poly_triso_3"]


def test_polynomial_toolbox():
    expected_toolbox = base.Toolbox()
    expected_toolbox.register("poly_triso_0", random.uniform, 1, 1)
    expected_toolbox.register("poly_triso_1", random.uniform, 1, 1)
    expected_toolbox.register("poly_triso_2", random.uniform, 1, 1)
    expected_toolbox.register("poly_triso_3", random.uniform, 1, 1)

    toolbox = base.Toolbox()
    sv = SpecialVariables()
    toolbox = sv.polynomial_toolbox(poly_dict, toolbox)

    for i in range(4):
        method = getattr(toolbox, "poly_triso_" + str(i))
        expected_method = getattr(expected_toolbox, "poly_triso_" + str(i))
        assert method() == expected_method()
