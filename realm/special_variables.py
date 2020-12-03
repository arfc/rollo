class SpecialVariables:
    def __init__(self):
        # developer's should add to this list when defining a new special
        # variable
        self.special_variables = ["polynomial"]
        return

    def polynomial_naming(self, polynomial_dict):
        """This function returns a list of strings of the variable names"""
        order = polynomial_dict["order"]
        name = order = polynomial_dict["name"]
        var_names = []
        for i in range(len(order) + 1):
            var_names.append("poly_" + name + "_" + str(i))
        return var_names

    def polynomial_generation():
        """This function returns a list of values for the polynomial variable"""
        return
