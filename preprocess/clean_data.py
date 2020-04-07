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
    p.add_argument('-t', dest='filetype', choices=['wikimatrix','os'], help='whether file is wikimatrix or opensubs')
    p.add_argument('-o', dest='output_dir')
    p.add_argument('--strict_filter', action='store_true', help="require bitext and that both lines in bitext be ok else toss")

    return p.parse_args()

def filter_true_language(filepath, lang, output_dir, ok_langs=None):
    if ok_langs:
        all_langs = ok_langs.add(lang)
    else:
        all_langs = {lang}
    pct_stripper = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    keep_lines, cut_lines = [], []
    print("Lang: {}".format(lang), file=sys.stderr)
    with open(filepath, "r") as fin:
        for i, line in enumerate(tqdm(fin)):
            clean_line = re.sub(r' +', ' ', line.strip().translate(pct_stripper))
            predict_lang, confidence  = langid.classify(clean_line)
            #print(predict_lang, confidence)
            if predict_lang not in all_langs:
                print("Predicted Lang {} (Conf: {:4f}) for line: {}".format(predict_lang, confidence, line.strip()),
                      file=sys.stderr)
                cut_lines.append((i,line))
            else:
                keep_lines.append((i,line))
    percent_kept = len(cut_lines)/(len(keep_lines)+len(cut_lines))*100 if keep_lines else 0
    print("{} cleaned lines and {} cut lines ({:2f}) % were cut".format(len(keep_lines),
                                                                    len(cut_lines),
                                                                        percent_kept))
    if args.output_dir:
        filename = os.path.split(filepath)[1]
        filepath = os.path.join(output_dir, filename)
        
    with open(filepath+"_cleaned", "w") as clean_fin, open(filepath+"_cut", "w") as cut_fin:
        clean_fin.write("".join(["{} {}".format(l[0], l[1]) for l in keep_lines]))
        cut_fin.write("".join(["{} {}".format(l[0], l[1]) for l in cut_lines]))


if __name__ == "__main__":
    args = setup_argparse()

    # some languages are sufficiently similar or sufficiently frequently mistaken for each other by classifiers that we want to consider them the same
    lang2ok_lang = {
        "id" : {"ms"}
    }
    
    if args.data_dir:
        with os.scandir(args.data_dir) as source_dir:
            if args.filetype == "wikimatrix":
                files = sorted([file.path for file in source_dir if file.is_file()
                                                            and not file.name.startswith('.')])
            else:
                files = sorted([file.path for file in source_dir if file.is_file()
                            and not file.name.startswith('.')
                            and file.name.endswith('.txt')])
    elif args.files:
        files = args.files

    for filepath in files:
        if args.filetype == "wikimatrix":
            this_lang = os.path.splitext(os.path.split(filepath)[1])[1][1:] # the language is the extension, minus the .
        else:
            this_lang = os.path.splitext(os.path.split(filepath)[1])[0] # filename will be lang.txt, so this grabs lang
        if "_" in this_lang: # handling for beyond standard iso code ie zh_cn which isnt in langid
            this_lang = this_lang.split("_")[0]

        if this_lang in lang2ok_lang:
            ok_langs = lang2ok_lang[this_lang]
        else:
            ok_langs = None

        filter_true_language(filepath, this_lang, args.output_dir, ok_langs)
