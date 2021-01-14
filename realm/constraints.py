from collections import defaultdict
import operator
import warnings
import random


class Constraints(object):
    def __init__(self, output_dict, input_constraints, toolbox):
        self.constraints = self.constraints_list(input_constraints)
        self.numbered_oup_dict = self.output_dict_numbered(output_dict)
        self.ops = {
            "<": operator.lt,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            ">=": operator.ge,
            ">": operator.gt,
        }
        self.toolbox = toolbox

    def output_dict_numbered(self, output_dict):
        """Returns dictionary of output variables and their corresponding index"""
        numbered_oup_dict = {}
        for i, key in enumerate(output_dict):
            numbered_oup_dict[key] = i
        return numbered_oup_dict

    def constraints_list(self, input_constraints):
        constraints_list = []
        for c in input_constraints:
            if type(input_constraints[c]["operator"]) is list:
                for i in range(len(input_constraints[c]["operator"])):
                    constraints_list.append(
                        [
                            c,
                            {
                                "op": input_constraints[c]["operator"][i],
                                "val": input_constraints[c]["constrained_val"][i],
                            },
                        ]
                    )
            else:
                constraints_list.append(
                    [
                        c,
                        {
                            "op": input_constraints[c]["operator"],
                            "val": input_constraints[c]["constrained_val"],
                        },
                    ]
                )
        return constraints_list

    def apply_constraints(self, pop):
        new_pop = []
        for ind in pop:
            not_constrained = True
            for i, c in enumerate(self.constraints):
                index = self.numbered_oup_dict[c[0]]
                if self.ops[c[1]["op"]](ind.output[index], c[1]["val"]):
                    pass
                else:
                    not_constrained = False
            if not_constrained:
                new_pop.append(ind)
        final_pop = [self.toolbox.clone(ind) for ind in new_pop]
        while len(final_pop) < len(pop):
            final_pop.append(self.toolbox.clone(random.choice(new_pop)))
        warnings.warn(
            "{}% of pop was constrained".format(
                (len(pop) - len(new_pop)) / len(final_pop) * 100
            )
        )
        return final_pop
