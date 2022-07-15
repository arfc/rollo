.. _parallel_rollo:

.. image:: ../pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

*************************
Running ROLLO in Parallel
*************************
**ROLLO** has a serial run mode and two modes for parallelization:

* serial (none)
* multiprocessing 
* job_control

Serial (none)
=============
The serial run mode runs each reactor model in each generation in series. 
The serial run mode utilizes a `map()` function to run the nuclear software for each 
reactor model.

Multiprocessing 
===============
The multiprocessing mode replaces the default `map()` function with the 
`multiprocessing_on_dill <https://pypi.org/project/multiprocessing_on_dill/>`_ map.
The `multiprocessing_on_dill` map chops the iterable into several chunks which it 
submits to the process pool as separate tasks. This multiprocessing mode is useful 
for parallelizing runs on a local machine or a single node on a computer cluster. 
However, it is unable to parallelize across distributed memory systems.

Job Control 
===========
The job control mode utilizes the Unix system's job control features to give users 
more flexibility with parallelization setup. This flexibility enables parallelization 
across distributed memory systems such as clusters and supercomputers.
This mode does not use the `map()` function. 
**ROLLO** generates a combined bash command that launches multiple 
evaluation function calls for the different reactor models by backgrounding each 
command. For example, a **ROLLO** simulation with a population size of 2 generates a 
combined command that looks like this:

.. code-block:: bash

    cd 0_0
    aprun -n 2 python program1.py &
    sleep 1
    cd ../0_1
    aprun -n 2 python program1.py &
    sleep 1
    wait

Users define evaluator script's executables in **ROLLO**'s input file; thus, the 
job control mode enables more control over the parallelization settings of each 
command. Many nuclear software, such as 
`OpenMC <https://docs.openmc.org/en/stable/>`_ and 
`MOOSE <https://moose.inl.gov/SitePages/Home.aspx>`_, use Message Passing Interface 
(MPI) or OpenMP to parallelize their runs. Since **ROLLO** uses job control to 
parallelize the runs, there is no clash with parallelization methods of the nuclear 
software. With control over each executable, users 
can continue to utilize the parallel versions of the nuclear software, thus, having 
two layers of parallelization. The first layer is the individual software's 
parallelization, and the second layer is **ROLLO**'s parallelization. For example, 
running 4 reactor models using **ROLLO** across 16 nodes on a cluster and assigning 
each reactor model to run in parallel across 4 nodes.