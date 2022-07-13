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
     - name of checkpoint restart file
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

ROLLO Execution
===============
Users will define the **ROLLO** genetic algorithm's number of ``generations`` and 
``population size`` (more description in :ref:`input file algorithm section 
<algorithm>`).
During each generation's run, **ROLLO** will create ``population size`` number of 
sub-directories which contain all the evaluator's evaluation files. 
The sub-directories are indexed by generation number and individual number; 
for generation 3 and individual 5, the directory will be named: ``3_5``. 

The individual refers to each reactor model. 
In each individual's directory, 

ROLLO Terminal Outputs 
======================
After each ROLLO generation runs, ROLLO will output the following table with details about 
that generation's run. 

.. code-block:: sh

                                oup                             	   ind                                           
                   -------------------------------  ----------------------------------------
  time  gen evals  avg     std     min     max      avg           min            max                      
  73.4  0   100    [19.8]  [3.01]  [4.47]  [22.1]   [1.81 -3.97]  [-32.6 -32.0]  [32.1 32.3]

The table below describes each section of the above outputted table: 

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Heading
     - Description
   * - time
     - Total time taken to run generation in seconds 
   * - gen
     - Generation #    
   * - evals
     - Total number of individuals evaluated (<= population size defined in input file) 
   * - oup 
     - average, standard deviation, minimum value, maximum value of output parameters (objective and constraint values)
   * - ind 
     - average, minimum value, maximum value of input parameters (control variables)