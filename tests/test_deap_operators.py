from realm.deap_operators import DeapOperators
from deap import base, creator, tools, algorithms
import random


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
        new_pop = toolbox.select(pop, k=selection_dict["k"])
        assert "select" in dir(toolbox)
        if selection_dict["operator"] == "selBest":
            assert new_pop == expected_inds
        else:
            assert len(new_pop) == len(expected_inds)


# def test_add_mutation_operators():
#    assert "mate" in dir(toolbox)
