from rollo.backend import BackEnd
from deap import base, creator, tools
import os
import random
from collections import OrderedDict

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


def ind_vals():
    pf = toolbox.pf()
    poly = toolbox.poly()
    return creator.Ind([pf, poly, pf + poly])


toolbox.register("individual", ind_vals)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def evaluator_fn(ind):
    return tuple([ind[0] + ind[1], 5])


toolbox.register("evaluate", evaluator_fn)
control_dict = OrderedDict(
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

input_file = {}  # placeholder


def test_initialize_new_backend():
    b = BackEnd(
        "square_checkpoint.pkl",
        creator,
        control_dict,
        output_dict,
        input_file,
        0)
    b.initialize_new_backend()
    assert b.results["start_gen"] == 0
    assert isinstance(b.results["halloffame"], tools.HallOfFame)
    assert isinstance(b.results["logbook"], tools.Logbook)
    assert isinstance(b.results["all"], dict)


def test_ind_naming():
    b = BackEnd(
        "square_checkpoint.pkl",
        creator,
        control_dict,
        output_dict,
        input_file,
        0)
    ind_dict = b.ind_naming()
    expected_ind_dict = {
        "packing_fraction": 0,
        "polynomial_triso_0": 1,
        "polynomial_triso_1": 2,
        "polynomial_triso_2": 3,
        "polynomial_triso_3": 4,
    }
    assert ind_dict == expected_ind_dict


def test_output_naming():
    b = BackEnd(
        "square_checkpoint.pkl",
        creator,
        control_dict,
        output_dict,
        input_file,
        0)
    oup_dict = b.output_naming()
    expected_oup_dict = {
        "packing_fraction": 0,
        "keff": 1,
        "num_batches": 2,
        "max_temp": 3,
    }
    assert oup_dict == expected_oup_dict


def test_initialize_checkpoint_backend():
    os.chdir("./input_test_files")
    os.system("python generate_backend_pickle.py")
    os.chdir("../")
    b = BackEnd(
        "input_test_files/test_checkpoint.pkl",
        creator,
        control_dict,
        output_dict,
        input_file,
        0,
    )
    b.initialize_checkpoint_backend()
    pop = b.results["population"]
    assert len(pop) == 10
    for ind in pop:
        assert ind[0] > 0
        assert ind[0] < 1
        assert ind[1] > 1
        assert ind[1] < 2
        assert ind.fitness.values[0] > 1
        assert ind.fitness.values[0] < 3
    assert b.results["start_gen"] == 0
    assert b.results["halloffame"].items[0] == max(pop, key=lambda x: x[2])
    assert isinstance(b.results["logbook"], tools.Logbook)
    assert len(b.results["logbook"]) == 1
    os.remove("./input_test_files/test_checkpoint.pkl")


def test_update_backend():
    os.chdir("./input_test_files")
    os.system("python generate_backend_pickle.py")
    os.chdir("../")
    b = BackEnd(
        "input_test_files/test_checkpoint.pkl",
        creator,
        control_dict,
        output_dict,
        input_file,
        0,
    )
    b.initialize_checkpoint_backend()
    new_pop = toolbox.population(n=toolbox.pop_size)
    gen = 1
    fitnesses = toolbox.map(toolbox.evaluate, new_pop)
    for ind, fitness in zip(new_pop, fitnesses):
        ind.fitness.values = (
            fitness[0],
            fitness[1],
        )
        ind.output = fitness
    invalids = [ind for ind in new_pop if not ind.fitness.valid]
    rndstate = random.getstate()
    b.update_backend(new_pop, gen, invalids, rndstate)
    pop = b.results["population"]
    assert b.results["halloffame"].items[0] == max(
        pop + new_pop, key=lambda x: x[2])
    assert len(b.results["logbook"]) == 2
    bb = BackEnd(
        "input_test_files/test_checkpoint.pkl",
        creator,
        control_dict,
        output_dict,
        input_file,
        0,
    )
    bb.initialize_checkpoint_backend()
    assert len(bb.results["logbook"]) == 2
    os.remove("./input_test_files/test_checkpoint.pkl")
