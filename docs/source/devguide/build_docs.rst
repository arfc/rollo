.. _build_docs:

.. image:: ../pics/rollo-logo.png
  :width: 450
  :alt: rollo-logo

================================
How to Build ROLLO Documentation
================================

In order to build the documentation in the ``docs`` directory, you will need to have 
the Sphinx third-party Python package and several Sphinx extentions. 
The easiest way to install Sphinx and its extensions is via pip:

.. code-block:: sh

    pip install sphinx
    pip install nbsphinx
    pip install sphinx_rtd_theme
    pip install sphinx_book_theme
    pip install sphinx-toolbox --user
    pip install sphinx-jinja2-compat==0.2.0b1
    pip install sphinx-autoapi

To build the documentation as a webpage, go to ``docs`` and run: 

.. code-block:: sh

    make html

To build the documentation as a PDF, go to ``docs`` and run: 

.. code-block:: sh

    make latexpdf