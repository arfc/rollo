from rollo.algorithm import Algorithm
from rollo.constraints import Constraints
from deap import base, creator, tools
import random
import os
from collections import OrderedDict


def init():
    creator.create(
        "obj",
        base.Fitness,
        weights=(
            1.0,
            -1.0,
        ),
    )
    creator.create("Ind", list, fitness=creator.obj)
    toolbox = base.Toolbox()
    toolbox.register("pf", random.uniform, 0, 1)
    toolbox.register("poly", random.uniform, 1, 2)
    toolbox.pop_size = 10
    toolbox.ngen = 10
    toolbox.min_list = [0.0, 1.0, 1.0]
    toolbox.max_list = [1.0, 2.0, 3.0]

    def ind_vals():
        pf = toolbox.pf()
        poly = toolbox.poly()
        return creator.Ind([pf, poly, pf + poly])

    toolbox.register("individual", ind_vals)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    k = 5
    toolbox.register("select", tools.selBest, k=k)
    toolbox.register("mate", tools.cxUniform, indpb=1.0)
    toolbox.register(
        "mutate",
        tools.mutPolynomialBounded,
        eta=0.5,
        indpb=1.0,
        low=[0.0, 1.0, 1.0],
        up=[1.0, 2.0, 3.0],
    )
    toolbox.cxpb = 1.0
    toolbox.mutpb = 1.0
    toolbox.objs = 2

    def evaluator_fn(ind):
        return tuple([ind[0] + ind[1], 5])

    toolbox.register("evaluate", evaluator_fn)

    test_constraints = Constraints(
        output_dict=OrderedDict({"total": "evaluator_1", "random": "evaluator_1"}),
        input_constraints={
            "total": {"operator": [">", "<"], "constrained_val": [1.5, 2.5]}
        },
        toolbox=toolbox,
    )
    return toolbox, test_constraints


control_dict = OrderedDict(
    {"packing_fraction": ["evaluator_1", 1], "polynomial_triso": ["evaluator_1", 4]}
)
output_dict = OrderedDict(
    {
        "packing_fraction": "evaluator_1",
        "keff": "evaluator_1",
        "num_batches": "evaluator_1",
        "max_temp": "evaluator_2",
    }
)


def test_generate():
    toolbox, test_constraints = init()
    a = Algorithm(
        deap_toolbox=toolbox,
        constraint_obj=test_constraints,
        checkpoint_file=None,
        deap_creator=creator,
        control_dict=control_dict,
        output_dict=output_dict,
        input_dict={},
        start_time=0,
        parallel_method="none",
    )
    final_pop = a.generate()
    assert len(final_pop) == toolbox.pop_size
    for ind in final_pop:
        for i, val in enumerate(ind):
            assert val > toolbox.min_list[i]
            assert val < toolbox.max_list[i]
        assert ind.fitness.values[0] > 1.5
        assert ind.fitness.values[0] < 2.5
    assert len(final_pop) == toolbox.pop_size
    assert len(a.backend.results["logbook"]) == toolbox.pop_size
    os.remove("checkpoint.pkl")


def test_initialize_pop():
    toolbox, test_constraints = init()
    a = Algorithm(
        deap_toolbox=toolbox,
        constraint_obj=test_constraints,
        checkpoint_file=None,
        deap_creator=creator,
        control_dict=control_dict,
        output_dict=output_dict,
        input_dict={},
        start_time=0,
        parallel_method="none",
    )
    a.backend.initialize_new_backend()
    pop = toolbox.population(n=5)
    new_pop = a.initialize_pop(pop)
    assert len(new_pop) == len(pop)
    for i, ind in enumerate(new_pop):
        assert ind.fitness.values[0] < 3
        assert ind.fitness.values[0] > 1
        assert ind.output[1] == 5
        assert isinstance(ind, creator.Ind)
        assert ind[0] < 1
        assert ind[0] > 0
        assert ind[1] > 1
        assert ind[1] < 2
        assert ind.gen == 0
        assert ind.fitness.values[0] > 1.5
        assert ind.fitness.values[0] < 2.5
    os.remove("checkpoint.pkl")


def test_apply_algorithm_ngen():
    toolbox, test_constraints = init()
    a = Algorithm(
        deap_toolbox=toolbox,
        constraint_obj=test_constraints,
        checkpoint_file=None,
        deap_creator=creator,
        control_dict=control_dict,
        output_dict=output_dict,
        input_dict={},
        start_time=0,
        parallel_method="none",
    )
    pop = toolbox.population(n=10)
    a.backend.initialize_new_backend()
    new_pop = [toolbox.clone(ind) for ind in pop]
    new_pop = a.initialize_pop(new_pop)
    new_pop = a.apply_algorithm_ngen(new_pop, 0)

    for ind in new_pop:
        for i, val in enumerate(ind):
            assert val > toolbox.min_list[i]
            assert val < toolbox.max_list[i]
        assert ind.fitness.values[0] > 1.5
        assert ind.fitness.values[0] < 2.5
    assert len(new_pop) == toolbox.pop_size
    assert new_pop != pop
    os.remove("checkpoint.pkl")


def test_apply_selection_operator():
    toolbox, test_constraints = init()
    a = Algorithm(
        deap_toolbox=toolbox,
        constraint_obj=test_constraints,
        checkpoint_file=None,
        deap_creator=creator,
        control_dict=control_dict,
        output_dict=output_dict,
        input_dict={},
        start_time=0,
        parallel_method="none",
    )
    a.backend.initialize_new_backend()
    pop = toolbox.population(n=toolbox.pop_size)
    pop = a.initialize_pop(pop)
    cloned_pop = [toolbox.clone(ind) for ind in pop]
    selected_pop = a.apply_selection_operator(cloned_pop)
    for s in selected_pop:
        assert s in cloned_pop
    os.remove("checkpoint.pkl")


def test_apply_mating_operator():
    toolbox, test_constraints = init()
    a = Algorithm(
        deap_toolbox=toolbox,
        constraint_obj=test_constraints,
        checkpoint_file=None,
        deap_creator=creator,
        control_dict=control_dict,
        output_dict=output_dict,
        input_dict={},
        start_time=0,
        parallel_method="none",
    )
    pop = toolbox.population(n=toolbox.pop_size)
    mated_pop = [toolbox.clone(ind) for ind in pop]
    mated_pop = a.apply_mating_operator(mated_pop)
    for i in range(len(pop)):
        if i % 2 == 0:
            assert pop[i] == mated_pop[i + 1]


def test_apply_mutation_operator():
    toolbox, test_constraints = init()
    a = Algorithm(
        deap_toolbox=toolbox,
        constraint_obj=test_constraints,
        checkpoint_file=None,
        deap_creator=creator,
        control_dict=control_dict,
        output_dict=output_dict,
        input_dict={},
        start_time=0,
        parallel_method="none",
    )
    pop = toolbox.population(n=toolbox.pop_size)
    mutated_pop = [toolbox.clone(ind) for ind in pop]
    mutated_pop = a.apply_mutation_operator(mutated_pop)
    for j, mutant in enumerate(mutated_pop):
        for i, val in enumerate(mutant):
            assert val > toolbox.min_list[i]
            assert val < toolbox.max_list[i]
        assert mutant != pop[j]
