from realm.deap_operators import DeapOperators
from deap import base, creator, tools, algorithms
import random, copy


def test_add_selection_operators():
    do = DeapOperators()
    toolbox = base.Toolbox()
    selection_dict_list = [
        {"operator": "selTournament", "k": 5, "tournsize": 2},
        {"operator": "selNSGA2", "k": 5},
        {"operator": "selBest", "k": 5},
        {"operator": "selLexicase", "k": 5},
    ]
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    toolbox.register("num", random.uniform, -1, 1)

    def f_cycle():
        return creator.Ind([toolbox.num()])

    toolbox.register("individual", f_cycle)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(n=10)
    for selection_dict in selection_dict_list:
        toolbox = do.add_selection_operators(toolbox, selection_dict)
        expected_inds = []
        for i, ind in enumerate(pop):
            if (i % 2) == 0:
                ind.fitness.values = (1,)
            else:
                ind.fitness.values = (0,)
                expected_inds.append(ind)
        new_pop = toolbox.select(pop)
        assert "select" in dir(toolbox)
        if selection_dict["operator"] == "selBest":
            assert new_pop == expected_inds
        else:
            assert len(new_pop) == len(expected_inds)


def test_add_mutation_operators():
    do = DeapOperators()
    toolbox = base.Toolbox()
    mutation_dict_list = [
        {"operator": "mutGaussian", "indpb": 0.5, "mu": 0.5, "sigma": 0.5},
        {"operator": "mutPolynomialBounded", "eta": 0.5, "indpb": 0.5},
    ]
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    ind = creator.Ind([1])
    min_list = [0.005, 1, 1, 1, 1]
    max_list = [0.1, 1, 1, 1, 1]

    for mutation_dict in mutation_dict_list:
        toolbox = do.add_mutation_operators(toolbox, mutation_dict, min_list, max_list)
        mutated = toolbox.mutate(ind)
        assert "mutate" in dir(toolbox)
        assert mutated != ind


def test_add_mating_operators():
    do = DeapOperators()
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
        return creator.Ind([toolbox.num(), toolbox.num(), toolbox.num(), toolbox.num()])

    toolbox.register("individual", f_cycle)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    starting_pop = toolbox.population(n=2)
    pop = copy.deepcopy(starting_pop)
    for mating_dict in mating_dict_list:
        new_pop = []
        for child1, child2 in zip(pop[::2], pop[1::2]):
            toolbox = do.add_mating_operators(toolbox, mating_dict)
            new_pop += toolbox.mate(child1, child2)
        assert "mate" in dir(toolbox)
        assert len(new_pop) == len(pop)
