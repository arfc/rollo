import sys, getopt

sys.path.insert(1, "realm/")
from realm import executor

if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile="])
    except getopt.GetoptError:
        print("python realm -i <inputfile>")
    opts_dict = {}
    for opt, arg in opts:
        opts_dict[opt] = arg
    if "-h" in opts_dict:
        print("python realm -i <inputfile>")
    elif "-i" in opts_dict:
        print("hi")
        if "-c" in opts_dict:
            new_run = executor.Executor(
                input_file=opts_dict["-i"], checkpoint_file=opts_dict["-c"]
            )
        else:
            new_run = executor.Executor(input_file=opts_dict["-i"])

    if "-i" in opts_dict:
        print("hi")
        new_run.execute()
