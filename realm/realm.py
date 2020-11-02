from .backend import BackEnd 
from num2words import num2words

class GenerateReactor(object): 
    """ A generalized framework to generate reactor designs
    using genetic algorithms. 
    """

    def __init__(self, deap_toolbox, params, constraint_obj, eval_obj): 
        self.toolbox = deap_toolbox # deap toolbox object 
        self.params = params # dict 
        self.results = BackEnd() 
        self.check() 

    def check():
        """ This function checks that the params dictionary has all 
        necessary variables defined, if not it raises an error. 
        """

    def generate(self): 
        """ Executes the genetic algorithm and outputs the summarized 
        results into an output file. 
        """
        # initialize the algorithm's parameters 
        pop_size = self.params['pop_size']
        pop = self.toolbox.population(n=pop_size) 
        ngen, cxpb, mutpb = self.params['ngen'],
                            self.params['cxpb']
                            self.params['mutpb']
        # initialize first pop's gen, ind num 
        ind_count = 0
        for ind in pop: 
            ind.gen = 0 
            ind.num = ind_count 
            ind_count += 1
        # evaluate fitness values of initial pop 
        fitnesses = self.toolbox.map(toolbox.evaluate, pop)
        # assign fitness values to individuals 
        for ind, fitness in zip(pop,fitnesses): 
            ind.fitness.values = (fitness[0],)
            ind.output = fitness
            self.results.add_ind(ind)
        # start working on each generation 
        for g in range(ngen):

        print('Completed!')
        return 
    