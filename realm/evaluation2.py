import os, sys
from jinja2 import nativetypes

sys.path.insert(1, "./plugin/")


class Evaluation:
    def __init__(self):
        self.supported_solvers = ["openmc", "moltres"]

    def add_evaluator(self):
        """This function adds information an evaluator to this class for later
        use in eval_fn_generator.
        """
        return

    def eval_fn_generator(self, control_dict, output_dict):
        """This function returns a function that accepts a DEAP individual
        and returns a tuple of output values listed in outputs
        """
        input_evaluators = input_dict["evaluators"]
        output_list = [0] * len(output_dict)

        def eval_function(ind):
            """This function accepts a DEAP individual
            and returns a tuple of output values listed in outputs
            """
            control_vars = self.name_ind(ind, control_dict)

            for solver in input_evaluators:
                path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
                os.mkdir(path)
                os.chdir(path)
                method(self, solver + "run")
                method(control_vars)

            return tuple(output_vals)

        return eval_function

    def name_ind(self, ind, control_dict, input_evaluators):
        """This function returns a dictionary that maps the control_dict's variable
        names to values from ind list
        """
        control_vars = {}
        for solver in input_evaluators:
            control_vars[solver] = {}
        for i, var in enumerate(control_dict):
            control_vars[control_dict[var]][var] = ind[i]
        return control_vars

    def render_jinja_template_python(self, script, input_dict):
        """This function renders a jinja2 templated python file
        This will be used by solver's with a python interface such as OpenMC
        This returns a the templated python script
        """
        env = nativetypes.NativeEnvironment()
        with open(script) as s:
            imported_script = s.read()
        template = nativetypes.NativeTemplate(imported_script)
        render_str = "template.render("
        for inp in input_dict:
            render_str += "**{'" + inp + "':" + str(input_dict[inp]) + "},"
        render_str += ")"
        print(render_str)
        rendered_template = eval(render_str)
        return rendered_template

    def render_jinja_template(self):
        """This function renders a jinja2 templated input file
        This will be used by solver's with a text based interface such as Moltres
        """
        return

    def openmc_run(self, input_dict):
        """This function runs the rendered openmc script"""
        rendered_openmc_script = self.render_jinja_template_python(
            openmc_script, input_dict
        )
        exec(rendered_openmc_script)
        return

    def moltres_run():
        """This function runs the rendered moltres input file"""
        return
