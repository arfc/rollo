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
file. Thus, if a **ROLLO** simulation ends prematurely, users can use the checkpoint 
file to restart the code from the most recent population and continue the simulation.

Restarting Simulation
=====================
The checkpoint file updates after each generation runs successfully. 
If the **ROLLO** simulation fails half way through a generation, the user can
restart the simulation from the previous generation. 
Therefore, if you're running a ROLLO simulation with 10 generations and it fails 
during generation 3, you can restart the ROLLO simulation from generation 2. 

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
     - total number of generations (int)
   * - ``hall of fame``
     - deap.tools.HallOfFame object (`see deap documentation <https://deap.readthedocs.io/en/master/api/tools.html#deap.tools.HallOfFame>`_)
   * - ``logbook``
     - deap.tools.Logbook object (`see deap documentation <https://deap.readthedocs.io/en/master/api/tools.html#logbook>`_)
   * - ``rndstate`` 
     -  random state (used when restarting simulation)
   * - ``all`` [``ind_naming``]
     - dict, key input parameter name, value: index, corresponds to each individual's input parameter order in ``all`` [``populations``] 
   * - ``all`` [``oup_naming``]
     - dict, key output parameter name, value: index, corresponds to each individual's output parameter order in ``all`` [``outputs``] 
   * - ``all`` [``populations``]
     - list of populations, each population list contains a list of reactor models individuals
   * - ``all`` [``outputs``]
     - list of population outputs, each population list contains a list of reactor model individuals output parameters

Each reactor model individual is of xx type and has the following information in it... 


Examples of how to analyze ROLLO results can be found in the `Example Notebooks
<https://github.com/arfc/rollo/wiki/Example-Jupyter-Notebooks/>`_.


