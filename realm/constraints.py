from collections import defaultdict
import operator
import warnings


class Constraints(object):
    """This class defines constraints in model
    # number, operator, value
    """

    def __init__(self, output_dict):
        self.output_dict = output_dict
        self.constraints = defaultdict(list)

    def add_constraint(self, fitness_index, operator_type, value):
        """This function adds a constraint's operator and value to the
        self.constraints list
        """
        if fitness_index in self.constraints:
            warnings.warn(
                "Warning... This variable's constraint \
            was previously defined"
            )
        self.constraints[fitness_index].append(operator_type)
        self.constraints[fitness_index].append(value)

    def apply_constraints(self, pop):
        """This function will delete individuals that don't meet the
        constraints in self.constraints and return a population that meets
        them
        """
        if len(self.constraints) == 0:
            warnings.warn("Warning... No constraints defined")
            return pop
        new_pop = []
        for ind in pop:
            not_constrained = True
            for index in self.constraints:
                if self.constraints[index][0](
                    ind.output[index], self.constraints[index][1]
                ):
                    pass
                else:
                    not_constrained = False
            if not_constrained:
                new_pop.append(ind)
        return new_pop



    def apply_constraints(self, pop):
        for ind in pop: 
