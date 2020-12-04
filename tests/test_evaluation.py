import pytest
from realm.evaluation2 import Evaluation
from collections import OrderedDict


def test_name_ind():
    ev = Evaluation()
    control_vars = ev.name_ind(
        ind=[0.01, 1, 1, 1, 1],
        control_dict=OrderedDict(
            {
                "packing_fraction": "openmc",
                "poly_triso_0": "moltres",
                "poly_triso_1": "moltres",
                "poly_triso_2": "moltres",
                "poly_triso_3": "moltres",
            }
        ),
        input_evaluators=["openmc", "moltres"],
    )
    expected_control_vars = {
        "openmc": {"packing_fraction": 0.01},
        "moltres": {
            "poly_triso_0": 1,
            "poly_triso_1": 1,
            "poly_triso_2": 1,
            "poly_triso_3": 1,
        },
    }
    assert control_vars == expected_control_vars


def test_render_jinja_template_python():
    ev = Evaluation()
    rendered_template = ev.render_jinja_template_python(
        "./input_test_files/input_test_render_jinja_template_python.py",
        {"packing_fraction": 0.01, "polynomial": [1, 1, 1, 1]},
    )

    expected_rendered_template = "total_pf = 0.01\npoly_coeff = [1, 1, 1, 1]"

    assert rendered_template == expected_rendered_template
