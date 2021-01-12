from collections import defaultdict
import pandas as pd


class BackEnd(object):
    """This class contains and manipulates the output results"""

    def __init__(self, control_dict, output_dict):
        self.results = defaultdict(list)
        self.control_list = self.extend_control_dict(control_dict)
        self.output_dict = output_dict

    def extend_control_dict(self, control_dict):
        control_list = []
        for var in control_dict:
            if control_dict[var][1] > 1:
                for i in range(control_dict[var][1]):
                    control_list.append(var + "_" + str(i))
            else:
                control_list.append(var)
        return control_list

    def add_ind(self, ind):
        """This function adds an individual's information to the results
        dictionary
        """
        self.results["gen"].append(ind.gen)
        self.results["ind"].append(ind.num)
        for i, inp in enumerate(ind):
            self.results["inp_" + str(i)] = inp
        for i, oup in enumerate(ind.output):
            self.results["oup_" + str(i)] = oup
        self.export_to_csv()

    def export_to_csv(self):
        """This function exports the current state of the results dict into
        an output file in the current directory as results.csv
        """
        df = pd.DataFrame(data=self.results)
        df.to_csv("results.csv")
