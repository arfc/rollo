import glob, openmc


class OpenMCEvaluation:
    """This class holds functions to evaluate openmc output files.
    - To add new openmc outputs, create a function called "evaluate_###" and
    input ### name as a str into the pre_defined_output list.

    Attributes
    ----------
    pre_defined_outputs : list
        list of variables names with evaluation functions in this class

    """

    def __init__(self):
        self.pre_defined_outputs = ["keff"]

    def evaluate_keff(self):
        """This function analyzes the openmc output file and returns keff value

        Returns
        -------
        float
            keff value

        """
        for file in glob.glob("statepoint*"):
            h5file = file
        sp = openmc.StatePoint(h5file, autolink=False)
        keff = sp.k_combined.nominal_value
        return keff
