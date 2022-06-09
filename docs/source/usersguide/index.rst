.. _usersguide:

============
User's Guide
============
Welcome to the **ROLLO** User's Guide! This tutorial will guide you through the 
essential aspects of using **ROLLO** to perform optimization simulations.

--------------------------
Running a ROLLO Simulation
--------------------------

When you build and install **ROLLO**, you will have a **ROLLO** executable in your 
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
Control variables are parameters the genetic algorithm will vary. 
For each control variable, the user must specify its minimum and maximum values. 
The user may define any number of control variables. 
The `control_variables` section of the **ROLLO** input file should look something 
like this: 

.. code-block:: JSON

  "control_variables": { 
    "variable1": {"min": 0.0, "max": 10.0}, 
    "variable2": {"min": -1.0, "max": 0.0} 
  }

This demonstrates that control variables, ``variable1`` and ``variable2``, will be 
varied from 0 to 10 and -1 to 0, respectively.

^^^^^^^^^^
Evaluators
^^^^^^^^^^
Evaluators are the nuclear software **ROLLO** utilizes to calculate objective functions. 
**ROLLO** is nuclear-software agnostic, thus the user may couple any nuclear software.  
In a single ROLLO input file, a user may define any number of evaluators.

For each evaluator, there are mandatory and optional input parameters. 
These input parameters are outlined in the following table: 

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1

   * - Input Parameter
     - Type
     - Description
     - Mandatory?
   * - ``order``
     - str
     - evaluator's operational order compared to other evaluators (indexed by 0)
     - yes
   * - ``inputs``
     - list of str
     - control variables to be placed into the input file template
     - yes
   * - ``input_script``
     - list of str (2 elements)
     - first element - executable to run input script, second element - input script template 
     - yes
   * - ``outputs``
     - list of str
     - output variables that the evaluator will return to the genetic algorithm
     - yes
   * - ``output_script``
     - list of str (2 elements)
      - first element - executable to run output script, second element - input output template 
     - no
   * - ``execute``
     - list of list of str
     - options 
     - no
   * - ``keep_files``
     - str
     - options 
     - no
     
The `evaluators` section of the **ROLLO** input file should look something like this: 

.. code-block:: JSON

  "evaluators": {
    "openmc": { 
      "input_script": "openmc_inp.py",
      "output_script": "openmc_output.py",
      "inputs": ["variable1", "variable2"],
      "outputs": ["output1", "output2"]
      }
    } 
