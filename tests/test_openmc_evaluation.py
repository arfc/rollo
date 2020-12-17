import pytest
import os
import openmc
from realm.openmc_evaluation import OpenMCEvaluation


def test_evaluate_keff():

    oe = OpenMCEvaluation()
    os.chdir("./input_test_files")
    keff = oe.evaluate_keff()
    expected_keff = 1.6331797843041689
    os.chdir("../")
    assert keff == expected_keff
