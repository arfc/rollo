from realm.algorithm import Algorithm
from realm.constraints import Constraints
from deap import base, creator, tools, algorithms
import random

creator.create("obj", base.Fitness, weights=(-1.0,))
creator.create("Ind", list, fitness=creator.obj)
toolbox = base.Toolbox()
toolbox.register("pf", random.uniform, 0, 1)
toolbox.register("poly", random.uniform, 1, 2)


def ind_vals():
    return creator.Ind([toolbox.pf(), toolbox.poly()])


toolbox.register("individual", ind_vals)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


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


def test_apply_algorithm_ngen():


# def test_generate():
#    a = Algorithm(deap_toolbox=test_toolbox, constraint_obj=test_constraints)
