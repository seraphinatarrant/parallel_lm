import argparse
import string
import re

import os
import sys
import langid
from tqdm import tqdm


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-d', dest='data_dir', help='a directory containing the files to clean')
    p.add_argument('-f', dest='files', nargs='+', help='files to check, rather than a full directory')
    #p.add_argument('--metrics', action='store_true', help="don't modify files, only print metrics")

    return p.parse_args()

def filter_true_language(filepath, lang):
    pct_stripper = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    keep_lines, cut_lines = [], []
    print("Lang: {}".format(lang), file=sys.stderr)
    with open(filepath, "r") as fin:
        for i, line in enumerate(tqdm(fin,
                                bar_format='{percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt}')):
            clean_line = re.sub(r' +', ' ', line.strip().translate(pct_stripper))
            predict_lang, confidence  = langid.classify(clean_line)
            #print(predict_lang, confidence)
            if predict_lang != lang:
                print("Predicted Lang {} (Conf: {:4f}) for line: {}".format(predict_lang, confidence, line.strip()),
                      file=sys.stderr)
                cut_lines.append((i,line))
            else:
                keep_lines.append((i,line))
    print("{} cleaned lines and {} cut lines ({:2f}) % were cut".format(len(keep_lines),
                                                                    len(cut_lines),
                                                                    (len(cut_lines)/len(keep_lines))*100))
    with open(filepath+"_cleaned", "w") as clean_fin, open(filepath+"_cut", "w") as cut_fin:
        clean_fin.write("".join(["{} {}".format(l[0], l[1]) for l in keep_lines]))
        cut_fin.write("".join(["{} {}".format(l[0], l[1]) for l in cut_lines]))


if __name__ == "__main__":
    args = setup_argparse()

    if args.data_dir:
        with os.scandir(args.data_dir) as source_dir:
            files = sorted([file.path for file in source_dir if file.is_file()
                            and not file.name.startswith('.')
                            and file.name.endswith('.txt')])
    elif args.files:
        files = args.files

    for filepath in files:
        this_lang = os.path.splitext(os.path.split(filepath)[1])[0] # filename will be lang.txt, so this grabs lang
        filter_true_language(filepath, this_lang)
