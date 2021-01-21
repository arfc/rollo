import sys, getopt
from deap import creator, base

sys.path.insert(1, "realm/")
from realm import executor

if __name__ == "__main__":
    argv = sys.argv[1:]
    print(argv)
    try:
        opts, args = getopt.getopt(argv, "i:m:c:")
    except getopt.GetoptError:
        print("python realm -i <inputfile>")
    opts_dict = {}
    for opt, arg in opts:
        opts_dict[opt] = arg
    if "-h" in opts_dict:
        print("python realm -i <inputfile>")
    elif "-i" in opts_dict:
        if "-c" in opts_dict:
            new_run = executor.Executor(
                input_file=opts_dict["-i"], checkpoint_file=opts_dict["-c"]
            )
        else:
            new_run = executor.Executor(input_file=opts_dict["-i"])
    creator.create("obj", base.Fitness, weights=(-1.0,))
    creator.create("Ind", list, fitness=creator.obj)
    if "-i" in opts_dict:
        new_run.execute()
