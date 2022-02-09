import os, subprocess, pickle 
from deap import base, creator, tools
import deap.benchmarks.tools as bt
import numpy as np

def test_binh_hypervolume():

    creator.create("obj", base.Fitness, weights=(-1.0,-1.0))
    creator.create("Ind", list, fitness=creator.obj)

    os.chdir("./input_test_files")
    subprocess.call("python ../../../rollo -i input_test_binh.json", shell=True)
    os.chdir("../")
    with open("./input_test_files/checkpoint.pkl", "rb") as cp_file:
        cp = pickle.load(cp_file)

    results = cp["all"]
    final_pop = results["populations"][-1]
    non_dom = tools.sortNondominated(final_pop, k=len(final_pop), first_front_only=True)[0]
    ref = np.array([120,50])
    hypervol = bt.hypervolume(non_dom, ref)
    print(hypervol)
    assert hypervol > 4200