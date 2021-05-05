import glob
import openmc


class OpenMCEvaluation:
    """This class evaluates openmc output files.
    - To add new openmc outputs, create a function called "output_***" and
    input *** name as a str into the openmc_output list.
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
