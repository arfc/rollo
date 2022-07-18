.. _motivation:

.. image:: pics/rollo-logo.png
  :width: 450
  :alt: Alternative text

===================
Motivation
===================
Previously, nuclear reactor designers individually customized available evolutionary algorithm 
packages for their reactor design optimization problems.
However, the evolutionary algorithm setup is highly customizable with an assortment of 
genetic algorithm designs and operators. 
A reactor designer unfamiliar with evolutionary algorithms will have to go through the 
cumbersome process of customizing a genetic algorithm for their needs and determine 
which operators and hyperparameters work best for their problem.
Furthermore, computing fitness values with nuclear software is computationally 
expensive, necessitating using supercomputers.
Reactor designers have to set up parallelization to use the genetic algorithm 
optimization with nuclear software.

The motivation for **ROLLO** is to provide a user-friendly tool that helps reactor designers use evolutionary algorithms for reactor design optimization.
**ROLLO** provides a general genetic algorithm framework, sets up parallelization for the 
user, and promotes usability with an input file that only exposes mandatory parameters.
**ROLLO** strives to be effective, flexible, open-source, parallel, reproducible, and usable:

- Effective: **ROLLO** is well documented, tested, and version-controlled on `Github <https://github.com/arfc/rollo/>`_. 
- Flexible: **ROLLO** is nuclear software agnostic. Users can vary any imaginable parameter with any nuclear software. **ROLLO** uses a templating method to edit the input file of the coupled software.
- Parallel: Users have two options for running **ROLLO** in parallel.
- Reproducible: Data from every **ROLLO** run saves into a unique `pickled file <https://docs.python.org/3/library/pickle.html>`_.