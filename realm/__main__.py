import sys, getopt

sys.path.insert(1, "realm/")
from realm import executor
from deap import creator, base

if __name__ == "__main__":
    argv = sys.argv[1:]
    msg = "python realm -i <inputfile> -c <checkpoint file> -p <min or max obj>"
    try:
        opts, args = getopt.getopt(argv, "i:p:c:")
    except getopt.GetoptError:
        print("To run realm:")
        print(msg)
    wt_dict = {"min": -1.0, "max": +1.0}
    opts_dict = {}
    for opt, arg in opts:
        opts_dict[opt] = arg
    if "-i" in opts_dict and "-p" in opts_dict:
        creator.create("obj", base.Fitness, weights=(wt_dict[opts_dict["-p"]],))
        creator.create("Ind", list, fitness=creator.obj)
        if "-c" in opts_dict:
            new_run = executor.Executor(
                input_file=opts_dict["-i"], checkpoint_file=opts_dict["-c"]
            )
        else:
            new_run = executor.Executor(input_file=opts_dict["-i"])
        new_run.execute()
    else:
        print("To run realm:")
        print(msg)
