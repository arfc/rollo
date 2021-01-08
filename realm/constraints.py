from collections import defaultdict
import operator
import warnings


class Constraints(object):
    def __init__(self, output_dict, input_constraints):
        self.input_constraints = input_constraints
        self.numbered_oup_dict = self.output_dict_numbered(output_dict)
        self.ops = {
            "<": operator.lt,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            ">=": operator.ge,
            ">": operator.gt,
        }

    def output_dict_numbered(self, output_dict):
        """Returns dictionary of output variables and their corresponding index"""
        numbered_oup_dict = {}
        for i, key in enumerate(output_dict):
            numbered_oup_dict[key] = i
        return numbered_oup_dict

    def apply_constraints(self, pop):
        for ind in pop:
            for c in self.input_constraints:
                index = self.numbered_oup_dict[c]
                if self.ops[self.input_constraints[c]["operator"]](
                    ind[index], self.input_constraints[c]["value"]
                ):
                    new_pop.append(ind)
                else:
                    pass
        return new_pop
