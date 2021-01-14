import sys, getopt

sys.path.insert(1, "realm/")
from realm import executor

if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile="])
    except getopt.GetoptError:
        print("python realm -i <inputfile>")
    for opt, arg in opts:
        print(opt, arg)
        if opt == "-h":
            print("python realm -i <inputfile>")
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            new_run = executor.Executor(input_file=inputfile)
            new_run.execute()
