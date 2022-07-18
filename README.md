# ROLLO (Reactor evOLutionary aLgorithm Optimizer)

[![PyPI version](https://badge.fury.io/py/rollo.svg)](https://badge.fury.io/py/rollo)
[![CI](https://github.com/arfc/rollo/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/arfc/rollo/actions/workflows/python-package-conda.yml)

ROLLO is an open-source Python package that applies evolutionary algorithm 
techniques to optimize nuclear reactor design. It essentially couples the `DEAP (Distributed Evolutionary Algorithms in Python) 
<https://deap.readthedocs.io/en/master/>`_ evolutionary algorithm driver with 
nuclear software.
ROLLO is nuclear-software agnostic, and designed to easily couple to any software. 

Documentation on the usage of ROLLO is hosted at: https://gwenchee.github.io/rollo/

## Installation 
`python -m pip install rollo`

The more detailed installation guide can be found [here](https://gwenchee.github.io/rollo/install.html).

## Running ROLLO 
`python -m rollo -i <input file> -c <checkpoint file> -v `

Command line flags: 
| Flag | Description | Mandatory ? |
| ----------- | ----------- | ----------- |
| -i | name of input file | Yes |
| -c| name of checkpoint file | No |
| -v| verbose output (only include the flag) | No |

Details about running ROLLO can be found in the users guide [here](https://gwenchee.github.io/rollo/usersguide/run_rollo.html).

## Citing 
TODO: Add ROLLO paper when completed. 

## Troubleshooting
If you run into problems compiling, installing, or running ROLLO, please post to the 
[discussion forum](https://github.com/arfc/rollo/discussions).