from realm.backend import BackEnd
from deap import base, creator, tools, algorithms

creator.create("obj", base.Fitness, weights=(1.0,))
creator.create("Ind", list, fitness=creator.obj)


def test_initialize_new_backend():
    b = BackEnd("square_checkpoint.pkl", creator)
    b.initialize_new_backend()
    assert b.backend["start_gen"] == 0
    assert type(b.backend["halloffame"]) == tools.HallOfFame
    assert type(b.backend["logbook"]) == tools.Logbook


def test_initialize_checkpoint_backend():
    b = BackEnd("input_test_files/test_checkpoint.pkl", creator)
    b.initialize_checkpoint_backend()
    pop = b.backend["population"]
    assert len(pop) == 10
    for ind in pop:
        assert ind[0] > 0
        assert ind[0] < 1
        assert ind[1] > 1
        assert ind[1] < 2
        assert ind.fitness.values[0] > 1
        assert ind.fitness.values[0] < 3
    assert b.backend["start_gen"] == 0
    assert b.backend["halloffame"].items[0] == max(pop, key=lambda x: x[2])
    assert type(b.backend["logbook"]) == tools.Logbook
