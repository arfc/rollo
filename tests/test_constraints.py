import pytest
from realm.constraints import Constraints
from deap import base, creator, tools, algorithms
from collections import OrderedDict

test_output_dict = OrderedDict(
    {
        "packing_fraction": "openmc",
        "keff": "openmc",
        "num_batches": "openmc",
        "max_temp": "moltres",
    }
)

test_input_constraints = {
    "keff": {"operator": ">=", "constrained_val": 1},
    "max_temp": {"operator": "<", "constrained_val": 500},
    "keff": {"operator": "<=", "constrained_val": 1.2},
}


def test_output_dict_numbered():
    c = Constraints(test_output_dict, test_input_constraints)
    numbered_oup_dict = c.output_dict_numbered(test_output_dict)
    expected_num_oup_dict = {
        "packing_fraction": 0,
        "keff": 1,
        "num_batches": 2,
        "max_temp": 3,
    }
    assert numbered_oup_dict == expected_num_oup_dict
