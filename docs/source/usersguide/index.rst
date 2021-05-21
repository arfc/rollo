.. _usersguide:

============
User's Guide
============
Welcome to the **ROLLO** User's Guide! This tutorial will guide you through the essential aspects of using **ROLLO** to perform simulations.

--------------------------
Running a ROLLO Simulation
--------------------------

When you build and install **ROLLO**, you will have a **ROLLO** executable in your system. 
To run a **ROLLO** simulation, you put this into the command line: 

.. code-block:: sh
  
  python -m rollo -i <input file> -c <checkpoint file>
  
.. list-table::
   :widths: 25 25 50
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
     
The checkpoint file holds the results from the ROLLO simulation and also acts 
as a restart file. Thus, if a ROLLO simulation ends prematurely, the checkpoint 
file can be used to restart the code from the most recent population and 
continue the simulation. The checkpoint file will be described further in the 
## INSERT SECTION ##

