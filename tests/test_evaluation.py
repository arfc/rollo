import pytest
from realm.evaluation2 import Evaluation


def test_render_jinja_template_python():
    ev = Evaluation()
    rendered_template = ev.render_jinja_template_python(
        "./input_test_files/input_test_render_jinja_template_python.py",
        {"packing_fraction": 0.01, "polynomial": [1, 1, 1, 1]},
    )

    expected_rendered_template = "total_pf = 0.01\npoly_coeff = [1, 1, 1, 1]"

    assert rendered_template == expected_rendered_template
