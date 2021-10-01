"""Integration Test to validate the Evolutionary Algorithm.
The Ackley function is one of the well-known benchmarks used for evolutionary
or metaheuristic optimization (https://www.sfu.ca/~ssurjano/ackley.html).
The minimum value is 0 at (0,0).
"""


from rollo.algorithm import Algorithm
from rollo.constraints import Constraints
from deap import base, creator, tools
import random
import numpy as np
from collections import OrderedDict


def test_ackley_minimum_check():
    creator.create(
        "obj",
        base.Fitness,
        weights=(-1.0,),
    )
    creator.create("Ind", list, fitness=creator.obj)
    toolbox = base.Toolbox()
    toolbox.register("x1", random.uniform, -32.768, 32.768)
    toolbox.register("x2", random.uniform, -32.768, 32.768)
    toolbox.pop_size = 1000
    toolbox.ngen = 20

    def ind_vals():
        x1 = toolbox.x1()
        x2 = toolbox.x2()
        return creator.Ind([x1, x2])

    toolbox.register("individual", ind_vals)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    k = 5
    toolbox.register("select", tools.selTournament, k=15, tournsize=5)
    toolbox.register("mate", tools.cxBlend, alpha=0.46)
    toolbox.register(
        "mutate",
        tools.mutPolynomialBounded,
        eta=0.23,
        indpb=0.23,
        low=[-32.768, -32.768],
        up=[32.768, 32.768],
    )
    toolbox.cxpb = 0.46
    toolbox.mutpb = 0.23
    toolbox.objs = 1
    toolbox.min_list = [-32.768, -32.768]
    toolbox.max_list = [32.768, 32.768]

    control_dict = OrderedDict({"x1": ["openmc", 1], "x2": ["openmc", 1]})
    output_dict = OrderedDict(
        {
            "output": "openmc",
        }
    )

    def evaluator_fn(ind):
        x1, x2 = ind[0], ind[1]
        ackley = (
            -20 * np.exp(-0.2 * np.sqrt(1 / 2 * (x1 ** 2 + x2 ** 2)))
            - np.exp(1 / 2 * (np.cos(2 * np.pi * x1) + np.cos(2 * np.pi * x2)))
            + 20
            + np.exp(1)
        )
        return tuple([ackley])

    toolbox.register("evaluate", evaluator_fn)
    test_constraints = Constraints(
        output_dict=OrderedDict(),
        input_constraints={},
        toolbox=toolbox,
    )
    see_all = []
    bad = []

    def run():
        a = Algorithm(
            deap_toolbox=toolbox,
            constraint_obj=test_constraints,
            checkpoint_file=None,
            deap_creator=creator,
            control_dict=control_dict,
            output_dict=output_dict,
            input_dict={},
            start_time=0,
            parallel_method="none",
        )
        final_pop = a.generate()
        result = min(a.backend.results["all"]["outputs"][-1])[0]
        see_all.append(result)
        if result > 5:
            bad.append(result)
        # assert min(a.backend.results["all"]["outputs"][-1])[0] < 0.1

    for i in range(100):
        run()
    print(see_all)
    print(bad)


test_ackley_minimum_check()
