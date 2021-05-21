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
     
The checkpoint file holds the results from the ROLLO simulation and also acts 
as a restart file. Thus, if a ROLLO simulation ends prematurely, the checkpoint 
file can be used to restart the code from the most recent population and 
continue the simulation. The checkpoint file will be described further in the 
## INSERT SECTION ##

-----------------------------
Setting up a ROLLO Input File
-----------------------------

The **ROLLO** input file is in `JSON <https://www.json.org/json-en.html>`_ format.
For each input file, the user must define four sections: `control_variables`, 
`evaluators`, `constraints`, and `algorithm`. 

^^^^^^^^^^^^^^^^^
Control Variables
^^^^^^^^^^^^^^^^^
Control variables are parameters the genetic algorithm will vary. For each control variable, the user must specify its minimum and maximum values. The `control_variables` section of the **ROLLO** input file should look something like this: 

.. code-block:: JSON

  "control_variables": { 
    "variable1": {"min": 0.0, "max": 10.0}, 
    "variable2": {"min": -1.0, "max": 0.0} 
  }

This demonstrates that control variables, ``variable1`` and ``variable2``, will be varied from
0 to 10 and -1 to 0, respectively.

^^^^^^^^^^
Evaluators
^^^^^^^^^^
Evaluators are the nuclear software **ROLLO** utilizes to calculate objective functions. Presently, only `OpenMC <https://openmc.org/>`_ and `Moltres <https://github.com/arfc/moltres/>`_ evaluators are available in ROLLO. In a single ROLLO input file, a user may define any number of evaluators.

For each evaluator, there are mandatory and optional input parameters. These input parameters are outlined in the following table: 

.. list-table::
   :widths: 25 25 15
   :header-rows: 1

   * - Input Parameter
     - Type
     - Description
     - Mandatory?
   * - ``input_script``
     - str
     - input file template's name for the evaluator software
     - yes
   * - ``inputs``
     - list of str
     - control variables to be placed into the input file template
     - yes

