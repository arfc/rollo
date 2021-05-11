import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rollo",
    version="0.0.1",
    author="Gwendolyn J.Y. Chee",
    author_email="gwendolynchee95@gmail.com",
    description="Reactor Evolutionary Algorithm Optimizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arfc/rollo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
