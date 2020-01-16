import argparse
import yaml
import sys

from collections import defaultdict


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='../config/zotero.yaml',
                   help='a yaml config containing necessary API information')
    #p.add_argument('-d', dest='output_dir', default='../outputs/D4/', help='dir to write output summaries to')
    #p.add_argument('-m', dest='model_path', default='', help='path for a pre-trained embedding model')
    return p.parse_args()


def read_yaml_config(config_file):
    return yaml.load(open(config_file))


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




if __name__ == "__main__":
    args = setup_argparse()
    langs2sents = defaultdict(list) # dictionary for storing list of languages and sentences that are in all of those. Coindexed key and rest
    all_languages = []
    src2tgts = {} # dictionary of all the languages that a given language can be translated into.
    
    for lang in all_languages:
        checked = {lang}
        curr_lang_list = [lang]
        curr_sent_list =[]
        target_langs = src2tgts[lang]
        for tgt_lang in target_langs:
            for sent_pair in lang+tgt_lang_bitext:
                curr_sent_list.extend([src_sent, tgt_sent])
                curr_lang_list.append(tgt_lang)
                checked.add(tgt_lang)
                more_langs, more_sents = find_next_translation(tgt_sent, checked)
                curr_lang_list.extend(more_langs)
                curr_sent_list.extend(more_sents)
                langs2sents[tuple(curr_lang_list)].append(curr_sent_list)

    #print out the statistics
    threshold = 10000 # minimum number of parallel sentences below which we do not care
    for lang_list in sorted(langs2sents, key=lambda k:len(k), reverse=True): #this is sorting them by maximum number of langs possible
        num_parallel_sents = len(langs2sents[lang_list])
        if num_parallel_sents < threshold:
            break
        print("{}: {}".format(lang_list, num_parallel_sents))

    # TODO note that I could decide to instead not store the sentences and just store the lists and a count, if memory is an issue. Then I could fetch them later.

                
            
        

