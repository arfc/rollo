import os
import subprocess
import ast
import shutil
import time
import jinja2
from rollo.openmc_evaluation import OpenMCEvaluation
from rollo.moltres_evaluation import MoltresEvaluation


class Evaluation:
    """Holds functions that generate and execute the evaluation solver's scripts.

    DEAP's (evolutionary algorithm package) fitness evaluator requires an
    evaluation function to evaluate each individual's fitness values. The
    Evaluation class contains a method that creates an evaluation function that
    runs the nuclear software and returns the required fitness values, defined
    in the input file.

    Attributes
    ----------
    supported_solvers : list of str
        list of supported evaluation software
    input_scripts : dict
        key is evaluation software name, value is that evaluation software's
        template input script name
    output_scripts : dict
        key is evaluation software name, value is that evaluation software's
        template output script name
    eval_dict : dict
        key is evaluation software name, value is a class containing the
        functions to evaluate its output files

    """

    def __init__(self):
        self.supported_solvers = ["openmc", "moltres"]
        self.input_scripts = {}
        self.output_scripts = {}
        # Developers can add new solvers to self.eval_dict below
        self.eval_dict = {
            "openmc": OpenMCEvaluation(),
            "openmc_gc": OpenMCEvaluation(),
            "moltres": MoltresEvaluation()}

    def add_evaluator(self, solver_name, input_script, output_script):
        """Adds information about an evaluator to the Evaluation class object
        for later use in eval_fn_generator.

        Parameters
        ----------
        solver_name : str
            name of solver
        input_script : str
            input script name
        output_script : str
            optional output script name
        """

        self.input_scripts[solver_name] = input_script
        try:
            self.output_scripts[solver_name] = output_script
        except BaseException:
            pass
        return

    def eval_fn_generator(
            self,
            control_dict,
            output_dict,
            input_evaluators,
            gens,
            parallel_type):
        """Returns a function that accepts a DEAP individual and returns a
        tuple of output values listed in outputs

        Parameters
        ----------
        control_dict : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        input_evaluators : dict
            evaluators sub-dictionary from input file

        Returns
        -------
        eval_function : function
            function that runs the evaluation software and returns output values
            output by the software

        """
        if parallel_type == "supercomputer":
            def eval_function(pop):
                order_of_solvers = self.solver_order(input_evaluators)
                control_vars_dict = {}
                output_vals_dict = OrderedDict()
                for ind in pop:
                    name = str(ind.gen) + "_" + str(ind.num)
                    control_vars_dict[name] = self.name_ind(
                        ind, control_dict, input_evaluators)
                    output_vals_dict[name] = [None] * len(output_dict)
                return all_output_vals # list of tuples
        else:
            def eval_function(ind):
                """Accepts a DEAP individual and returns a tuple of output values
                listed in outputs

                Parameters
                ----------
                ind : deap.creator.Ind
                    Created in `rollo.toolbox_generator.ToolboxGenerator`. It is
                    a list with special attributes.

                Returns
                -------
                tuple
                    output values from evaluators ordered by output_dict

                """

                control_vars = self.name_ind(ind, control_dict, input_evaluators)
                output_vals = [None] * len(output_dict)
                order_of_solvers = self.solver_order(input_evaluators)

                for solver in order_of_solvers:
                    # path name for solver's run
                    path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
                    os.mkdir(path)
                    self.run_input_script(solver, control_vars[solver], ind, path)
                    if "execute2" in input_evaluators[solver]:
                        self.run_execute(
                            input_evaluators[solver]["execute2"], path)
                    # get output values
                    output_vals = self.get_output_vals(
                        output_vals, solver, output_dict, control_vars, path
                    )
                    if input_evaluators[solver]["keep_files"] == "none":
                        shutil.rmtree(path)
                    elif input_evaluators[solver]["keep_files"] == "only_final":
                        if ind.gen < gens - 1:
                            shutil.rmtree(path)
                return tuple(output_vals)

        return eval_function

    def run_input_script(self, solver, control_vars_solver, ind, path):
        # render jinja-ed input script
        rendered_script = self.render_jinja_template(
            script=self.input_scripts[solver][1],
            control_vars_solver=control_vars_solver,
            ind=ind,
            solver=solver
        )
        # enter directory for this particular solver's run
        os.chdir(path)
        # run input file
        f = open(self.input_scripts[solver][1], "w+")
        f.write(rendered_script)
        f.close()
        with open("input_script_output.txt", "wb") as output:
            subprocess.call(
                self.input_scripts[solver][0] +
                " " +
                self.input_scripts[solver][1],
                stdout=output,
                stderr=output,
                shell=True)
        os.chdir("../")
        return

    def run_execute(self, input_evaluator_solver_execute2, path):
        os.chdir(path)
        for i, executables in enumerate(input_evaluator_solver_execute2):
            if len(executables) > 1:
                shutil.copyfile("../" + executables[1], executables[1])
                execute = executables[0] + " " + executables[1]
            else:
                execute = executables[0]
            txt_file = "execute_" + str(i) + "_output.txt"
            with open(txt_file, "wb") as output:
                subprocess.call(
                    execute,
                    stdout=output,
                    stderr=output,
                    shell=True)
        os.chdir("../")
        return

    def solver_order(self, input_evaluators):
        order = [None] * len(input_evaluators)
        for solver in input_evaluators:
            order[input_evaluators[solver]["order"]] = solver
        return order

    def get_output_vals(
            self,
            output_vals,
            solver,
            output_dict,
            control_vars,
            path):
        """Returns a populated list with output values for each solver

        Parameters
        ----------
        output_vals : list
            empty list of the correct size
        solver : str
            name of solver
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        control_vars : dict
            maps the control_dict's variable names to values from ind list to
            order the output_vals correctly
        path : str
            path name

        Returns
        -------
        output_vals : list
            output values requested by rollo input file in correct order

        """

        if self.output_scripts[solver]:
            # copy rendered output script into a new file in the particular
            # solver's run
            shutil.copyfile(
                self.output_scripts[solver][1],
                path + "/" + self.output_scripts[solver][1])
            # enter directory for this particular solver's run
            os.chdir(path)
            # run the output script
            execute = self.output_scripts[solver][0] + \
                " " + self.output_scripts[solver][1]
            txt_file = "./output_script_output.txt"
            with open(txt_file, "wb") as output:
                subprocess.call(
                    execute,
                    stdout=output,
                    stderr=output,
                    shell=True)
            # return the output script's printed dictionary into a variable
            with open(txt_file) as fp:
                firstline = fp.readlines()[0]
            oup_script_results = ast.literal_eval(firstline)
            # go back to normal directory with all files
            os.chdir("../")
        for i, var in enumerate(output_dict):
            if output_dict[var] == solver:
                # if variable is a control variable
                if var in control_vars[solver]:
                    output_vals[i] = control_vars[solver][var]
                # if variable's analysis script is pre-defined
                elif var in self.eval_dict[solver].pre_defined_outputs:
                    os.chdir(path)
                    method = getattr(self.eval_dict[solver], "evaluate_" + var)
                    output_vals[i] = method()
                    os.chdir("../")
                # if variable's defined in output script
                else:
                    output_vals[i] = oup_script_results[var]
        return output_vals

    def name_ind(self, ind, control_dict, input_evaluators):
        """Returns a dictionary that maps the control_dict's variable names to
        values from ind list

        Parameters
        ----------
        ind : deap.creator.Ind
            Created in `rollo.toolbox_generator.ToolboxGenerator`. It is
            a list with special attributes.
        control_dict : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value
        input_evaluators : dict
            evaluators sub-dictionary from input file

        Returns
        -------
        control_vars : dict
            maps the control_dict's variable names to values from ind list to
            order the output_vals correctly

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

    def render_jinja_template(self, script, control_vars_solver, ind, solver):
        """Renders a jinja2 templated input file. This will be used by solver's
        with a text based interface such as Moltres
        Parameters
        ----------
        script : str
            name of evaluator template script
        control_vars_solver : str
            name of evaluation solver software
        Returns
        -------
        rendered_template : str
            rendered evaluator template script
        """

        with open(script) as f:
            tmp = jinja2.Template(f.read())
        render_str = "tmp.render("
        for var in control_vars_solver:
            render_str += str(var) + "='" + \
                str(control_vars_solver[var]) + "',"
            # special condition for moltres
        if solver == "moltres":
            render_str += "group_constant_dir='../openmc_gc_" + \
                str(ind.gen) + "_" + str(ind.num) + "'"
        render_str += ")"
        rendered_template = eval(render_str)

        return rendered_template
