class MoltresEvaluation:
    """The MoltresEvaluation class contains ROLLO built-in methods for evaluating
    Moltres output files. Developers can update thisfile with methods to 
    evaluate frequently used Moltres outputs.

    Attributes
    ----------
    pre_defined_outputs : list
        list of variables names with evaluation functions in this class

    """

    def __init__(self):
        self.pre_defined_outputs = []
