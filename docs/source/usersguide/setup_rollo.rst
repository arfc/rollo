.. _setup_rollo:

.. image:: ../pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

======================
ROLLO Input File Setup
======================

The **ROLLO** input file is in `JSON <https://www.json.org/json-en.html>`_ format.
For each input file, the user must define four sections: 

- :ref:`Control Variables <control_variables>`
- :ref:`Evaluators <evaluators>`
- :ref:`Constraints <constraints>`
- :ref:`Algorithm <algorithm>`

.. _control_variables:

Control Variables
=================
Control variables are parameters the genetic algorithm will vary. 
For each control variable, the user must specify its minimum and maximum values. 
The user may define any number of control variables. 
The `control_variables` section of the **ROLLO** input file looks 
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

Variable names must be strings. 
The following table describes each variable's input parameter sub-requirements: 

.. list-table::
   :widths: 25 25 30 20
   :header-rows: 1

   * - Input Parameter
     - Type
     - Description
     - Mandatory?
   * - ``min``
     - float
     - minimum value
     - yes
   * - ``max``
     - float
     - max value
     - yes

.. _evaluators:

Evaluators
==========
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

The `evaluators` section of the **ROLLO** input file looks like this: 

.. code-block:: JSON

  "evaluators": {
    "evaluator_1": { 
      "order": 0,
      "inputs": ["variable1", "variable2"],
      "input_script": ["python", "input_script.py"],
      "execute": [["exe1", "exe1_inp.py"], ["exe2", "exe2_inp.py"]],
      "outputs": ["output1", "output2"],
      "output_script": ["python", "output_script.py"]
      }
    } 

Evaluators: Input File Templating 
---------------------------------
**ROLLO** utilizes `Jinja2 <https://jinja2docs.readthedocs.io/en/stable/>`_ 
templating to insert control variables values into the ``input_script``. 
Users must include each evaluator's input file template in the same directory as 
the **ROLLO** input file. 
Users must also ensure the template variables correspond to the inputs defined in 
the corresponding evaluator's section in the **ROLLO** input file. 

The following code snippets show the template and templated input scripts; 
once the ``input_script`` is templated, {{variable1}} and {{variable2}} 
will be replaced with values selected by **ROLLO**'s genetic algorithm. 

+----------------------------+---------------------------+
|       Template             |   Templated               |
|.. code-block::             |.. code-block::            |
|                            |                           |
| variable1 = {{variable1}}  | variable1 = 3.212         |     
| variable1 = {{variable1}}  | variable1 = -0.765        |     
+----------------------------+---------------------------+

Evaluators: Returning Output Parameters 
---------------------------------------
**ROLLO** uses two methods to return an output variable to the genetic algorithm. 
First, **ROLLO** will automatically return the input parameter's value if the 
output parameter is also an input parameter. 
Second, the user may include an output script that returns the desired output 
parameter. 
The ``output_script`` must include a line that prints a dictionary containing the 
output parameters' names and their corresponding value as key-value pairs: 

.. code-block:: Python

  output1_val = # some logic 
  output2_val = # some logic 

  print({"output1":output1_val, "output2":output2_val})

.. _constraints:

Constraints
===========
The user can define constraints on any output parameter. 
Any individual that does not meet the defined constraints is removed from the 
population, encouraging the proliferation of individuals that meet the constraints.
For each constrained parameter, the user lists the ``operator`` and ``constrained_val``. 

The `constraints` section of the **ROLLO** input file with two constraints looks 
like this: 

.. code-block:: JSON

  "constraints": {
    "output1": {"operator": [">=", "<"], "constrained_val": [1.0, 1.5]},
    "output2": {"operator": ["<"], "constrained_val": [1000]}
      }

The constraints are 1.0 >= output1 > 1.5 and output2 < 1000. 

The following table describes each constrained variable's sub-requirements: 

.. list-table::
   :widths: 25 25 30 20
   :header-rows: 1

   * - Input Parameter
     - Type
     - Description
     - Mandatory?
   * - ``operator``
     - list of str
     - operators for constraint
     - yes
   * - ``constrained_val``
     - list of floats 
     - values to constrain (corresponds to operator list)
     - yes

.. _algorithm:

Algorithm
=========
In the algorithm section, users define the simulation's general settings and the genetic 
algorithm's hyperparameters. 
The algorithm section's input parameters are outlined in the following table: 

.. list-table::
   :widths: 20 20 20 20 20
   :header-rows: 1

   * - Input Parameter
     - Type
     - Description
     - Mandatory?
     - Default 
   * - ``optimized_variable``
     - list of str
     - variables to be optimized
     - yes
     - n/a
   * - ``objective``
     - list of str
     - string options include: min or max. each objective corresponds to a variable in ``optimized_variable``
     - yes
     - n/a
   * - ``pop_size``
     - int
     - population size
     - yes
     - n/a
   * - ``generations``
     - int
     - number of generations
     - yes
     - n/a
   * - ``parallel``
     - str
     - options include: none, multiprocessing, job control
     - yes
     - none
   * - ``keep_files``
     - str
     - options include: none, only_final, all
     - yes
     - none
   * - ``mutation_probability``
     - float
     - individual's mutation probability (must be between 0 and 1)
     - no
     - 0.23
   * - ``mating_probability``
     - float
     - individual's mating probability (must be between 0 and 1)
     - no
     - 0.47
   * - ``selection_operator``
     - dict
     - options described in sections below
     - no
     - {"operator": ”selTournament”, ”tournsize”: 5}
   * - ``mutation_operator``
     - dict
     - options described in sections below 
     - no
     - {"operator": "mutPolynomialBounded", "eta": 0.23, "indpb": 0.23}
   * - ``mating_operator``
     - dict
     - options described in sections below
     - no
     - {"operator": "cxBlend", "alpha": 0.46}

The following sub-sections describe the selection, mutation, and mating operators 
available and their corresponding hyperparameters. 

Selection Operators 
-------------------
There are three options for selection operator: ``selTournament``, ``selBest``, and 
``selNSGA2``. 
In tournament selection (``selTournament``), a user-defined number of individuals 
play in a tournament, and the best individual proceeds to the next population. 
The tournament repeats until all the population's spots are filled. 
In best selection (``selBest``), the operator selects a user-defined number of 
best individuals, and copies are made to keep the population size constant. 
In NSGA-II selection (``selNSGA2``), the elitist operator selects the best individuals
from the combination of parent and offspring populations. 
NSGA-II selection works well for multi-objective optimization.

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1

   * - Selection Operators
     - Hyperparameters
     - Description
     - Type
   * - ``selTournament``
     - ``tournsize``
     - no. of individuals in each tournament
     - int
   * - ``selBest``
     - n/a
     - n/a
     - n/a
   * - ``selNSGA2``
     - n/a
     - n/a
     - n/a

Mutation Operators 
-------------------

There is one option for mutation operator: ``mutPolynomialBounded``. 
Polynomial bounded mutation (``mutPolynomialBounded``) mutates each individual 
based on a polynomial distribution. 
The user also defines the crowding degree of the mutation, eta (a big eta will
produce a mutant resembling its parent, while a small eta will produce the opposite).

+-------------------------+-----------------+---------------------------------+------------------------+
| Mutation Operators      | Hyperparameters | Description                     | Type                   |
+=========================+=================+=================================+========================+
| ``mutPolynomialBounded``| ``eta``         | crowding degree of the mutation | float (btwn 0 and 1)   | 
|                         |                 |                                 |                        |
|                         | ``indpb``       | independent probability for each| float (btwn 0 and 1)   |      
|                         |                 | attribute to be mutated         |                        |
+-------------------------+-----------------+---------------------------------+------------------------+

Mating Operators 
----------------

There are three options for mating operators: ``cxOnePoint``, ``cxUniform``, and 
``cxBlend``.
In the single-point crossover (``cxOnePoint``), the operator randomly selects two 
individuals from the population and a site along the individual's definition.
For example, if the individual is a list, the operator randomly chooses an element 
in the list as the cross-site. Then, the attributes on the cross site's right side 
are exchanged between the two individuals, creating two new offspring individuals. 
In a uniform crossover (``cxUniform``), the user defines an independent exchange 
probability for each individual's attribute. 
In blend crossover (``cxBlend``), the operator creates two offspring (O) individuals 
based on a linear combination of two-parent (P) individuals using the following 
equations:

:math:`O_1 = P_1 - \alpha(P_1-P_2)`
:math:`O_2 = P_2 + \alpha(P_1-P_2)`

where: 

:math:`\alpha =` Extent of the interval in which the new values can be drawn 
for each attribute on both side of the parents' attributes (user-defined)

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1

   * - Mating Operators
     - Hyperparameters
     - Description
     - Type
   * - ``cxOnePoint``
     - n/a
     - n/a
     - n/a
   * - ``cxUniform``
     - ``indpb``
     - independent probability for each attribute to be exchanged
     - float (btwn 0 and 1) 
   * - ``cxBlend``
     - ``alpha``
     - Extent of the interval that the new values can be drawn for each attribute on both sides of the parents' attributes
     - float (btwn 0 and 1) 