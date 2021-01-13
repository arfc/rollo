from realm.algorithm import Algorithm
from realm.constraints import Constraints
from deap import base, creator, tools, algorithms
import random

creator.create("obj", base.Fitness, weights=(1.0,))
creator.create("Ind", list, fitness=creator.obj)
toolbox = base.Toolbox()
toolbox.register("pf", random.uniform, 0, 1)
toolbox.register("poly", random.uniform, 1, 2)
toolbox.pop_size = 300
toolbox.min_list = [0.0, 1.0, 1.0]
toolbox.max_list = [1.0, 2.0, 3.0]


def ind_vals():
    pf = toolbox.pf()
    poly = toolbox.poly()
    return creator.Ind([pf, poly, pf + poly])


toolbox.register("individual", ind_vals)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
k = 100
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


def evaluator_fn(ind):
    return tuple([ind[0] + ind[1], 5])


toolbox.register("evaluate", evaluator_fn)
test_constraints = Constraints(output_dict={}, input_constraints={})


def test_initialize_pop():
    a = Algorithm(deap_toolbox=toolbox, constraint_obj=test_constraints)
    pop = toolbox.population(n=5)
    pop = a.initialize_pop(pop)
    for i, ind in enumerate(pop):
        assert ind.fitness.values[0] < 3
        assert ind.fitness.values[0] > 1
        assert ind.output[1] == 5
        assert type(ind) is creator.Ind
        assert ind[0] < 1
        assert ind[0] > 0
        assert ind[1] > 1
        assert ind[1] < 2
        assert ind.num == i
        assert ind.gen == 0


def test_apply_selection_operator():
    a = Algorithm(deap_toolbox=toolbox, constraint_obj=test_constraints)
    pop = toolbox.population(n=toolbox.pop_size)
    pop = a.initialize_pop(pop)
    cloned_pop = [toolbox.clone(ind) for ind in pop]
    selected_pop = a.apply_selection_operator(cloned_pop, toolbox)
    expected_inds = [toolbox.clone(ind) for ind in pop]
    expected_inds.sort(key=lambda x: x[2])
    expected_inds = expected_inds[k:]
    for s in selected_pop:
        assert s in expected_inds


def test_apply_mating_operator():
    a = Algorithm(deap_toolbox=toolbox, constraint_obj=test_constraints)
    pop = toolbox.population(n=4)
    mated_pop = [toolbox.clone(ind) for ind in pop]
    mated_pop = a.apply_mating_operator(mated_pop, toolbox)
    for i in range(len(pop)):
        if i % 2 == 0:
            assert pop[i] == mated_pop[i + 1]


def test_apply_mutation_operator():
    a = Algorithm(deap_toolbox=toolbox, constraint_obj=test_constraints)
    pop = toolbox.population(n=1)
    mutated_pop = [toolbox.clone(ind) for ind in pop]
    mutated_pop = a.apply_mutation_operator(mutated_pop, toolbox)
    for mutant in mutated_pop:
        for i, val in enumerate(mutant):
            assert val > toolbox.min_list[i]
            assert val < toolbox.max_list[i]
