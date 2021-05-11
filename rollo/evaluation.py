import os, subprocess, ast, shutil, time
from jinja2 import nativetypes
from rollo.openmc_evaluation import OpenMCEvaluation
from rollo.moltres_evaluation import MoltresEvaluation


class Evaluation:
    """Holds functions that generate and execute the evaluation solver's scripts.

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
        # developer should add to here when adding a new solver
        self.eval_dict = {"openmc": OpenMCEvaluation(), "moltres": MoltresEvaluation()}

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
        except:
            pass
        return

    def eval_fn_generator(self, control_dict, output_dict, input_evaluators):
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

            self.rank_time = time.time()
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
                if input_evaluators[solver]["keep_files"] == False:
                    shutil.rmtree(path)
            return tuple(output_vals)

        return eval_function

    def get_output_vals(self, output_vals, solver, output_dict, control_vars, path):
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

    def system_call(self, command):
        """Runs evaluation software output file

        Parameters
        ----------
        command : str
            command to run in the command line

        Returns
        -------
        str
            printed output from running evaluation software output file

        """

        p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        return p.stdout.read()

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

    def render_jinja_template_python(self, script, control_vars_solver):
        """Renders a jinja2 templated python file and returns a templated python
        script. This will be used by solver's with a python interface such as
        OpenMC.

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
        """Renders a jinja2 templated input file. This will be used by solver's
        with a text based interface such as Moltres

        ### TO BE POPULATED
        """

        return

    def openmc_run(self, rendered_openmc_script):
        """Runs the rendered openmc script

        Parameters
        ----------
        rendered_openmc_script : str
            rendered OpenMC evaluator template script

        """

        f = open("openmc_input.py", "w+")
        f.write(rendered_openmc_script)
        f.close()
        with open("output.txt", "wb") as output:
            subprocess.call(["python", "-u", "./openmc_input.py"], stdout=output)
        return

    def moltres_run(self, rendered_moltres_script):
        """Runs the rendered moltres input file

        ### TO BE POPULATED
        """

        return
