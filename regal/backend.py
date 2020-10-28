from collections import defaultdict

class BackEnd(object):
    """ This class contains and manipulates the output results 
    """ 

    def __init__(self): 
        self.results_dict = defaultdict(list)
