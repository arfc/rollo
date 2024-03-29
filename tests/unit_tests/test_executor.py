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
    },
    "evaluators": {
        "evaluator_1": {
            "order": 0,
            "input_script":
                ["python", "input_test_eval_fn_generator_template.py"],
            "inputs": ["packing_fraction", "variable2"],
            "outputs": ["packing_fraction", "num_batches"],
            "output_script":
                ["python", "input_test_eval_fn_generator_output.py"],
            "keep_files": True,
        },
        "evaluator_2": {
            "order": 1,
            "input_script":
                ["python", "input_test_render_jinja_template_python.py"],
            "inputs": ["variable2"],
            "outputs": ["max_temp"],
            "output_script":
                ["python",
                 "input_test_evaluation_get_output_vals_evaluator2.py"],
            "keep_files": True,
        },
    },
    "constraints": {},
    "algorithm": {
        "objective": ["max", "min"],
        "weight": [1.0, 1.0],
        "optimized_variable": ["packing_fraction", "max_temp"],
        "pop_size": 100,
        "generations": 10,
        "parallel": "none",
        "keep_files": "none",
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
        {"packing_fraction": ["evaluator_1"],
         "variable2": ["evaluator_1", "evaluator_2"]}
    )
    expected_output_dict = OrderedDict(
        {
            "packing_fraction": "evaluator_1",
            "max_temp": "evaluator_2",
            "num_batches": "evaluator_1",
        }
    )
    assert ctrl_dict == expected_ctrl_dict
    assert output_dict == expected_output_dict


def test_load_evaluator():
    os.chdir("./input_test_files")
    if os.path.exists("./0_0"):
        shutil.rmtree("./0_0")
    e = Executor("input_file_placeholder")
    test_control_dict, test_output_dict = e.organize_input_output(
        test_input_dict)
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
    ind = creator.Ind([0.03, 1])
    ind.gen = 0
    ind.num = 0
    output_vals = eval_function(ind)
    expected_output_vals = tuple([0.03, 1000, 10])

    os.chdir("../")
    assert output_vals == expected_output_vals


def test_load_toolbox():
    e = Executor("input_file_placeholder")
    ctrl_dict = OrderedDict(
        {"packing_fraction": ["evaluator_1", 1]}
    )
    output_dict = OrderedDict(
        {
            "packing_fraction": "evaluator_1",
            "max_temp": "evaluator_2",
            "keff": "evaluator_1",
            "num_batches": "evaluator_1",
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
    assert isinstance(test_toolbox_ind, creator.Ind)
    test_toolbox_pop = toolbox.population(n=10)
    assert isinstance(test_toolbox_pop, list)
    test_toolbox_eval = toolbox.evaluate()
    assert test_toolbox_eval == tuple([1, 1])
    assert toolbox.pop_size == 100
    assert toolbox.ngen == 10
    assert toolbox.mutpb == 0.5
    assert toolbox.cxpb == 0.5


def test_load_constraints():
    output_dict = OrderedDict(
        {
            "packing_fraction": "evaluator_1",
            "keff": "evaluator_1",
            "num_batches": "evaluator_1",
            "max_temp": "evaluator_2",
        }
    )
    e = Executor("input_file_placeholder")
    constraint_obj = e.load_constraints(
        output_dict, test_input_dict["constraints"], base.Toolbox()
    )
    assert isinstance(constraint_obj, Constraints)
