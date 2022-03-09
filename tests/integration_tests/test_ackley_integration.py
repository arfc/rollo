"""Integration Test to validate the Evolutionary Algorithm.
The Ackley function is one of the well-known benchmarks used for evolutionary
or metaheuristic optimization (https://www.sfu.ca/~ssurjano/ackley.html).
The minimum value is 0 at (0,0).
We use it as a performance test for single-objective optimization.
"""

import os
import subprocess
import pickle
from deap import base, creator, tools, algorithms

if os.path.exists("./input_test_files/checkpoint.pkl"):
    os.remove("./input_test_files/checkpoint.pkl")


def test_ackley_integration():

    creator.create("obj", base.Fitness, weights=(1.0,))
    creator.create("Ind", list, fitness=creator.obj)

    os.chdir("./input_test_files")
    subprocess.call(
        "python ../../../rollo -i input_test_ackley.json",
        shell=True)
    os.chdir("../")
    with open("./input_test_files/checkpoint.pkl", "rb") as cp_file:
        cp = pickle.load(cp_file)

    logbook = cp["all"]
    assert min(logbook["outputs"][-1])[0] < 0.5
    os.remove("./input_test_files/checkpoint.pkl")
    return


def test_ackley_integration_supercomputer():

    creator.create("obj", base.Fitness, weights=(1.0,))
    creator.create("Ind", list, fitness=creator.obj)

    os.chdir("./input_test_files")
    subprocess.call(
        "python ../../../rollo -i input_test_ackley_supercomputer.json",
        shell=True)
    os.chdir("../")
    with open("./input_test_files/checkpoint.pkl", "rb") as cp_file:
        cp = pickle.load(cp_file)

    logbook = cp["all"]
    assert min(logbook["outputs"][-1])[0] < 0.5
    os.remove("./input_test_files/checkpoint.pkl")
    return


test_ackley_integration_supercomputer()
