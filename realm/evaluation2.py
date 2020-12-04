import os, sys
from jinja2 import nativetypes

from realm.openmc_evaluation import OpenMCEvaluation


class Evaluation:
    def __init__(self):
        self.supported_solvers = ["openmc", "moltres"]
        self.scripts = {}
        # developer should add to here when adding a new solver
        self.eval_dict = {"openmc": OpenMCEvaluation()}

    def add_evaluator(self, solver_name, input_script):
        """This function adds information an evaluator to this class for later
        use in eval_fn_generator.
        """
        self.scripts[solver_name] = input_script
        return

    def eval_fn_generator(self, control_dict, output_dict, input_dict):
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
                method(self.scripts["solver"], control_vars[solver])
                output_vals = self.get_output_vals(
                    output_vals, solver, output_dict, control_dict
                )
            return tuple(output_vals)

        return eval_function

    def get_output_vals(self, output_vals, solver, output_dict, control_vars):
        """This function returns a populated list with output values for each
        solver
        """
        for i, var in enumerate(output_dict):
            if output_dict[var] == solver:
                if var in control_vars[solver]:
                    output_vals[i] = control_vars[solver][var]
                #elif var in self.eval_dict[solver].pre_defined_outputs:


        return output_vals

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

    def render_jinja_template_python(self, script, control_vars_solver):
        """This function renders a jinja2 templated python file
        This will be used by solver's with a python interface such as OpenMC
        This returns a the templated python script
        """
        env = nativetypes.NativeEnvironment()
        with open(script) as s:
            imported_script = s.read()
        template = nativetypes.NativeTemplate(imported_script)
        render_str = "template.render("
        for inp in control_vars_solver:
            render_str += "**{'" + inp + "':" + str(control_vars_solver[inp]) + "},"
        render_str += ")"
        print(render_str)
        rendered_template = eval(render_str)
        return rendered_template

    def render_jinja_template(self):
        """This function renders a jinja2 templated input file
        This will be used by solver's with a text based interface such as Moltres
        """
        return

    def openmc_run(self, openmc_script, control_vars_solver):
        """This function runs the rendered openmc script"""
        rendered_openmc_script = self.render_jinja_template_python(
            openmc_script, control_vars_solver
        )
        exec(rendered_openmc_script)
        return

    def moltres_run():
        """This function runs the rendered moltres input file"""
        return
