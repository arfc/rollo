from rollo.toolbox_generator import ToolboxGenerator
from deap import base, creator, tools
import random
import copy
from collections import OrderedDict


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
            "input_script": "input_test_eval_fn_generator_openmc_template.py",
            "inputs": ["packing_fraction", "polynomial_triso"],
            "outputs": ["packing_fraction", "keff", "num_batches"],
            "output_script": "input_test_eval_fn_generator_openmc_output.py",
        },
        "moltres": {
            "order": 1,
            "input_script": "input_test_render_jinja_template_python.py",
            "inputs": [],
            "outputs": ["max_temp"],
            "output_script": "input_test_evaluation_get_output_vals_moltres.py",
        },
    },
    "constraints": {"keff": {"operator": ">", "constrained_val": 1}},
    "algorithm": {
        "objective": ["max", "min"],
        "weight": [1.0, 1.0],
        "optimized_variable": ["keff", "packing_fraction"],
        "pop_size": 100,
        "generations": 10,
        "mutation_probability": 0.5,
        "mating_probability": 0.5,
        "selection_operator": {"operator": "selBest"},
        "mutation_operator": {
            "operator": "mutGaussian",
            "indpb": 0.5,
            "mu": 0.5,
            "sigma": 0.5,
        },
        "mating_operator": {"operator": "cxOnePoint"},
    },
}


def test_setup():
    tg = ToolboxGenerator()
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

    toolbox, creator = tg.setup(
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
    assert toolbox.objs == 2


def test_individual_values():
    tg = ToolboxGenerator()
    ctrl_dict = OrderedDict(
        {"packing_fraction": ["openmc", 1]}
    )
    toolbox = base.Toolbox()
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    toolbox.register("packing_fraction", random.uniform, 0.005, 0.1)
    ind_values = tg.individual_values(
        test_input_dict["control_variables"], ctrl_dict, toolbox
    )
    assert isinstance(ind_values, creator.Ind)
    assert ind_values[0] >= 0.005
    assert ind_values[0] <= 0.1


def test_min_max_list():
    tg = ToolboxGenerator()
    ctrl_dict = OrderedDict(
        {"packing_fraction": ["openmc", 1], "polynomial_triso": ["openmc", 4]}
    )
    min_list, max_list = tg.min_max_list(
        ctrl_dict, test_input_dict["control_variables"]
    )
    expected_min_list = [0.005, 1, 1, 1, 1]
    expected_max_list = [0.1, 1, 1, 1, 1]


def test_add_selection_operators():
    tg = ToolboxGenerator()
    selection_dict_list = [
        {"operator": "selTournament", "tournsize": 2},
        {"operator": "selNSGA2"},
        {"operator": "selBest"},
    ]
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)

    def f_cycle():
        return creator.Ind([toolbox.num()])

    for i in range(100):
        for selection_dict in selection_dict_list:
            toolbox = base.Toolbox()
            toolbox.register("num", random.uniform, -1, 1)
            toolbox.register("individual", f_cycle)
            toolbox.register(
                "population",
                tools.initRepeat,
                list,
                toolbox.individual)
            pop = toolbox.population(n=10)
            toolbox = tg.add_selection_operators(toolbox, selection_dict)
            new_pop = toolbox.select(pop, k=len(pop))
            assert "select" in dir(toolbox)
            if selection_dict["operator"] == "selBest":
                assert new_pop == pop
            else:
                assert len(new_pop) == len(pop)


def test_add_mutation_operators():
    tg = ToolboxGenerator()
    toolbox = base.Toolbox()
    mutation_dict_list = [
        {"operator": "mutPolynomialBounded", "eta": 0.5, "indpb": 0.5},
    ]
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    min_list = [0.005, 0.1, 0.1, 0.1, 0.1]
    max_list = [0.1, 1, 1, 1, 1]

    for j in range(100):
        for mutation_dict in mutation_dict_list:
            ind = creator.Ind([0.05, 0.9, 0.9, 0.8, 0.7])
            toolbox = tg.add_mutation_operators(
                toolbox, mutation_dict, min_list, max_list
            )
            mutated = toolbox.mutate(ind)
            assert "mutate" in dir(toolbox)
            assert mutated != ind


def test_add_mating_operators():
    tg = ToolboxGenerator()
    toolbox = base.Toolbox()
    mating_dict_list = [
        {"operator": "cxOnePoint"},
        {"operator": "cxUniform", "indpb": 0.5},
        {"operator": "cxBlend", "alpha": 0.5},
    ]
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    toolbox.register("num", random.uniform, -1, 1)

    def f_cycle():
        return creator.Ind([toolbox.num(), toolbox.num(),
                           toolbox.num(), toolbox.num()])

    toolbox.register("individual", f_cycle)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    starting_pop = toolbox.population(n=2)
    pop = copy.deepcopy(starting_pop)
    for i in range(100):
        for mating_dict in mating_dict_list:
            new_pop = []
            for child1, child2 in zip(pop[::2], pop[1::2]):
                toolbox = tg.add_mating_operators(toolbox, mating_dict)
                new_pop += toolbox.mate(child1, child2)
            assert "mate" in dir(toolbox)
            assert len(new_pop) == len(pop)
