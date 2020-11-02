from collections import defaultdict
import pandas as pd

class BackEnd(object):
    """ This class contains and manipulates the output results 
    """ 

    def __init__(self): 
        self.results = defaultdict(list)

    def add_ind(self, ind):
        """ This function adds an individual's information to the results 
        dictionary 
        """
        self.results['gen'].append(ind.gen)
        self.results['ind'].append(ind.num)
        for i, inp in enumerate(ind):
            self.results['inp_'+str(i)] = inp
        for i, oup in enumerate(ind.output):
            self.results['oup_'+str(i)] = oup
        self.export_to_txt()

    def export_to_txt(self):
        """ This function exports the current state of the results dict into 
        an output file in the current directory as results.csv 
        """
        df = pd.DataFrame(data=self.results)
        df.to_csv('results.csv')