import pytest
import os
import shutil
from rollo.executor import Executor
from collections import OrderedDict
from deap import base, creator
from rollo.constraints import Constraints

test_input_dict = {
    "control_variables": {
        "packing_fraction": {"min": 0.005, "max": 0.1},
        "polynomial_triso": {
            "order": 3,
            "min": 1,
            "max": 1,
            "radius": 4235e-5,
            "volume": 10,
            "slices": 10,
            "height": 10,
        },
    },
    "evaluators": {
        "openmc": {
            "order": 0,
            "input_script": ["python", "input_test_eval_fn_generator_openmc_template.py"],
            "execute2": [],
            "inputs": ["packing_fraction", "polynomial_triso"],
            "outputs": ["packing_fraction", "keff", "num_batches"],
            "output_script": ["python", "input_test_eval_fn_generator_openmc_output.py"],
            "keep_files": True,
        },
        "moltres": {
            "order": 1,
            "input_script": ["python", "input_test_render_jinja_template_python.py"],
            "execute2": [],
            "inputs": [],
            "outputs": ["max_temp"],
            "output_script": ["python", "input_test_evaluation_get_output_vals_moltres.py"],
            "keep_files": True,
        },
    },
    "constraints": {"keff": {"operator": [">"], "constrained_val": [1]}},
    "algorithm": {
        "objective": ["max", "min"],
        "optimized_variable": ["keff", "packing_fraction"],
        "pop_size": 100,
        "generations": 10,
        "mutation_probability": 0.5,
        "mating_probability": 0.5,
        "selection_operator": {"operator": "selBest", "inds": 1},
        "mutation_operator": {
            "operator": "mutGaussian",
            "indpb": 0.5,
            "mu": 0.5,
            "sigma": 0.5,
        },
        "mating_operator": {"operator": "cxOnePoint"},
    },
}


def test_organize_input_output():
    e = Executor("input_file_placeholder")
    ctrl_dict, output_dict = e.organize_input_output(test_input_dict)
    expected_ctrl_dict = OrderedDict(
        {"packing_fraction": ["openmc", 1], "polynomial_triso": ["openmc", 4]}
    )
    expected_output_dict = OrderedDict(
        {
            "keff": "openmc",
            "packing_fraction": "openmc",
            "num_batches": "openmc",
            "max_temp": "moltres",
        }
    )
    assert ctrl_dict == expected_ctrl_dict
    assert output_dict == expected_output_dict


def test_load_evaluator():
    os.chdir("./input_test_files")
    if os.path.exists("./openmc_0_0"):
        shutil.rmtree("./openmc_0_0")
    if os.path.exists("./moltres_0_0"):
        shutil.rmtree("./moltres_0_0")
    e = Executor("input_file_placeholder")
    test_control_dict, test_output_dict = e.organize_input_output(test_input_dict)
    eval_function = e.load_evaluator(
        control_dict=test_control_dict,
        output_dict=test_output_dict,
        input_dict=test_input_dict,
    )
    creator.create(
        "obj",
        base.Fitness,
        weights=(
            1.0,
            -1.0,
        ),
    )
    creator.create("Ind", list, fitness=creator.obj)
    ind = creator.Ind([0.03, 1, 1, 1, 1])
    ind.gen = 0
    ind.num = 0
    output_vals = eval_function(ind)
    expected_output_vals = tuple([output_vals[0], 0.03, 10, 1000])
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./moltres_0_0")
    os.chdir("../")
    assert output_vals == expected_output_vals


def test_load_toolbox():
    e = Executor("input_file_placeholder")
    ctrl_dict = OrderedDict(
        {"packing_fraction": ["openmc", 1], "polynomial_triso": ["openmc", 4]}
    )
    output_dict = OrderedDict(
        {
            "packing_fraction": "openmc",
            "keff": "openmc",
            "num_batches": "openmc",
            "max_temp": "moltres",
        }
    )

    def test_evaluator_fn():
        return tuple([1, 1])

    toolbox, creator = e.load_toolbox(
        evaluator_fn=test_evaluator_fn,
        input_algorithm=test_input_dict["algorithm"],
        input_ctrl_vars=test_input_dict["control_variables"],
        control_dict=ctrl_dict,
    )

    test_toolbox_ind = toolbox.individual()
    assert type(test_toolbox_ind) == creator.Ind
    test_toolbox_pop = toolbox.population(n=10)
    assert type(test_toolbox_pop) == list
    test_toolbox_eval = toolbox.evaluate()
    assert test_toolbox_eval == tuple([1, 1])
    assert toolbox.pop_size == 100
    assert toolbox.ngen == 10
    assert toolbox.mutpb == 0.5
    assert toolbox.cxpb == 0.5


def test_load_constraints():
    output_dict = OrderedDict(
        {
            "packing_fraction": "openmc",
            "keff": "openmc",
            "num_batches": "openmc",
            "max_temp": "moltres",
        }
    )
    e = Executor("input_file_placeholder")
    constraint_obj = e.load_constraints(
        output_dict, test_input_dict["constraints"], base.Toolbox()
    )
    assert type(constraint_obj) == Constraints
