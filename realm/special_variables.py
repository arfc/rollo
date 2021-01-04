import random
import numpy as np

class SpecialVariables:
    def __init__(self):
        # developer's should add to this list when defining a new special
        # variable
        self.special_variables = ["polynomial"]
        return

    def polynomial_naming(self, polynomial_dict):
        """This function returns a list of strings of the variable names"""
        order = polynomial_dict["order"]
        name = polynomial_dict["name"]
        var_names = []
        for i in range(order + 1):
            var_names.append("poly_" + name + "_" + str(i))
        return var_names

    def polynomial_toolbox(self, poly_dict, toolbox):
        """This function registers all the polynomial variables in deap toolbox"""
        toolbox.register("poly_" + poly_dict["name"], 
                         random.uniform, 
                         poly_dict["min"],
                         poly_dict["max"],
                         )
        return toolbox

    def polynomial_values(self, poly_dict, toolbox, total_pf):
        """ This function returns polynomial values 
        """
        dz = 10
        poly_vals = np.array([-1.]*dz)
        dz_vals = np.linspace(0, 100, dz)
        pf_z = np.array([0.3] * dz)
        vol_triso = 4/3*np.pi*poly_dict["radius"]**3
        total_trisos = round(total_pf*poly_dict["volume"]/vol_triso)
        poly = []
        while len(poly_vals[poly_vals<0]) != 0 and len(pf_z[pf_z > 0.25]):
            for i in range(poly_dict["order"]+1):
                poly.append(getattr(toolbox, "poly_"+poly_dict["name"])())
            poly_vals = np.array([0.]*dz)
            for i in range(poly_dict["order"]+1):
                poly_vals += poly[i]*dz_vals**(poly_dict["order"]-float(i))
            z_trisos = poly_vals/sum(poly_vals)*total_trisos
            pf_z = z_trisos*vol_triso/(poly_dict["volume"]/dz)
        print("pf", [round(i,2) for i in pf_z])
        print("polyval", [round(i,2) for i in poly_vals])
        print("poly", [round(i,2) for i in poly])
        return poly
