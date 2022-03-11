from rollo import executor
import sys
import getopt


def main():
    argv = sys.argv[1:]
    msg = "python rollo -i <inputfile> -c <checkpoint file> -v "
    try:
        opts, args = getopt.getopt(argv, "i:c:v")
        if len(opts) == 0:
            raise Exception("To run rollo: " + msg)
        opts_dict = {}
        for opt, arg in opts:
            opts_dict[opt] = arg
        if "-c" in opts_dict:
            cp_file = opts_dict['-c']
        else:
            cp_file = None
        if "-v" in opts_dict:
            verbrose = True
        else:
            verbrose = False
        new_run = executor.Executor(
            input_file=opts_dict['-i'],
            checkpoint_file=cp_file,
            verbrose=verbrose)
        new_run.execute()
    except getopt.GetoptError:
        raise Exception("To run rollo: " + msg)


if __name__ == "__main__":
    main()
