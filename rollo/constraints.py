import operator, warnings, random


class Constraints(object):
    """Holds information about constraints for the problem and functions
    to apply the constraints

    Parameters
    ----------
    output_dict : OrderedDict
        Ordered dict of output variables as keys and solvers as values
    input_constraints : dict
        constraints sub-dictionary from input file
    toolbox : deap.base.Toolbox object
        DEAP toolbox populated with user-defined genetic algorithm parameters

    Attributes
    ----------
    constraints : list
        list of constraints information
    numbered_oup_dict : dict
        output parameter name as key and ordered position as value
    ops: dict
        dict of accepted operators
    toolbox : deap.base.Toolbox object
        DEAP toolbox populated with user-defined genetic algorithm parameters

    """

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
        """Returns dictionary of output variables and their corresponding index

        Parameters
        ----------
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values

        Returns
        -------
        dict
            output parameter name as key and ordered position as value

        """

        numbered_oup_dict = {}
        for i, key in enumerate(output_dict):
            numbered_oup_dict[key] = i
        return numbered_oup_dict

    def constraints_list(self, input_constraints):
        """Returns list of constraints information

        Parameters
        ----------
        input_constraints : dict
            constraints sub-dictionary from input file

        Returns
        -------
        constraints_list : list
            list of constraints information

        """

        constraints_list = []
        for c in input_constraints:
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
        return constraints_list

    def apply_constraints(self, pop):
        """Removes individuals in population that fail to meet constraints

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind for that generation

        Returns
        -------
        list
            list of deap.creator.Ind for that generation with individuals that
            fail to meet constraints removed

        """

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
            str(len(pop) - len(new_pop))
            + " out of "
            + str(len(pop))
            + " inds were constrained"
        )
        return final_pop
