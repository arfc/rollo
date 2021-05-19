# ROLLO (Reactor evOLutionary aLgorithm Optimizer)

ROLLO is a Python package that applies evolutionary algorithm techniques to optimize nuclear reactor design.

Documentation on the usage of ROLLO is hosted at: ## INSERT WEBSITE ##

## Installation 
`python -m pip install rollo`

## Running ROLLO 
`python -m rollo -i <input file> -c <checkpoint file>`

Command line flags: 
| Flag | Description | Mandatory ? |
| ----------- | ----------- | ----------- |
| -i | name of input file | Yes |
| -c| name of checkpoint file | No |


## To build documentation 
`cd docs` 

`make html`

## To upload to PyPI
`python3 -m build`

`python3 -m twine upload dist/*`

## License 
ROLLO is distributed under the 3-Clause BSD License.
