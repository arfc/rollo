""" This file creates "test_checkpoint.pkl" that is used in test_backend.py
for testing purposes
"""

import pickle
import random
from deap import base, creator, tools, algorithms
import numpy as np

creator.create("obj", base.Fitness, weights=(1.0,))
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


pop = toolbox.population(n=toolbox.pop_size)
fitnesses = toolbox.map(toolbox.evaluate, pop)
for ind, fitness in zip(pop, fitnesses):
    ind.fitness.values = (fitness[0],)
    ind.output = fitness
invalids = [ind for ind in pop if not ind.fitness.valid]
hof = tools.HallOfFame(maxsize=1)
hof.update(pop)
logbook = tools.Logbook()
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("max", np.max)
record = stats.compile(pop)
gen = 0
logbook.record(gen=gen, evals=len(invalids), **record)
all = {}
all["ind_naming"] = {
    "packing_fraction": 0,
    "polynomial_triso_0": 1,
    "polynomial_triso_1": 2,
    "polynomial_triso_2": 3,
    "polynomial_triso_3": 4,
}
all["oup_naming"] = {
    "packing_fraction": 0,
    "keff": 1,
    "num_batches": 2,
    "max_temp": 3,
}
all["populations"] = [pop]
for ind in pop:
    oup = ind.output
all["outputs"] = [oup]
cp = dict(
    population=pop,
    generation=gen,
    halloffame=hof,
    logbook=logbook,
    rndstate=random.getstate(),
    all=all,
)
checkpoint_file = "test_checkpoint.pkl"
with open(checkpoint_file, "wb") as cp_file:
    pickle.dump(cp, cp_file)
