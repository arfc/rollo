import pytest
from realm.executor import Executor
from collections import OrderedDict

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
            "input_script": "openmc_inp.py",
            "inputs": ["packing_fraction"],
            "outputs": ["packing_fraction", "keff"],
        },
        "moltres": {
            "input_script": "moltres_inp.py",
            "inputs": ["polynomial"],
            "outputs": ["max_temp"],
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
            "poly_triso_0": "moltres",
            "poly_triso_1": "moltres",
            "poly_triso_2": "moltres",
            "poly_triso_3": "moltres",
        }
    )
    expected_output_dict = OrderedDict(
        {"packing_fraction": "openmc", "keff": "openmc", "max_temp": "moltres"}
    )
    assert ctrl_dict == expected_ctrl_dict
    assert output_dict == expected_output_dict
