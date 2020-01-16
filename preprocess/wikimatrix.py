import argparse
import csv
import sys

import yaml
import os

from collections import defaultdict
from typing import List, Tuple, Dict

from utils.general_utils import get_language_list


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='../config/zotero.yaml',
                   help='a yaml config containing necessary API information')
    #p.add_argument('-d', dest='output_dir', default='../outputs/D4/', help='dir to write output summaries to')
    #p.add_argument('-m', dest='model_path', default='', help='path for a pre-trained embedding model')
    return p.parse_args()


def read_yaml_config(config_file):
    return yaml.load(open(config_file))

"""
def find_next_translation(src_sent, checked):
    more_langs = []
    more_sents = []
    for lang_pair in all_lang_pairs_starting_with_src_dict:
        if tgt_lang in checked:
            continue
        if src_sent in lang_pair_bitext:
            more_langs.append(tgt_lang)
            more_sents.append(tgt_sent)
            checked.add(tgt_lang)
            find_next_translation(tgt_sent, checked) # TODO make sure this works
    return more_langs, more_sents
"""

def get_all_targets_from_pairs(all_language_pairs: List[Tuple]) -> Dict:
    # based on the way wikimatrix is constructed, translations are symmetrical, so they're not really src and target but equal pairs
    src2tgts = defaultdict(list)
    for lang1, lang2 in all_language_pairs:
        src2tgts[lang1].append(lang2)
        src2tgts[lang2].append(lang1)
    return src2tgts


def make_tsv_name(lang, tgt_lang, data_dir) -> Tuple:
    """since bitext is symmetric, try both ways"""
    template = "WikiMatrix.{}-{}.tsv"
    t1, t2 = os.path.join(data_dir, template.format(lang, tgt_lang)), \
             os.path.join(data_dir, template.format(tgt_lang, lang))
    if os.path.isfile(t1):
        return t1, False  # returns whether the langs had to be swapped around
    if os.path.isfile(t2):
        return t2, True
    print("No file for either language found. Check that the directory is correct? "
          "Looked in:\n{}\n{}".format(t1, t2), file=sys.stderr)
    return None, False


if __name__ == "__main__":
    args = setup_argparse()
    # things to go in a config later
    lang_list = "config/list_of_bitexts.txt"
    data_dir = "~/data/WikiMatrix/"
    sim_score_thresh = 1.04

    langs2sents = defaultdict(list) # dictionary for storing list of languages and sentences that are in all of those. Coindexed key and rest
    all_language_pairs = get_language_list(lang_list)
    src2tgts = get_all_targets_from_pairs(all_language_pairs)
    all_languages = list(src2tgts.keys())
    print("Processing {} languages and {} language pairs...".format(len(all_languages),
                                                                    len(all_language_pairs)))
    for key in sorted(src2tgts, key=lambda x: len(src2tgts[x]),reverse=True):
        print("{}: {}".format(key, len(src2tgts[key])), file=sys.stderr)
    
    for lang in all_languages:
        checked = {lang}
        curr_lang_list = [lang]
        curr_sent_list = []
        target_langs = src2tgts[lang]
        for tgt_lang in target_langs:
            # fetch tsv from data dir, load it in. Don't load in everything at once cause it's 60GB
            tsv_name, swapped = make_tsv_name(lang, tgt_lang, data_dir)
            if not tsv_name:
                continue
            with open(tsv_name, "r", newline='') as tsvin:
                tsv_reader, swapped = csv.reader(tsvin, delimiter="\t")
                # wikimatrix format is sim_score \t src_sent \t tgt_sent
                total_skipped = 0
                for row in tsv_reader:
                    if float(row[0]) < sim_score_thresh:
                        total_skipped += 1
                    else:
                        if not swapped:
                            src_sent, tgt_sent = row[1], row[2]
                        else:
                            src_sent, tgt_sent = row[2], row[1]

                        curr_sent_list.extend([src_sent, tgt_sent])
                        curr_lang_list.append(tgt_lang)
                        checked.add(tgt_lang)
                        # this is where we spin out to all the languages that this
                        #todo
                        #more_langs, more_sents = find_next_translation(tgt_sent, checked)
                        #curr_lang_list.extend(more_langs)
                        #curr_sent_list.extend(more_sents)
                        langs2sents[tuple(curr_lang_list)].extend(curr_sent_list)

    #print out the statistics
    threshold = 10000 # minimum number of parallel sentences below which we do not care
    for lang_list in sorted(langs2sents, key=lambda k:len(k), reverse=True): #this is sorting them by maximum number of langs possible
        num_parallel_sents = len(langs2sents[lang_list])
        if num_parallel_sents < threshold:
            break
        print("{}: {}".format(lang_list, num_parallel_sents))

    # TODO note that I could decide to instead not store the sentences and just store the lists and a count, if memory is an issue. Then I could fetch them later.

                
            
        

