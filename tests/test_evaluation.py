import pytest
import os, shutil
from realm.evaluation import Evaluation
from collections import OrderedDict
from deap import base, creator, tools, algorithms


def test_eval_fn_generator():
    os.chdir("./input_test_files")
    if os.path.exists("./openmc_0_0"):
        shutil.rmtree("./openmc_0_0")
    if os.path.exists("./moltres_0_0"):
        shutil.rmtree("./moltres_0_0")
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc",
        input_script="input_test_eval_fn_generator_openmc_template.py",
        output_script="input_test_eval_fn_generator_openmc_output.py",
    )
    ev.add_evaluator(
        solver_name="moltres",
        input_script="./input_test_render_jinja_template_python.py",
        output_script="input_test_evaluation_get_output_vals_moltres.py",
    )
    eval_function = ev.eval_fn_generator(
        control_dict=OrderedDict(
            {
                "packing_fraction": "openmc",
                "poly_triso_0": "openmc",
                "poly_triso_1": "openmc",
                "poly_triso_2": "openmc",
                "poly_triso_3": "openmc",
            }
        ),
        output_dict=OrderedDict(
            {
                "packing_fraction": "openmc",
                "keff": "openmc",
                "max_temp": "moltres",
                "num_batches": "openmc",
            }
        ),
        input_evaluators={"openmc": {}, "moltres": {}},
    )

    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    ind = creator.Ind([0.03, 1, 1, 1, 1])
    ind.gen = 0
    ind.num = 0
    output_vals = eval_function(ind)
    expected_output_vals = tuple([0.03, output_vals[1], 1000, 10])
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./moltres_0_0")
    os.chdir("../")
    assert output_vals == expected_output_vals


def test_get_output_vals():
    os.chdir("./input_test_files")
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc",
        input_script="placeholder.py",
        output_script="input_test_evaluation_get_output_vals.py",
    )
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
        path="./test_evaluation/",
    )
    expected_output_vals = [0.03, 1.6331797843041689, None, 3]
    os.remove("./test_evaluation/openmc_output.py")
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
        script="./input_test_render_jinja_template_python.py",
        control_vars_solver={
            "packing_fraction": 0.01,
            "poly_triso_0": 1,
            "poly_triso_1": 1,
            "poly_triso_2": 1,
            "poly_triso_3": 1,
        },
    )

    expected_rendered_template = "total_pf = 0.01\npoly_coeff = [1, 1, 1, 1]"
    os.chdir("../")
    assert rendered_template == expected_rendered_template
