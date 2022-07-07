.. _setup_rollo:

.. image:: ../pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

======================
ROLLO Input File Setup
======================

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
For example, in traditional reactor design, a control variable might be fuel 
enrichment. 

^^^^^^^^^^
Evaluators
^^^^^^^^^^
Evaluators are the nuclear software **ROLLO** utilizes to calculate the objective 
and constraint values. 
**ROLLO** is nuclear-software agnostic, and does not have any nuclear software 
dependencies. 
Thus the user may use any nuclear software as an evaluator, and it is also up to the 
user to ensure that the nuclear software and their corresponding executables are 
correctly installed. 
In a **ROLLO** input file, a user may define any number of evaluators.

For each evaluator, there are mandatory and optional input parameters. 
These input parameters are outlined in the following table: 

.. list-table::
   :widths: 25 25 30 20
   :header-rows: 1

   * - Input Parameter
     - Type
     - Description
     - Mandatory?
   * - ``order``
     - int
     - evaluator's operational order compared to other evaluators (indexed by 0)
     - yes
   * - ``inputs``
     - list of str
     - control variables to be placed into the input file template
     - yes
   * - ``input_script``
     - 2-element list (containing str)
     - 1st element: executable to run input script, 
       2nd element: input script template 
     - yes
   * - ``outputs``
     - list of str
     - output variables that the evaluator will return to the genetic algorithm
     - yes
   * - ``output_script``
     - 2-element list (containing str)
     - 1st element: executable to run output script, 
       2nd element: output script template 
     - no
   * - ``execute``
     - list of 2-element lists (containing str)
     - enables users to run other executables or files beyond the input and output 
       scripts. 
       1st element: executable to run file, 
       2nd element: file to run
     - no

The `evaluators` section of the **ROLLO** input file should look something like this: 

.. code-block:: JSON

  "evaluators": {
    "evaluator_1": { 
      "order": 0,
      "inputs": ["variable1", "variable2"],
      "input_script": ["python", "input_script.py"],
      "execute": [["exe1", "exe1_inp.py"], ["exe2", "exe2_inp.py"]],
      "outputs": ["output1", "output2"],
      "output_script": ["python", "output_script.py"],
      "keep_files": all,
      }
    } 

**ROLLO** utilizes `Jinja2 <https://jinja2docs.readthedocs.io/en/stable/>`_ 
templating to insert control variables values into the ``input_script``. 
Users must include each evaluator's input file template in the same directory as 
the ROLLO input file. 
Users must also ensure the template variables correspond to the inputs defined in 
the corresponding evaluator's section in the ROLLO input file. 

The following code snippets show the template and templated input scripts; 
once the ``input_script`` is templated, {{variable1}} and {{variable2}} on Lines 3 and 
4 will be replaced with values selected by **ROLLO**'s genetic algorithm. 

+---------------------------+---------------------------+
|       Template            |   Templated               |
|.. code-block::            |.. code-block::            |
|                           |                           |
| variable1 = {{variable1}  | variable1 = 3.212         |     
| variable1 = {{variable1}  | variable1 = -0.765        |     
+---------------------------+---------------------------+


**ROLLO** uses two methods to return an output variable to the genetic algorithm. 
First, **ROLLO** will automatically return the input parameter's value if the 
output parameter is also an input parameter. 
Second, the user may include an output script that returns the desired output 
parameter. 
The output script must include a line that prints a dictionary containing the 
output parameters' names and their corresponding value as key-value pairs: 

.. code-block:: Python

  output1_val = # some logic 
  output2_val = # some logic 

  print({"output1":output1_val, "output2":output2_val})

^^^^^^^^^^^
Constraints
^^^^^^^^^^^
The user can define constraints on any output parameter. 
Any individual that does not meet the defined constraints is removed from the 
population, encouraging the proliferation of individuals that meet the constraints.
For each constrained parameter, the user lists the ``operator`` and ``constrained_val``. 

The `constraints` section of the **ROLLO** input file with two constraints should look 
something like this: 

.. code-block:: JSON

  "constraints": {
    "output1": {"operator": [">=", "<"], "constrained_val": [1.0, 1.5]},
    "output2": {"operator": ["<"], "constrained_val": [1000]}
      }

^^^^^^^^^^
Algorithm
^^^^^^^^^^

