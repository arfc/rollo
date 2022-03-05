import os, subprocess, pickle 
from deap import base, creator, tools, algorithms

def test_ackley_integration():

    creator.create("obj", base.Fitness, weights=(1.0,))
    creator.create("Ind", list, fitness=creator.obj)

    os.chdir("./input_test_files")
    subprocess.call("python ../../../rollo -i input_test_ackley.json", shell=True)
    os.chdir("../")
    with open("./input_test_files/checkpoint.pkl", "rb") as cp_file:
        cp = pickle.load(cp_file)

    logbook = cp["all"]
    assert min(logbook["outputs"][-1])[0] < 0.1 