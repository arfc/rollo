## rollo (Reactor evOLutionary aLgorithm Optimizer)
Repository to hold the framework and code to produce generative reactor designs.

python -m rollo -i <input file> -c <checkpoint file>

# To build documentation 
cd docs 
make html

# To install 
python -m pip install rollo

# To upload to PyPI
python3 -m build
python3 -m twine upload dist/*