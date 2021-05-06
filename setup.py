import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gwenchee",
    version="0.0.1",
    author="Gwendolyn J.Y. Chee",
    author_email="gwendolynchee95@gmail.com",
    description="Generative Reactor Designs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arfc/rollo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
