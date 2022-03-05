"""Integration Test to validate the Evolutionary Algorithm.
The Binh and Korn function is a two-objective function. 
[1]T. T. Binh and U. Korn, “MOBES: A multiobjective evolution strategy 
for constrained optimization problems,” in The third international 
conference on genetic algorithms (Mendel 97), 1997, vol. 25, p. 27.
We use it as a performance test for two-objective optimization.
"""

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
    assert hypervol > 4200 
