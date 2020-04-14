import argparse

import os
import random
import sys


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-d', dest='data_dir', help='a dir for files to sample from')
    p.add_argument('-f', dest='files', nargs='+', help='a list of all the files to use instead of a dir')
    p.add_argument('-t', dest='target_dir', help='a dir to write files to')
    p.add_argument('-m', dest='max_lines', type=int, help='maximum lines to sample down to')

    return p.parse_args()



if __name__ == "__main__":
    args = setup_argparse()

    if args.data_dir:
        with os.scandir(args.data_dir) as source_dir:
            files = sorted([file.path for file in source_dir if file.is_file()
                            and not file.name.startswith('.')])

    elif args.files:
        files = args.files

    else:
        sys.exit("need to provide either -d or -f flag")

    os.makedirs(args.target_dir, exist_ok=True)
    for filepath in files:
        print("Working on: {}".format(filepath))
        filename = os.path.split(filepath)[1]
        with open(filepath, "r") as fin:
            lines = fin.readlines()
            out_lines = random.sample(lines, args.max_lines)
        with open(os.path.join(args.target_dir, filename), "w") as fout:
            fout.write("".join(out_lines))