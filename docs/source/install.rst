.. _install:

.. image:: pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

===================
Install Guide
===================

The install guide outlines the steps to install **ROLLO** on your computer. 

----------------------------
ROLLO Installation with PyPI
----------------------------
The Python Package Index (PyPI) is a repository of software for the Python 
programming language. Pip installing ROLLO is the most straightforward way to install 
it. 

.. code-block:: sh
  
  python -m pip install rollo

-----------------------------------------------
ROLLO Installation with from Source on Mac OS X
-----------------------------------------------
All ROLLO source code is hosted on `Github <https://github.com/arfc/rollo/>`_. 
To install ROLLO from source, enter these commands in a terminal: 

.. code-block:: sh

  git clone git@github.com:arfc/rollo.git
  cd rollo 
  python setup.py install --user

You must also install the following dependencies individually to successfully use 
ROLLO that is built from source. 

------------
Dependencies
------------

These are the **ROLLO** dependencies.

1) `DEAP (Distributed Evolutionary Algorithms in Python) <https://deap.readthedocs.io/en/master/>`_:

2) `Numpy <https://numpy.org/>`_

3) `JSON Schema <https://json-schema.org/>`_

4) `Jinja2 <https://jinja2docs.readthedocs.io/en/stable/>`_

5) `Multiprocessing on Dill <https://pypi.org/project/multiprocessing_on_dill/>`_


