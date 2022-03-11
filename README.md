[![PyPI version](https://badge.fury.io/py/rollo.svg)](https://badge.fury.io/py/rollo)
[![CI](https://github.com/arfc/rollo/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/arfc/rollo/actions/workflows/python-package-conda.yml)

# ROLLO (Reactor evOLutionary aLgorithm Optimizer)

ROLLO is a Python package that applies evolutionary algorithm techniques to optimize nuclear reactor design.

Documentation on the usage of ROLLO is hosted at: https://gwenchee.github.io/rollo/

## Installation 
`python -m pip install rollo`

## Running ROLLO 
`python -m rollo -i <input file> -c <checkpoint file> -v `

Command line flags: 
| Flag | Description | Mandatory ? |
| ----------- | ----------- | ----------- |
| -i | name of input file | Yes |
| -c| name of checkpoint file | No |
| -v| verbrose output (only include the flag) | No |

The checkpoint file holds the results from the ROLLO simulation and also acts 
as a restart file. Thus, if a ROLLO simulation ends prematurely, the checkpoint 
file can be used to restart the code from the most recent population and 
continue the simulation.

The verbrose flag (-v) enables ROLLO to output extra information for the user. 

## To build documentation 
`cd docs` 

`make html`

## To upload to PyPI
`python3 -m build`

`python3 -m twine upload dist/*`

## License 
ROLLO is distributed under the 3-Clause BSD License.
