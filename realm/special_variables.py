import random

class SpecialVariables:
    def __init__(self):
        # developer's should add to this list when defining a new special
        # variable
        self.special_variables = ["polynomial"]
        return

    def polynomial_naming(self, polynomial_dict):
        """This function returns a list of strings of the variable names"""
        order = polynomial_dict["order"]
        name = polynomial_dict["name"]
        var_names = []
        for i in range(order + 1):
            var_names.append("poly_" + name + "_" + str(i))
        return var_names

    def polynomial_toolbox(self, poly_dict, toolbox):
        """This function registers all the polynomial variables in deap toolbox"""
        for i in range(poly_dict["order"]+1):
            toolbox.register(
                "poly_" + poly_dict["name"] + "_" + str(i),
                random.uniform,
                poly_dict["min"],
                poly_dict["max"],
            )
        return toolbox
