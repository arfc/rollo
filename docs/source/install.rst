.. _install:

===================
Install Guide
===================

The install guide outlines the steps to install **ROLLO** on your computer. 

------------
Dependencies
------------

These are the **ROLLO** dependencies. Most are installed with the **ROLLO** PyPI install below. 

1) `DEAP (Distributed Evolutionary Algorithms in Python) <https://deap.readthedocs.io/en/master/>`_:

2) `Numpy <https://numpy.org/>`_

3) `JSON Schema <https://json-schema.org/>`_

4) `Jinja2 <https://jinja2docs.readthedocs.io/en/stable/>`_

5) `Multiprocessing on Dill <https://pypi.org/project/multiprocessing_on_dill/>`_

Users must manually install `OpenMC <https://openmc.org/>`_

.. code-block:: sh
  
  conda install -c conda-forge openmc

----------------------------
ROLLO Installation with PyPI
----------------------------
.. code-block:: sh
  
  python -m pip install rollo

---------------------
ROLLO Parallelization
---------------------
Users that want to use `mpi_evals` supercomputer parallelization option (described in ## INSERT ##)
must install `mpi4py <https://mpi4py.readthedocs.io/en/1.3.1/index.html>`_. Follow your supercomputer/cluster's 
``mpi4py`` installation process.



