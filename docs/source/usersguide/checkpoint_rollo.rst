.. _checkpoint_rollo:

.. image:: ../pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

======================
ROLLO Checkpoint File
======================

The checkpoint file is a `serialized pickle file <https://docs.python.org/3/library/pickle.html>`_. 

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
   :widths: 25 25 25
   :header-rows: 1

   * - Checkpoint File Key 
     - Description
     - Type
   * - ``input_file``
     - a copy of the input file 
     - str





