import sys, getopt

sys.path.insert(1, "rollo/")
from rollo import executor


def main():
    argv = sys.argv[1:]
    msg = "python rollo -i <inputfile> -c <checkpoint file> "
    try:
        opts, args = getopt.getopt(argv, "i:c:")
        opts_dict = {}
        for opt, arg in opts:
            opts_dict[opt] = arg
        if "-i" in opts_dict:
            if "-c" in opts_dict:
                new_run = executor.Executor(
                    input_file=opts_dict["-i"], checkpoint_file=opts_dict["-c"]
                )
            else:
                new_run = executor.Executor(input_file=opts_dict["-i"])
            new_run.execute()
        if len(opts) == 0:
            raise Exception("To run rollo: " + msg)
    except getopt.GetoptError:
        raise Exception("To run rollo: " + msg)


if __name__ == "__main__":
    main()
