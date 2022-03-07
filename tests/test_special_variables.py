import pytest
import numpy as np
from rollo.special_variables import SpecialVariables

poly_dict = {
    "name": "triso",
    "order": 3,
    "min": 1,
    "max": 1,
    "radius": 4235e-5,
    "volume": 10,
    "slices": 10,
    "height": 10,
}


def test_polynomial_triso_num():
    sv = SpecialVariables()
    assert sv.polynomial_triso_num(poly_dict) == 4


def test_polynomial_triso_values():
    poly_dict = {
        "name": "triso",
        "order": 3,
        "min": -1,
        "max": 1,
        "radius": 4235e-5,
        "volume": 10,
        "slices": 10,
        "height": 10,
    }

    var_dict = {"packing_fraction": 0.1}
    sv = SpecialVariables()
    dz_vals = np.linspace(0, poly_dict["height"], poly_dict["slices"])
    vol_triso = 4 / 3 * np.pi * poly_dict["radius"] ** 3
    no_trisos = var_dict["packing_fraction"] * poly_dict["volume"] / vol_triso
    for i in range(100):
        poly = sv.polynomial_triso_values(poly_dict, var_dict)
        poly_val = (
            poly[0] * dz_vals ** 3 +
            poly[1] * dz_vals ** 2 +
            poly[2] * dz_vals +
            poly[3]
        )
        pf_z = poly_val / sum(poly_val) * no_trisos * \
            vol_triso / poly_dict["volume"]
        assert len([i for i in pf_z if i > 0.25]) == 0
        assert len([i for i in poly_val if i < 0]) == 0
