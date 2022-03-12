import pytest
import ast
import os
import shutil
from rollo.evaluation import Evaluation
from collections import OrderedDict
from deap import base, creator

if os.path.exists("./input_test_files/openmc_0_0"):
    shutil.rmtree("./input_test_files/openmc_0_0")
if os.path.exists("./input_test_files/openmc_0_1"):
    shutil.rmtree("./input_test_files/openmc_0_1")
if os.path.exists("./input_test_files/moltres_0_0"):
    shutil.rmtree("./input_test_files/moltres_0_0")
if os.path.exists("./input_test_files/moltres_0_1"):
    shutil.rmtree("./input_test_files/moltres_0_1")


def init():
    creator.create(
        "obj",
        base.Fitness,
        weights=(
            1.0,
        ),
    )
    creator.create("Ind", list, fitness=creator.obj)


def test_eval_fn_generator():
    os.chdir("./input_test_files")
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc",
        input_script=[
            "python",
            "input_test_eval_fn_generator_openmc_template.py"],
        output_script=[
            "python",
            "input_test_eval_fn_generator_openmc_output.py"],
    )
    ev.add_evaluator(
        solver_name="moltres",
        input_script=[
            "python", "input_test_render_jinja_template_python.py"],
        output_script=[
            "python", "input_test_evaluation_get_output_vals_moltres.py"], )
    eval_function = ev.eval_fn_generator(
        control_dict=OrderedDict(
            {"packing_fraction": ["openmc", 1]}
        ),
        output_dict=OrderedDict(
            {
                "packing_fraction": "openmc",
                "keff": "openmc",
                "max_temp": "moltres",
                "num_batches": "openmc",
            }
        ),
        input_evaluators={
            "openmc": {"keep_files": True, "order": 0},
            "moltres": {"keep_files": True, "order": 1},
        },
        gens=2,
        parallel_method="none"
    )
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    ind = creator.Ind([0.03, 1, 1, 1, 1])
    ind.gen = 0
    ind.num = 0
    output_vals = eval_function(ind)
    expected_output_vals = tuple([0.03, output_vals[1], 1000, 10])
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./moltres_0_0")
    os.chdir("../")
    assert output_vals == expected_output_vals


def test_eval_fn_generator_job_control():
    os.chdir("./input_test_files")
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc",
        input_script=[
            "python",
            "input_test_eval_fn_generator_openmc_template.py"],
        output_script=[
            "python",
            "input_test_eval_fn_generator_openmc_output.py"],
    )
    ev.add_evaluator(
        solver_name="moltres",
        input_script=[
            "python", "input_test_render_jinja_template_python.py"],
        output_script=[
            "python", "input_test_evaluation_get_output_vals_moltres.py"], )
    eval_function = ev.eval_fn_generator(
        control_dict=OrderedDict(
            {"packing_fraction": ["openmc", 1],
                "polynomial_triso": ["openmc", 4]}
        ),
        output_dict=OrderedDict(
            {
                "packing_fraction": "openmc",
                "keff": "openmc",
                "max_temp": "moltres",
                "num_batches": "openmc",
            }
        ),
        input_evaluators={
            "openmc": {"keep_files": True, "order": 0},
            "moltres": {"keep_files": True, "order": 1},
        },
        gens=1,
        parallel_method="job_control"
    )
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    ind1, ind2 = creator.Ind(
        [0.03, 1, 1, 1, 1]), creator.Ind([0.03, 1, 1, 1, 1])
    ind1.gen, ind1.num = 0, 0
    ind2.gen, ind2.num = 0, 1
    pop = [ind1, ind2]
    output_vals = eval_function(pop)
    print(output_vals)
    expected_output_vals = [tuple([0.03, output_vals[0][1], 1000, 10]), tuple([
        0.03, output_vals[1][1], 1000, 10])]
    print(expected_output_vals)
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./moltres_0_0")
    shutil.rmtree("./openmc_0_1")
    shutil.rmtree("./moltres_0_1")
    os.chdir("../")
    assert output_vals == expected_output_vals
    return


def test_create_input_execute_output_scripts():
    init()
    os.chdir("./input_test_files")
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc", input_script=[
            "python", "input_test_run_input_script.py"], output_script=[
            "python", "input_test_create_input_execute_output_scripts.py"], )
    control_vars_dict = {
        "0_0": {"openmc": {"hi": 1, "hi2": 2}},
        "0_1": {"openmc": {"hi": 3, "hi2": 4}}
    }
    ind1, ind2 = creator.Ind([1]), creator.Ind([2])
    ind1.gen, ind1.num = 0, 0
    ind2.gen, ind2.num = 0, 1
    pop = [ind1, ind2]
    input_evaluators_solver = {"execute": [
        ["python", "input_test_run_execute.py"],
        ["rollo-non-existent-executable"]]}
    ev.create_input_execute_output_scripts(
        pop=pop,
        solver="openmc",
        control_vars_dict=control_vars_dict,
        input_evaluators_solver=input_evaluators_solver)
    with open("./openmc_0_0/input_test_run_input_script.py") as fp:
        Lines = fp.readline()
    assert Lines == "print([1, 2])"
    with open("./openmc_0_1/input_test_run_input_script.py") as fp:
        Lines = fp.readline()
    assert Lines == "print([3, 4])"
    with open("./openmc_0_0/input_test_run_execute.py") as fp:
        Lines = fp.readline()
    assert Lines == "print([5, 6])\n"
    with open("./openmc_0_1/input_test_run_execute.py") as fp:
        Lines = fp.readline()
    assert Lines == "print([5, 6])\n"
    with open("./openmc_0_0/input_test_create_input_execute_output_scripts.py") as fp:
        Lines = fp.readline()
    assert Lines == 'print({"random": 3})\n'
    with open("./openmc_0_1/input_test_create_input_execute_output_scripts.py") as fp:
        Lines = fp.readline()
    assert Lines == 'print({"random": 3})\n'
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./openmc_0_1")
    os.chdir("../")
    return


def test_run_input_and_execute_and_output_scripts():
    init()
    os.chdir("./input_test_files")
    control_vars_dict = {
        "0_0": {"openmc": {"hi": 1, "hi2": 2}},
        "0_1": {"openmc": {"hi": 3, "hi2": 4}}
    }
    ind1, ind2 = creator.Ind([1]), creator.Ind([2])
    ind1.gen, ind1.num = 0, 0
    ind2.gen, ind2.num = 0, 1
    pop = [ind1, ind2]
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc", input_script=[
            "python", "input_test_run_input_script.py"], output_script=[
            "python", "input_test_create_input_execute_output_scripts.py"], )
    input_evaluators_solver = {"execute": [
        ["python", "input_test_run_execute.py"],
        ["rollo-non-existent-executable"]]}
    ev.create_input_execute_output_scripts(
        pop=pop,
        solver="openmc",
        control_vars_dict=control_vars_dict,
        input_evaluators_solver=input_evaluators_solver)
    ev.run_input_and_execute_and_output_scripts(
        pop=pop,
        solver="openmc",
        input_evaluators_solver=input_evaluators_solver
    )
    with open("./openmc_0_0/input_script_out.txt") as fp:
        Lines = fp.readlines()[0]
    assert Lines == "[1, 2]\n"
    with open("./openmc_0_1/input_script_out.txt") as fp:
        Lines = fp.readlines()[0]
    assert Lines == "[3, 4]\n"
    with open("./openmc_0_0/execute_0_out.txt") as fp:
        Lines = fp.readlines()[0]
    assert Lines == "[5, 6]\n"
    with open("./openmc_0_1/execute_0_out.txt") as fp:
        Lines = fp.readlines()[0]
    assert Lines == "[5, 6]\n"
    with open("./openmc_0_0/execute_1_out.txt") as fp:
        Lines = fp.readlines()[0]
    assert "not found" and "rollo-non-existent-executable" in Lines
    with open("./openmc_0_1/execute_1_out.txt") as fp:
        Lines = fp.readlines()[0]
    assert "not found" and "rollo-non-existent-executable" in Lines
    with open("./openmc_0_0/output_script_out.txt") as fp:
        Lines = fp.readline()
    assert Lines == "{'random': 3}\n"
    with open("./openmc_0_1/output_script_out.txt") as fp:
        Lines = fp.readline()
    assert Lines == "{'random': 3}\n"
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./openmc_0_1")
    os.chdir("../")
    return


def test_generate_run_command_job_control():
    init()
    ind1, ind2 = creator.Ind([1]), creator.Ind([2])
    ind1.gen, ind1.num = 0, 0
    ind2.gen, ind2.num = 0, 1
    pop = [ind1, ind2]
    ev = Evaluation()
    command = ev.generate_run_command_job_control(
        pop, "openmc", "python hello.py")
    expected_command = "cd openmc_0_0\npython hello.py & \nsleep 1 \n" + \
        "cd ../openmc_0_1\npython hello.py & \nsleep 1 \nwait"
    assert command == expected_command
    return


def test_get_output_vals_job_control():
    init()
    ind1, ind2 = creator.Ind([1]), creator.Ind([2])
    ind1.gen, ind1.num = 0, 0
    ind2.gen, ind2.num = 0, 1
    pop = [ind1, ind2]
    ev = Evaluation()
    os.chdir("./input_test_files")
    ev.add_evaluator(
        solver_name="openmc", input_script=[
            "python", "input_test_run_input_script.py"], output_script=[
            "python", "input_test_create_input_execute_output_scripts.py"], )
    output_vals_dict = OrderedDict()
    control_vars_dict = {
        "0_0": {"openmc": {"hi": 1, "hi2": 2}},
        "0_1": {"openmc": {"hi": 3, "hi2": 4}}
    }
    output_vals_dict["0_0"] = [None] * 2
    output_vals_dict["0_1"] = [None] * 2
    input_evaluators_solver = {}
    ev.create_input_execute_output_scripts(
        pop=pop,
        solver="openmc",
        control_vars_dict=control_vars_dict,
        input_evaluators_solver=input_evaluators_solver)
    ev.run_input_and_execute_and_output_scripts(
        pop=pop,
        solver="openmc",
        input_evaluators_solver=input_evaluators_solver
    )
    all_output_vals = ev.get_output_vals_job_control(
        output_vals_dict=output_vals_dict,
        pop=pop,
        solver="openmc",
        output_dict=OrderedDict(
            {
                "hi": "openmc",
                "random": "openmc",
            }
        ),
        control_vars_dict=control_vars_dict)
    expected_output_vals = [tuple([1, 3]), tuple([3, 3])]
    assert all_output_vals == expected_output_vals
    shutil.rmtree("./openmc_0_0")
    shutil.rmtree("./openmc_0_1")
    os.chdir("../")
    return


def test_run_input_script_serial():
    os.chdir("./input_test_files")
    path = "openmc_0_0"
    os.mkdir(path)
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc",
        input_script=["python", "input_test_run_input_script.py"],
        output_script=["python", "placeholder.py"],
    )
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    ind = creator.Ind([1, 1])
    ind.gen = 0
    ind.num = 0
    control_vars_solver = {"hi": 1, "hi2": 2}
    ev.run_input_script_serial("openmc", control_vars_solver, ind, path)
    with open("./" + path + "/input_script_out.txt") as fp:
        Lines = fp.readlines()[0]
    assert Lines == "[1, 2]\n"
    shutil.rmtree(path)
    os.chdir("../")
    return


def test_run_execute_serial():
    os.chdir("./input_test_files")
    path = "openmc_0_0"
    os.mkdir(path)
    ev = Evaluation()
    ev.run_execute_serial([["python", "input_test_run_execute.py"], [
        "rollo-non-existent-executable"]], path, "openmc")
    with open("./" + path + "/execute_0_output.txt") as fp:
        Lines = fp.readlines()[0]
    assert Lines == "[5, 6]\n"
    with open("./" + path + "/execute_1_output.txt") as fp:
        Lines = fp.readlines()[0]
    assert "not found" and "rollo-non-existent-executable" in Lines
    shutil.rmtree(path)
    os.chdir("../")
    return


def test_solver_order():
    input_evaluators = {"openmc": {"order": 0}, "moltres": {"order": 1}}
    ev = Evaluation()
    order = ev.solver_order(input_evaluators)
    assert order == ["openmc", "moltres"]
    return


def test_run_output_script_serial():
    os.chdir("./input_test_files")
    ev = Evaluation()
    ev.add_evaluator(
        solver_name="openmc",
        input_script=["python", "placeholder.py"],
        output_script=["python", "input_test_evaluation_get_output_vals.py"],
    )
    output_vals = ev.run_output_script_serial(
        output_vals=[None] * 4,
        solver="openmc",
        output_dict=OrderedDict(
            {
                "packing_fraction": "openmc",
                "keff": "openmc",
                "max_temp": "moltres",
                "random": "openmc",
            }
        ),
        control_vars={
            "openmc": {"packing_fraction": 0.03},
            "moltres": {"polynomial_triso": [1, 1, 1, 1]},
        },
        path="./test_evaluation/",
    )
    expected_output_vals = [0.03, 1.6331797843041689, None, 3]
    os.remove("./test_evaluation/output_script_out.txt")
    os.remove("./test_evaluation/input_test_evaluation_get_output_vals.py")
    os.chdir("../")
    assert output_vals == expected_output_vals


def test_name_ind():
    ev = Evaluation()
    control_vars = ev.name_ind(
        ind=[0.01, 1, 1, 1, 1],
        control_dict=OrderedDict(
            {"packing_fraction": ["openmc", 1],
                "polynomial_triso": ["moltres", 4]}
        ),
        input_evaluators=["openmc", "moltres"],
    )
    expected_control_vars = {
        "openmc": {"packing_fraction": 0.01},
        "moltres": {"polynomial_triso": [1, 1, 1, 1]},
    }
    assert control_vars == expected_control_vars


def test_render_jinja_template():
    os.chdir("./input_test_files")
    ev = Evaluation()
    rendered_template = ev.render_jinja_template(
        script="./input_test_render_jinja_template_python.py",
        control_vars_solver={
            "packing_fraction": 0.01,
            "polynomial_triso": [1, 1, 1, 1],
        },
        ind=1,
        solver="openmc"
    )
    print(rendered_template)
    expected_rendered_template = "total_pf = 0.01\npoly_coeff = [1, 1, 1, 1]"
    os.chdir("../")
    assert rendered_template == expected_rendered_template
