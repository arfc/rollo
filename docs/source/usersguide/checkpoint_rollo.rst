.. _checkpoint_rollo:

.. image:: ../pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

======================
ROLLO Checkpoint File
======================

The checkpoint file is a `serialized pickle file 
<https://docs.python.org/3/library/pickle.html>`_ and is based on the `DEAP 
checkpointing system <https://deap.readthedocs.io/en/master/tutorials/advanced/checkpoint.html?highlight=rndstate#checkpointing>`_. 

The checkpoint file holds the **ROLLO** simulation results and acts as a restart 
file.

Restarting Simulation
=====================
The checkpoint file updates after each generation runs successfully. 
If the **ROLLO** simulation fails during a generation, the user can
restart the simulation from the previous generation. 
Therefore, if you're running a **ROLLO** simulation with 10 generations and it fails 
during generation 3, you can restart the **ROLLO** simulation from generation 2. 

This capability can also be used for running one generation at a time. For example, 
you're running a large optimization simulation across many nodes on a 
supercomputer, and don't want to waste compute time if the simulation fails part way 
through. You can run one generation at a time, increasing the number of generations 
defined in the input file with each run. 

Results Analysis
================

To un-pickle the data and analyze the results: 

.. code-block:: Python 

    import pickle
    checkpoint_file="checkpoint.pkl"
    with open(checkpoint_file, "rb") as cp_file:
      cp = pickle.load(cp_file)

Once loaded into Python, the checkpoint file is a dict. 
The following table describes the keys in the checkpoint file: 

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Checkpoint File Key 
     - Description
   * - ``input_file``
     - a copy of the input file 
   * - ``evaluator_files``
     - a dict with copies of the evaluators' scripts 
   * - ``population`` 
     - the final population (list of reactor model individuals)
   * - ``generation``
     - number of generations (int)
   * - ``hall of fame``
     - deap.tools.HallOfFame object (`see deap documentation <https://deap.readthedocs.io/en/master/api/tools.html#deap.tools.HallOfFame>`_)
   * - ``logbook``
     - deap.tools.Logbook object (`see deap documentation <https://deap.readthedocs.io/en/master/api/tools.html#logbook>`_)
   * - ``rndstate`` 
     -  simulation's random state (used when restarting simulation)
   * - ``all`` [``ind_naming``]
     - dict, key: input parameter name, value: index, corresponds to each individual's input parameter index in ``all`` [``populations``] 
   * - ``all`` [``oup_naming``]
     - dict, key: output parameter name, value: index, corresponds to each individual's output parameter index in ``all`` [``outputs``] 
   * - ``all`` [``populations``]
     - list of populations, each population list contains a list of reactor models individuals
   * - ``all`` [``outputs``]
     - list of population outputs, each population list contains a list of reactor model individual's output parameters

Each reactor model individual is an :class:`Ind` class type with attributes and is a simple 
list (`DEAP Individual class <https://deap.readthedocs.io/en/master/tutorials/basic/part1.html#individual>`_).
The following code snippet demonstrates a reactor model individual's attributes: 

.. code-cell:: Python
    :execution-count: 1

    ind1 = cp["all"]["populations"][0][0]
    print(ind1)

.. output-cell::
    :execution-count: 1

    [7.930883654471881]

.. code-cell:: Python
    :execution-count: 2

    print(ind1.__dict__)

.. output-cell::
    :execution-count: 2
    
    {'fitness': deap.creator.obj((-7.930883654471881,)),
    'gen': 0, 
    'num': 0, 
    'output': (7.930883654471881, 1.4598642651422447)}

Descriptions of the reactor model individual's attributes: 

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Attribute 
     - Description
   * - ``fitness``
     - fitness tuple holds the objective values. The sign refers to whether the objective is to maximize or minimize. 
   * - ``gen``
     - generation 
   * - ``num``
     - reactor model index in generation
   * - ``output`` 
     - tuple of reactor model individual output parameters

Examples of how to analyze ROLLO results can be found in the `Example Notebooks
<https://github.com/arfc/rollo/wiki/Example-Jupyter-Notebooks/>`_.


