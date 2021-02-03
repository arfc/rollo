import random
import numpy as np


class SpecialVariables:
    def __init__(self):
        # developer's should add to this list when defining a new special
        # variable
        self.special_variables = ["polynomial_triso", "sine"]
        return

    def polynomial_triso_num(self, poly_dict):
        return poly_dict["order"] + 1

    def polynomial_triso_values(self, poly_dict, var_dict):
        """Returns a list of polynomial coefficients"""
        """This function returns polynomial values"""
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

    def sine_num(self):
        return 4

    def sine_values(self, sine_dict, var_dict):
        a = random.uniform(sine_dict["a"][0], sine_dict["a"][1])
        b = random.uniform(sine_dict["b"][0], sine_dict["b"][1])
        c = random.uniform(sine_dict["c"][0], sine_dict["c"][1])
        d = random.uniform(sine_dict["d"][0], sine_dict["d"][1])
        return [a, b, c, d]
