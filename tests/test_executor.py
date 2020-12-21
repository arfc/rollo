import pytest, os, shutil
from realm.executor import Executor
from collections import OrderedDict
from deap import base, creator, tools, algorithms

test_input_dict = {
    "control_variables": {
        "packing_fraction": {"min": 0.005, "max": 0.1},
        "polynomial": {
            "name": "triso",
            "order": 3,
            "min": -1,
            "max": 1,
            "above_x_axis": True,
        },
    },
    "evaluators": {
        "openmc": {
            "input_script": "input_test_eval_fn_generator_openmc_template.py",
            "inputs": ["packing_fraction", "polynomial"],
            "outputs": ["packing_fraction", "keff", "num_batches"],
            "output_script": "input_test_eval_fn_generator_openmc_output.py",
        },
        "moltres": {
            "input_script": "input_test_render_jinja_template_python.py",
            "inputs": [],
            "outputs": ["max_temp"],
            "output_script": "input_test_evaluation_get_output_vals_moltres.py",
        },
    },
    "constraints": {"keff": {"operator": ">", "constrained_val": 1}},
    "algorithm": {
        "objective": "min",
        "optimized_variable": "packing_fraction",
        "pop_size": 100,
        "generations": 10,
        "selection_operator": {"operator": "selBest", "k": 1},
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
        {
            "packing_fraction": "openmc",
            "poly_triso_0": "openmc",
            "poly_triso_1": "openmc",
            "poly_triso_2": "openmc",
            "poly_triso_3": "openmc",
        }
    )
    expected_output_dict = OrderedDict(
        {
            "packing_fraction": "openmc",
            "keff": "openmc",
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
    print("test control", test_control_dict)
    print("test output", test_output_dict)
    eval_function = e.load_evaluator(
        control_dict=test_control_dict,
        output_dict=test_output_dict,
        input_dict=test_input_dict,
    )
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    ind = creator.Ind([0.03, 1, 1, 1, 1])
    ind.gen = 0
    ind.num = 0
    output_vals = eval_function(ind)
    expected_output_vals = tuple([0.03, output_vals[1], 10, 1000])
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./moltres_0_0")
    os.chdir("../")
    assert output_vals == expected_output_vals
