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


def strict_filter_true_language(files, langs, output_dir):

    pct_stripper = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    keep_lines, cut_lines = [], []
    print("Langs: {}".format(langs), file=sys.stderr)
    with open(files[0], "r") as fin1, open(files[1], "r") as fin2:
        for i, line1, line2 in enumerate(zip(fin1, fin2)):
            clean_line1 = re.sub(r' +', ' ', line1.strip().translate(pct_stripper))
            clean_line2 = re.sub(r' +', ' ', line1.strip().translate(pct_stripper))
            predict_lang1, confidence1 = langid.classify(clean_line1)
            predict_lang2, confidence2 = langid.classify(clean_line2)
            # print(predict_lang, confidence)
            if predict_lang1 not in langs[0] or predict_lang2 not in langs[1]:
                print(
                    "Pair:\n"
                    "Predicted Lang {} (Conf: {:4f}) for line: {} \n"
                    "Predicted Lang {} (Conf: {:4f}) for line: {}".format(
                        predict_lang1, confidence1, line1.strip(),
                        predict_lang2, confidence2, line2.strip()),
                    file=sys.stderr)
                cut_lines.append((line1, line2))
            else:
                keep_lines.append((line1, line2))

    percent_kept = len(cut_lines) / (len(keep_lines) + len(cut_lines)) * 100 if keep_lines else 0
    print("{} cleaned lines and {} cut lines ({:2f}) % were cut".format(len(keep_lines),
                                                                        len(cut_lines),
                                                                        percent_kept))
    if args.output_dir:
        out_files = []
        for filepath in files:
            filename = os.path.split(filepath)[1]
            filepath = os.path.join(output_dir, filename)
            out_files.append(filepath)
    else:
        out_files = files

    with open(out_files[0] + "_cleaned", "w") as clean_fin1, open(out_files[1] + "_cleaned", "w") as clean_fin2:
        clean_fin1.write("".join([l[0] for l in keep_lines]))
        clean_fin2.write("".join([l[1] for l in keep_lines]))

    with open(out_files[0] + "_cut", "w") as cut_fin1, open(out_files[1] + "_cut", "w") as cut_fin2:
        clean_fin1.write("".join([l[0] for l in cut_lines]))
        clean_fin2.write("".join([l[1] for l in cut_lines]))

def filter_true_language(filepath, ok_langs: set, output_dir):

    pct_stripper = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    keep_lines, cut_lines = [], []
    print("Lang: {}".format(ok_langs), file=sys.stderr)
    with open(filepath, "r") as fin:
        for i, line in enumerate(tqdm(fin)):
            clean_line = re.sub(r' +', ' ', line.strip().translate(pct_stripper))
            predict_lang, confidence  = langid.classify(clean_line)
            #print(predict_lang, confidence)
            if predict_lang not in ok_langs:
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


def extract_lang(filepath: str, filetype: str):
    if filetype == "wikimatrix":
        this_lang = os.path.splitext(os.path.split(filepath)[1])[1][1:]  # the language is the extension, minus the .
    else:
        this_lang = os.path.splitext(os.path.split(filepath)[1])[0]  # filename will be lang.txt, so this grabs lang

    if "_" in this_lang:  # handling for beyond standard iso code ie zh_cn which isnt in langid
        this_lang = this_lang.split("_")[0]

    return this_lang


def expand_lang(this_lang: str, lang2ok_lang: dict) -> set:
    if this_lang in lang2ok_lang:
        ok_langs = lang2ok_lang[this_lang]
    else:
        ok_langs = {this_lang}
    return ok_langs


if __name__ == "__main__":
    args = setup_argparse()

    # some languages are sufficiently similar or sufficiently frequently mistaken for each other by classifiers that we want to consider them the same
    lang2ok_lang = {
        "id" : {"id", "ms"}
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

    if args.strict_filter:
        langs = [extract_lang(f, args.filetype) for f in files]
        ok_langs = [expand_lang(this_lang, lang2ok_lang) for this_lang in langs]
        strict_filter_true_language(files, ok_langs, args.output_dir)

    else:
        for filepath in files:
            this_lang = extract_lang(filepath, args.filetype)
            ok_langs = expand_lang(this_lang, lang2ok_lang)

            filter_true_language(filepath, ok_langs, args.output_dir)
