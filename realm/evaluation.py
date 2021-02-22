import os, sys, subprocess, ast, shutil
from jinja2 import nativetypes
import openmc
import subprocess

from realm.openmc_evaluation import OpenMCEvaluation
from realm.moltres_evaluation import MoltresEvaluation


class Evaluation:
    def __init__(self):
        self.supported_solvers = ["openmc", "moltres"]
        self.input_scripts = {}
        self.output_scripts = {}
        # developer should add to here when adding a new solver
        self.eval_dict = {"openmc": OpenMCEvaluation(), "moltres": MoltresEvaluation()}

    def add_evaluator(self, solver_name, input_script, output_script):
        """This function adds information an evaluator to this class for later
        use in eval_fn_generator.
        """
        self.input_scripts[solver_name] = input_script
        try:
            self.output_scripts[solver_name] = output_script
        except:
            pass
        return

    def eval_fn_generator(self, control_dict, output_dict, input_evaluators):
        """This function returns a function that accepts a DEAP individual
        and returns a tuple of output values listed in outputs
        """
        output_list = [0] * len(output_dict)

        def eval_function(ind):
            """This function accepts a DEAP individual
            and returns a tuple of output values listed in outputs
            """
            control_vars = self.name_ind(ind, control_dict, input_evaluators)
            output_vals = [None] * len(output_dict)

            for solver in input_evaluators:
                # path name for solver's run
                path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
                # render jinja-ed input script
                rendered_script = self.render_jinja_template_python(
                    script=self.input_scripts[solver],
                    control_vars_solver=control_vars[solver],
                )
                # enter directory for this particular solver's run
                print("IN", path)
                os.mkdir(path)
                os.chdir(path)
                # run solver's function where run is executed
                exec("self." + solver + "_run(rendered_script)")
                # go back to normal directory with all files
                os.chdir("../")
                # get output values
                output_vals = self.get_output_vals(
                    output_vals, solver, output_dict, control_vars, path
                )
            return tuple(output_vals)

        return eval_function

    def get_output_vals(self, output_vals, solver, output_dict, control_vars, path):
        """This function returns a populated list with output values for each
        solver
        """
        if self.output_scripts[solver]:
            #print(" in if statement", self.output_scripts[solver])
            # copy rendered output script into a new file in the particular solver's run
            shutil.copyfile(
                self.output_scripts[solver], path + "/" + solver + "_output.py"
            )
            # enter directory for this particular solver's run
            os.chdir(path)
            # run the output script
            oup_bytes = self.system_call("python " + solver + "_output.py")
            # return the output script's printed dictionary into a variable
            oup_script_results = ast.literal_eval(oup_bytes.decode("utf-8"))
            # go back to normal directory with all files
            os.chdir("../")

        for i, var in enumerate(output_dict):
            if output_dict[var] == solver:
                #print("IN OUT")
                # if variable is a control variable
                if var in control_vars[solver]:
                    output_vals[i] = control_vars[solver][var]
                # if variable's analysis script is pre-defined
                elif var in self.eval_dict[solver].pre_defined_outputs:
                    #print("predefined")
                    os.chdir(path)
                    method = getattr(self.eval_dict[solver], "evaluate_" + var)
                    output_vals[i] = method()
                    os.chdir("../")
                # if variable's defined in output script
                else:
                    # print("output scipt")
                    output_vals[i] = oup_script_results[var]
                #rint("out out")
        return output_vals

    def system_call(self, command):
        p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        return p.stdout.read()

    def name_ind(self, ind, control_dict, input_evaluators):
        """This function returns a dictionary that maps the control_dict's variable
        names to values from ind list
        """
        control_vars = {}
        for solver in input_evaluators:
            control_vars[solver] = {}
        for i, var in enumerate(control_dict):
            if control_dict[var][1] == 1:
                ind_vars = ind[i]
            else:
                ind_vars = []
                for j in range(control_dict[var][1]):
                    ind_vars.append(ind[i + j])
            control_vars[control_dict[var][0]][var] = ind_vars
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
        rendered_template = eval(render_str)
        return rendered_template

    def render_jinja_template(self):
        """This function renders a jinja2 templated input file
        This will be used by solver's with a text based interface such as Moltres
        """
        return

    def openmc_run(self, rendered_openmc_script):
        """This function runs the rendered openmc script"""
        f = open("openmc_input.py", "w+")
        f.write(rendered_openmc_script)
        f.close()
        with open("output.txt", "w+") as output:
            subprocess.call(["python", "./openmc_input.py"], stdout=output)
        return

    def moltres_run(self, rendered_moltres_script):
        """This function runs the rendered moltres input file"""
        return
