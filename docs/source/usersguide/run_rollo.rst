.. _run_rollo:

.. image:: ../pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

==========================
Running a ROLLO Simulation
==========================

After you build and install **ROLLO**, you will have a **ROLLO** executable in your 
system. 
To run a **ROLLO** simulation, enter these commands in a terminal:  

.. code-block:: sh
  
  python -m rollo -i <input file> -c <checkpoint file> -v
  
.. list-table::
   :widths: 10 25 15
   :header-rows: 1

   * - Flag
     - Description
     - Mandatory?
   * - -i
     - name of input file
     - yes
   * - -c
     - name of checkpoint file
     - no
   * - -v
     - turns on verbose output (only include the flag)
     - no 
     
The checkpoint file holds the results from the **ROLLO** simulation. 
**ROLLO** automatically generates/updates a checkpoint file (``checkpoint.pkl``)
after each generation. 
The checkpoint file also acts as a restart file.
If a **ROLLO** simulation ends prematurely, the checkpoint 
file can be used to restart the code from the most recent generation and 
continue the simulation. Further description can be found in the
:ref:`checkpoint file section <checkpoint_rollo>`.

