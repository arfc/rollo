from deap import base, creator, tools, algorithms


class DeapOperators(object):
    """A class that registers deap toolbox operators. This class was required
    because the operators take different input variables
    """

    def add_toolbox_operators(
        self, toolbox, selection_dict, mutation_dict, mating_dict
    ):
        """This function adds selection, mutation, and mating operators to
        the deap toolbox
        """
        toolbox = self.add_selection_operators(toolbox, selection_dict)
        toolbox = self.add_mutation_operators(toolbox, mutation_dict)
        toolbox = self.add_mating_operators(toolbox, mating_dict)
        return toolbox

    def add_selection_operators(self, toolbox, selection_dict):
        operator = selection_dict["operator"]
        if operator == "selTournament":
            toolbox.register(
                "select",
                tools.selTournament,
                k=selection_dict["k"],
                tournsize=selection_dict["tournsize"],
            )
        elif operator == "selNSGA2":
            toolbox.register("select", tools.selNSGA2, k=selection_dict["k"])
        elif operator == "selBest":
            toolbox.register("select", tools.selBest, k=selection_dict["k"])
        elif operator == "selLexicase":
            toolbox.register("select", tools.selLexicase, k=selection_dict["k"])
        return toolbox

    def add_mutation_operators(self, toolbox, mutation_dict):
        operator = mutation_dict["operator"]
        if operator == "mutGaussian":
            toolbox.register(
                "mutate",
                tools.mutGaussian,
                mu=mutation_dict["mu"],
                sigma=mutation_dict["sigma"],
                indpb=mutation_dict["indpb"],
            )
        elif operator == "mutPolynomialBounded":
            toolbox.register(
                "mutate",
                tools.mutPolynomialBounded,
                eta=mutation_dict["eta"],
                indpb=mutation_dict["indpb"],
            )
        return toolbox

    def add_mating_operators(self, toolbox, mating_dict):
        operator = mating_dict["operator"]
        if operator == "cxOnePoint":
            toolbox.register("mate", tools.cxOnePoint)
        elif operator == "cxUniform":
            toolbox.register("mate", tools.cxUniform, indpb=mating_dict["indpb"])
        elif operator == "cxBlend":
            toolbox.register("mate", tools.cxBlend, alpha=mating_dict["alpha"])
        return toolbox
