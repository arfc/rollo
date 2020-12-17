import pytest
import os
from realm.evaluation2 import Evaluation
from collections import OrderedDict


def test_get_output_vals():
    os.chdir("./input_test_files")
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc",
        input_script="placeholder.py",
        output_script="input_test_evaluation_get_output_vals.py",
    )
    print(ev.output_scripts)
    output_vals = ev.get_output_vals(
        output_vals=[None] * 4,
        solver="openmc",
        output_dict=OrderedDict(
            {
                "packing_fraction": "openmc",
                "keff": "openmc",
                "max_temp": "moltres",
                "random": "openmc",
            }
        ),
        control_vars={
            "openmc": {"packing_fraction": 0.03},
            "moltres": {
                "poly_triso_0": 1,
                "poly_triso_1": 1,
                "poly_triso_2": 1,
                "poly_triso_3": 1,
            },
        },
    )
    expected_output_vals = [0.03, 1.6331797843041689, None, 3]
    os.chdir("../")
    assert output_vals == expected_output_vals


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
    os.chdir("./input_test_files")
    ev = Evaluation()
    rendered_template = ev.render_jinja_template_python(
        "./input_test_render_jinja_template_python.py",
        {"packing_fraction": 0.01, "polynomial": [1, 1, 1, 1]},
    )

    expected_rendered_template = "total_pf = 0.01\npoly_coeff = [1, 1, 1, 1]"
    os.chdir("../")
    assert rendered_template == expected_rendered_template
