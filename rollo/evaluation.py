import os
import subprocess
import ast
import shutil
import time
import jinja2
from collections import OrderedDict
from rollo.openmc_evaluation import OpenMCEvaluation
from rollo.moltres_evaluation import MoltresEvaluation


class Evaluation:
    """Holds functions that generate and execute the evaluation solver's scripts.

    DEAP's (evolutionary algorithm package) fitness evaluator requires an
    evaluation function to evaluate each individual's fitness values. The
    Evaluation class contains a method that creates an evaluation function that
    runs the nuclear software and returns the required fitness values, defined
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
        self.supported_solvers = ["openmc", "openmc_gc", "moltres"]
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
            parallel_method):
        """if parallel_method is none or multiprocessing, this function
        returns a function that accepts a DEAP individual and returns a
        tuple of output values listed in outputs

        if parallel_method is job_control, this function returns a function
        that accepts a list of DEAP individuals (population) and returns
        a list of output value tuples. Each tuple corresponds to one
        individual

        Parameters
        ----------
        control_dict : OrderedDict
            Ordered dict of control variables as keys and a list of their
            solver and number of variables as each value
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        input_evaluators : dict
            evaluators sub-dictionary from input file
        gens : int
            total generations in simulation (defined in input file)
        parallel_method : {'none', 'multiprocessing', 'job_control'}
            parallelization method

        Returns
        -------
        eval_function : function
            function that runs the evaluation software and returns output values
            output by the software

        """
        if parallel_method == "job_control":
            def eval_function(pop):
                """Accepts a list of DEAP individuals (population) and returns
                a list of output value tuples. Each tuple corresponds to one
                individual

                Parameters
                ----------
                pop : list
                    list of deap.creator.Ind

                Returns
                -------
                all_output_vals : list of tuple
                    each index of list contains a tuple of output values from
                    evaluators ordered by output_dict

                """
                order_of_solvers = self.solver_order(input_evaluators)
                control_vars_dict = {}
                output_vals_dict = OrderedDict()
                for ind in pop:
                    name = str(ind.gen) + "_" + str(ind.num)
                    control_vars_dict[name] = self.name_ind(
                        ind, control_dict, input_evaluators)
                    output_vals_dict[name] = [None] * len(output_dict)

                for solver in order_of_solvers:
                    self.create_input_execute_output_scripts(
                        pop,
                        solver,
                        control_vars_dict,
                        input_evaluators[solver])
                    self.run_input_and_execute_and_output_scripts(
                        pop, solver, input_evaluators[solver])
                    all_output_vals = self.get_output_vals_job_control(
                        output_vals_dict, pop, solver,
                        output_dict, control_vars_dict)
                # remove files
                if input_evaluators[solver]["keep_files"] == "none":
                    for ind in pop:
                        name = str(ind.gen) + "_" + str(ind.num)
                        path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
                        shutil.rmtree(path)
                elif input_evaluators[solver]["keep_files"] == "only_final":
                    for ind in pop:
                        if ind.gen < gens - 1:
                            name = str(ind.gen) + "_" + str(ind.num)
                            path = solver + "_" + \
                                str(ind.gen) + "_" + str(ind.num)
                            shutil.rmtree(path)
                return all_output_vals  # list of tuples
        else:
            def eval_function(ind):
                """Accepts a DEAP individual and returns a tuple of output
                values listed in outputs

                Parameters
                ----------
                ind : deap.creator.Ind
                    created in `rollo.toolbox_generator.ToolboxGenerator`.
                    It is a list with special attributes.

                Returns
                -------
                tuple
                    output values from evaluators ordered by output_dict

                """
                control_vars = self.name_ind(
                    ind, control_dict, input_evaluators)
                output_vals = [None] * len(output_dict)
                order_of_solvers = self.solver_order(input_evaluators)

                for solver in order_of_solvers:
                    # path name for solver's run
                    path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
                    os.mkdir(path)
                    # run input script
                    self.run_input_script_serial(
                        solver, control_vars[solver], ind, path)
                    # run execute if they exist
                    if "execute" in input_evaluators[solver]:
                        self.run_execute_serial(
                            input_evaluators[solver]["execute"], path)
                    # get output values
                    output_vals = self.run_output_script_serial(
                        output_vals, solver, output_dict, control_vars, path
                    )
                    # remove files
                    if input_evaluators[solver]["keep_files"] == "none":
                        shutil.rmtree(path)
                    elif input_evaluators[solver]["keep_files"] == \
                            "only_final":
                        if ind.gen < gens - 1:
                            shutil.rmtree(path)
                return tuple(output_vals)

        return eval_function

    def create_input_execute_output_scripts(
            self,
            pop,
            solver,
            control_vars_dict,
            input_evaluators_solver):
        """Renders input scripts, copies execute scripts, and renders
        output scripts for parallel_method=job_control in each
        individual's directory

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind
        solver : str
            name of solver
        control_vars_dict: dict
            multiple layers of dicts
            layer 1: gen_ind dir (str)
            layer 2: solver (str)
            layer 3: control parameter (str)
            layer 4: control parameter value (float)
        input_evaluators_solver: dict
            specific solver's evaluators sub-sub-dictionary from input file

        Returns
        -------
        None

        """
        for ind in pop:
            name = str(ind.gen) + "_" + str(ind.num)
            path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
            os.mkdir(path)
            self.render_input_script(
                solver, control_vars_dict[name][solver], ind, path)
            if "execute" in input_evaluators_solver:
                self.generate_execute_scripts(
                    path, input_evaluators_solver["execute"])
            self.generate_output_script(path, solver)
        return

    def run_input_and_execute_and_output_scripts(
            self, pop, solver, input_evaluators_solver):
        """Runs input scripts, execute scripts or executable, and
        output scripts for parallel_method=job_control in each
        individual's directory

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind
        solver : str
            name of solver
        control_vars_dict: dict
            multiple layers of dicts
            layer 1: gen_ind dir (str)
            layer 2: solver (str)
            layer 3: control parameter (str)
            layer 4: control parameter value (float)
        input_evaluators_solver: dict
            specific solver's evaluators sub-sub-dictionary from input file

        Returns
        -------
        None

        """
        # run input script
        run_input = self.generate_run_command_job_control(
            pop=pop,
            solver=solver,
            single_command=self.input_scripts[solver][0] + " " +
            self.input_scripts[solver][1] + " > input_script_out.txt 2>&1")
        subprocess.call(run_input, shell=True)
        # run execute script if exists
        if "execute" in input_evaluators_solver:
            for i, executable in enumerate(input_evaluators_solver["execute"]):
                single_command = ""
                for exe in executable:
                    single_command += exe + " "
                single_command += "> execute_" + str(i) + "_out.txt 2>&1"
                execute_input = self.generate_run_command_job_control(
                    pop=pop,
                    solver=solver,
                    single_command=single_command)
                subprocess.call(execute_input, shell=True)
        # run output script
        run_output = self.generate_run_command_job_control(
            pop=pop,
            solver=solver,
            single_command=self.output_scripts[solver][0] + " " +
            self.output_scripts[solver][1] + " > output_script_out.txt 2>&1")
        subprocess.call(run_output, shell=True)
        return

    def generate_run_command_job_control(self, pop, solver, single_command):
        """Generates bash command to run all directories executables
        for parallel_method=job_control

        Parameters
        ----------
        pop : list
            list of deap.creator.Ind
        solver : str
            name of solver
        control_vars_dict: dict
            multiple layers of dicts
            layer 1: gen_ind dir (str)
            layer 2: solver (str)
            layer 3: control parameter (str)
            layer 4: control parameter value (float)
        input_evaluators_solver: dict
            specific solver's evaluators sub-sub-dictionary from input file

        Returns
        -------
        command : str
            bash command to run all directories executables for
            parallel_method=job_control

        """
        command = ''''''
        count = 0
        for ind in pop:
            path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
            if count == 0:
                command += "cd " + path + "\n"
            else:
                command += "cd ../" + path + "\n"
            count += 1
            command += single_command + " & \n"
            command += "sleep 1 \n"
        command += "wait"
        return command

    def get_output_vals_job_control(
            self,
            output_vals_dict,
            pop,
            solver,
            output_dict,
            control_vars_dict):
        """returns a list of output value tuples. Each tuple corresponds to
        output values for one individual. The results are in order of the
        individuals in pop. For parallel_method=job_control

        Parameters
        ----------
        output_vals_dict : dict
            layer 1: gen_ind dir (str)
            layer 2: list of output values requested by rollo input file
                     in correct order
        pop : list
            list of deap.creator.Ind
        solver : str
            name of solver
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        control_vars_dict: dict
            multiple layers of dicts
            layer 1: gen_ind dir (str)
            layer 2: solver (str)
            layer 3: control parameter (str)
            layer 4: control parameter value (float)

        Returns
        -------
        all_output_vals : list
            each index of list contains a tuple of output values from
            evaluators ordered by output_dict

        """
        all_output_vals = []
        for ind in pop:
            name = str(ind.gen) + "_" + str(ind.num)
            path = solver + "_" + str(ind.gen) + "_" + str(ind.num)
            output_vals_dict[name] = self.get_output_vals(
                output_vals_dict[name],
                solver,
                path,
                output_dict,
                control_vars_dict[name])
            all_output_vals.append(tuple(output_vals_dict[name]))
        return all_output_vals

    def run_input_script_serial(self, solver, control_vars_solver, ind, path):
        """Renders an input script into an individual's directory and runs it
        for parallel_method=none or multiprocessing

        Parameters
        ----------
        solver : str
            name of solver
        control_vars_solver : str
            name of evaluation solver software
        ind : deap.creator.Ind
        path : str
            path name

        Returns
        -------
        None

        """
        self.render_input_script(solver, control_vars_solver, ind, path)
        self.subprocess_call(
            path,
            "input_script_out.txt",
            self.input_scripts[solver][0] +
            " " +
            self.input_scripts[solver][1])
        return

    def run_execute_serial(self, input_evaluator_solver_execute, path):
        """copies execute scripts into an individual's directory if the scripts
        exists then runs it or only the executable for parallel_method=none
        or multiprocessing

        Parameters
        ----------
        input_evaluator_solver_execute : list
            execute list from specific solver's evaluators sub-sub-dictionary
            from input file
        path : str
            path name

        Returns
        -------
        None

        """
        self.generate_execute_scripts(path, input_evaluator_solver_execute)
        for i, executables in enumerate(input_evaluator_solver_execute):
            if len(executables) > 1:
                execute = executables[0] + " " + executables[1]
            else:
                execute = executables[0]
            self.subprocess_call(
                path, "execute_" + str(i) + "_output.txt", execute)
        return

    def solver_order(self, input_evaluators):
        """Returns a list with solver name at its order index

        Parameters
        ----------
        input_evaluators : dict
            evaluators sub-dictionary from input file

        Returns
        -------
        list
            list with solver name at its order index
            e.g. if openmc solver order = 0 and moltres solver order = 1, the
            returned list looks like ["openmc", "moltres"]

        """
        order = [None] * len(input_evaluators)
        for solver in input_evaluators:
            order[input_evaluators[solver]["order"]] = solver
        return order

    def render_input_script(self, solver, control_vars_solver, ind, path):
        """Renders an input script into an individual's directory

        Parameters
        ----------
        solver : str
            name of solver
        control_vars_solver : str
            name of evaluation solver software
        ind : deap.creator.Ind
        path : str
            path name

        Returns
        -------
        None

        """
        rendered_script = self.render_jinja_template(
            script=self.input_scripts[solver][1],
            control_vars_solver=control_vars_solver,
            ind=ind,
            solver=solver
        )
        os.chdir(path)
        f = open(self.input_scripts[solver][1], "w+")
        f.write(rendered_script)
        f.close()
        os.chdir("../")
        return

    def generate_execute_scripts(self, path, input_evaluator_solver_execute):
        """Copies execute scripts into an individual's directory

        Parameters
        ----------
        path : str
            path name
        input_evaluator_solver_execute : list
            execute list from specific solver's evaluators sub-sub-dictionary
            from input file

        Returns
        -------
        None

        """
        os.chdir(path)
        for executables in input_evaluator_solver_execute:
            if len(executables) > 1:
                shutil.copyfile("../" + executables[1], executables[1])
        os.chdir("../")
        return

    def generate_output_script(self, path, solver):
        """Copies output script into an individual's directory

        Parameters
        ----------
        path : str
            path name
        solver : str
            name of solver

        Returns
        -------
        None

        """
        os.chdir(path)
        shutil.copyfile(
            "../" + self.output_scripts[solver][1],
            self.output_scripts[solver][1])
        os.chdir("../")
        return

    def subprocess_call(self, path, out_file, command):
        """Runs command in bash

        Parameters
        ----------
        path : str
            path name
        out_file : str
            txt file to output command's stderror and stdoutput to
        command : str
            bash command to run

        Returns
        -------
        None

        """
        os.chdir(path)
        with open(out_file, "wb") as output:
            subprocess.call(
                command,
                stdout=output,
                stderr=output,
                shell=True)
        os.chdir("../")
        return

    def run_output_script_serial(
            self,
            output_vals,
            solver,
            output_dict,
            control_vars,
            path):
        """Copies an output script into an individual's directory and runs it
        and returns a populated list with output values for each solver

        Parameters
        ----------
        output_vals : list
            empty list of the correct size
        solver : str
            name of solver
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        control_vars : dict
            multiple layers of dict
            layer 1: solver name
            layer 2: control parameter str
            layer 3: control parameter value
        path : str
            path name

        Returns
        -------
        output_vals : list
            output values requested by rollo input file in correct order

        """
        if self.output_scripts[solver]:
            self.generate_output_script(path, solver)
            # run the output script
            self.subprocess_call(
                path,
                "./output_script_out.txt",
                self.output_scripts[solver][0] +
                " " +
                self.output_scripts[solver][1])
            output_vals = self.get_output_vals(
                output_vals, solver, path, output_dict, control_vars)
        return output_vals

    def get_output_vals(
            self,
            output_vals,
            solver,
            path,
            output_dict,
            control_vars):
        """Returns a populated list with output values for each solver

        Parameters
        ----------
        output_vals : list
            empty list of the correct size
        solver : str
            name of solver
        path : str
            path name
        output_dict : OrderedDict
            Ordered dict of output variables as keys and solvers as values
        control_vars : dict
            multiple layers of dict
            layer 1: solver name
            layer 2: control parameter str
            layer 3: control parameter value

        Returns
        -------
        output_vals : list
            output values requested by rollo input file in correct order

        """
        if self.output_scripts[solver]:
            # return the output script's printed dictionary into a variable
            with open("./" + path + "/output_script_out.txt") as fp:
                firstline = fp.readlines()[0]
            oup_script_results = ast.literal_eval(firstline)
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
            multiple layers of dict
            layer 1: solver name
            layer 2: control parameter str
            layer 3: control parameter value

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
        """Renders a jinja2 templated input file. This will be used by solvers
        with text-based interfaces such as Moltres

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
