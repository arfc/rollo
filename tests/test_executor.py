import pytest, os, shutil, random
from realm.executor import Executor
from collections import OrderedDict
from deap import base, creator, tools, algorithms
from realm.special_variables import SpecialVariables

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
            "input_script": "input_test_eval_fn_generator_openmc_template.py",
            "inputs": ["packing_fraction", "polynomial_triso"],
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
        {"packing_fraction": ["openmc", 1], "polynomial_triso": ["openmc", 4]}
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


# def test_load_toolbox():


def test_min_max_list():
    e = Executor("input_file_placeholder")
    ctrl_dict = OrderedDict(
        {"packing_fraction": ["openmc", 1], "polynomial_triso": ["openmc", 4]}
    )
    min_list, max_list = e.min_max_list(ctrl_dict, test_input_dict["control_variables"])
    expected_min_list = [0.005, 1, 1, 1, 1]
    expected_max_list = [0.1, 1, 1, 1, 1]


def test_individual_values():
    e = Executor("input_file_placeholder")
    ctrl_dict = OrderedDict(
        {"packing_fraction": ["openmc", 1], "polynomial_triso": ["openmc", 4]}
    )
    poly_dict = test_input_dict["control_variables"]["polynomial_triso"]
    toolbox = base.Toolbox()
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    toolbox.register("packing_fraction", random.uniform, 0.005, 0.1)
    sv = SpecialVariables()
    toolbox = sv.polynomial_triso_toolbox(poly_dict, toolbox)
    ind_values = e.individual_values(
        test_input_dict["control_variables"], ctrl_dict, toolbox
    )
    assert type(ind_values) is creator.Ind
    assert ind_values[0] >= 0.005
    assert ind_values[0] <= 0.1
    for i in range(1, 4):
        ind_values[i] >= -1
        ind_values[i] <= 1
