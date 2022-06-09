import pytest
from rollo.constraints import Constraints
from deap import base, creator
from collections import OrderedDict

test_output_dict = OrderedDict(
    {
        "packing_fraction": "evaluator_1",
        "keff": "evaluator_1",
        "num_batches": "evaluator_1",
        "max_temp": "evaluator_2",
    }
)

test_input_constraints = {
    "keff": {"operator": [">=", "<="], "constrained_val": [1, 1.2]},
    "max_temp": {"operator": ["<"], "constrained_val": [500]},
}
toolbox = base.Toolbox()


def test_output_dict_numbered():
    c = Constraints(test_output_dict, test_input_constraints, toolbox)
    numbered_oup_dict = c.output_dict_numbered(test_output_dict)
    expected_num_oup_dict = {
        "packing_fraction": 0,
        "keff": 1,
        "num_batches": 2,
        "max_temp": 3,
    }
    assert numbered_oup_dict == expected_num_oup_dict


def test_constraints_list():
    c = Constraints(test_output_dict, test_input_constraints, toolbox)
    constraints_list = c.constraints_list(test_input_constraints)
    expected_constraints_list = [
        ["keff", {"op": ">=", "val": 1}],
        ["keff", {"op": "<=", "val": 1.2}],
        ["max_temp", {"op": "<", "val": 500}],
    ]
    assert constraints_list == expected_constraints_list


def test_apply_constraints():
    creator.create(
        "obj",
        base.Fitness,
        weights=(
            -1.0,
            1.0,
        ),
    )
    creator.create("Ind", list, fitness=creator.obj)
    ind1 = creator.Ind([1])
    ind2 = creator.Ind([2])
    ind3 = creator.Ind([3])
    ind4 = creator.Ind([4])
    ind5 = creator.Ind([5])
    ind1.output = tuple([0.1, 1.1, 1, 400])
    ind2.output = tuple([0.1, 1.1, 1, 600])
    ind3.output = tuple([0.1, 1.4, 1, 400])
    ind4.output = tuple([0.1, 0.9, 1, 400])
    ind5.output = tuple([0.1, 1.15, 2, 450])
    pop = [ind1, ind2, ind3, ind4, ind5]
    c = Constraints(test_output_dict, test_input_constraints, toolbox)
    new_pop = c.apply_constraints(pop)
    expected_pop = [ind1, ind5]
    for ind in new_pop:
        assert ind in expected_pop
    assert len(new_pop) == len(pop)
