import random
import numpy as np


class SpecialVariables:
    """A class to hold special developer-defined variables

    Attributes
    ----------
    special_variables : list
        names of special variables

    """

    def __init__(self):
        # developer's should add to this list when defining a new special
        # variable
        self.special_variables = ["polynomial_triso"]
        return

    def polynomial_triso_num(self, poly_dict):
        """Returns number of variables

        Returns
        -------
        int
            number of control variables in polynomial_triso special variable
        """

        return poly_dict["order"] + 1

    def polynomial_triso_values(self, poly_dict, var_dict):
        """Returns a list of polynomial coefficients

        Parameters
        ----------
        poly_dict : dict
            polynomial_triso sub-dictionary from input file
        var_dict : dict
            control variable sub-dictionary from input file

        Returns
        -------
        list
            list of polynomial coefficients

        """

        total_pf = var_dict["packing_fraction"]
        dz = poly_dict["slices"]
        vol_total = poly_dict["volume"]
        dz_vals = np.linspace(0, poly_dict["height"], dz)
        vol_triso = 4 / 3 * np.pi * poly_dict["radius"] ** 3
        no_trisos = total_pf * vol_total / vol_triso
        poly_val_under_zero = [1.0] * dz
        pf_z_over_max = [1.0] * dz
        while (len(poly_val_under_zero) > 0) or (len(pf_z_over_max) > 0):
            poly = []
            for i in range(poly_dict["order"] + 1):
                poly.append(random.uniform(poly_dict["min"], poly_dict["max"]))
            poly_val = np.array([0.0] * dz)
            for i in range(poly_dict["order"] + 1):
                poly_val += poly[i] * dz_vals ** (poly_dict["order"] - i)
            pf_z = poly_val / sum(poly_val) * no_trisos * vol_triso / vol_total
            pf_z_over_max = [i for i in pf_z if i > 0.25]
            poly_val_under_zero = [i for i in poly_val if i < 0]
        return poly
