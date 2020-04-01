#for each lang pair
#    get overlap
#load in zip files
#extract overlapping files and make into format like dir: en-fr with subdir en and fr.

import argparse
import glob
import gzip

import os
import pickle
import time

from tqdm import tqdm
import zipfile
import xml.etree.ElementTree as ET


from collections import defaultdict


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-s', dest='source_dir', help='source dir for files')
    p.add_argument('-t', dest='target_dir', help='target dir to write extracted text')
    p.add_argument('-f', '--file_ids', help='source dir for pre-extracted file ids')
    return p.parse_args()


def find_overlapping_files(p, all_files=False, target_dir=''):
    
    if all_files:
        files = glob.glob(p + '*.xml.gz')
    else:
        files = glob.glob(p + '.xml.gz') # this will be lang1-lang2.xml.gz
    dic = defaultdict(dict)
    # 1. Loop over all ces files in path (e.g. de-en.xml.gz) to find overlapping files.
    # 2. Create a dictionary containing matching filenames
    # example dictionary output:
    # {
    #   'en/1921/12349/5775558.xml.gz': {
    #       'de': 'de/1921/12349/5510195.xml.gz',
    #       'es': 'es/1921/12349/4260047.xml.gz',
    #       'et': 'et/1921/12349/5184442.xml.gz',
    #       'fi': 'fi/1921/12349/3676439.xml.gz',
    #       'nl': 'nl/1921/12349/3683372.xml.gz',
    #       'sv': 'sv/1921/12349/5510194.xml.gz'
    #   }
    # }
    print('Found files {}'.format(files))
    for i, f in enumerate(files):
        print('Processing {} | {}/{}'.format(f, i + 1, len(files)))
        with gzip.open(f, 'rt') as fl:
            try:
                tree = ET.parse(fl)
            except OSError:
                print('skipping')
                # os.remove(f)
                continue
            root = tree.getroot()
            linkGrps = root.findall('linkGrp')
            for linkGrp in tqdm(linkGrps, desc=f,
                                bar_format='{desc}{percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt}'):
                # check for .gz ending and strip it
                fromDoc, f_ext = os.path.splitext(linkGrp.get('fromDoc'))
                toDoc, t_ext = os.path.splitext(linkGrp.get('toDoc'))

                # fromDoc is always english
                default_from = 'en'
                tmp = toDoc
                toDoc = toDoc if not toDoc.startswith(default_from) else fromDoc
                fromDoc = fromDoc if fromDoc.startswith(default_from) else tmp
                #breakpoint()
                dic[fromDoc].update({toDoc.split('/')[0]: toDoc})

    # 3. Save the dictionary in a file
    out_file = os.path.join(target_dir, '{}_file_ids'.format(os.path.split(p)[1])) if not all_files else 'all_file_ids'
    with open(out_file, 'wb') as f:
        pickle.dump(dic, f)
    return dic


def get_sents(this_zip, filename):
    all_sents = []
    with this_zip.open(filename, "r") as fin:
        try:
            tree = ET.parse(fin)
        except:
            print("failed to parse file: {}".format(filename))
            return None
        root = tree.getroot()
        sents = root.findall("s")
        for s in sents:
            all_sents.append(" ".join([w.text for w in s.findall("w")]))

    return all_sents



def copy_files(overlaps, source_dir, target_dir, lang):
    # keys in overlaps will be english, subdicts will be key other lang, values other file
    print("processing data for en and {}".format(lang))
    start_time = time.time()
    skipped = []
    prefix = "OpenSubtitles/xml/"
    all_en_lines, all_other_lines = [], [] # TODO might have to do something different if can't all fit in memory...
    with zipfile.ZipFile(os.path.join(source_dir, "en.zip")) as z_en, \
         zipfile.ZipFile(os.path.join(source_dir, "{}.zip".format(lang))) as z_other: # currently only works for bitext, easy to extend
        all_en_files, all_other_files = set(z_en.namelist()), set(z_other.namelist())
        for en_file in overlaps.keys():
            # make sure all found before copying otherwise data isn't parallel
            other_file = overlaps[en_file][lang]
            en_file = prefix + en_file
            other_file = prefix + other_file
            #breakpoint()
            if en_file not in all_en_files or other_file not in all_other_files:
                skipped.append((en_file, other_file))
                continue
            en_sents, other_sents = get_sents(z_en, en_file), get_sents(z_other, other_file)
            #breakpoint()
            if en_sents and other_sents:
                all_en_lines.extend(en_sents)
                all_other_lines.extend(other_sents)
    with open(os.path.join(target_dir, "en.txt"), "w") as en_out, \
            open(os.path.join(target_dir, "{}.txt".format(lang)), "w") as other_out:
        en_out.write("\n".join(all_en_lines))
        other_out.write("\n".join(all_other_lines))
        print("wrote {} lines of en and {} lines of {}".format(
            len(all_en_lines), len(all_other_lines), lang))
        print("Seconds elapsed for this lang set: {}".format(time.time()-start_time))
    

if __name__ == "__main__":
    args = setup_argparse()

    all_languages = ["zh_cn", "zh_tw", "eu", "ar", "fi", "id", "ta", "ru", "de", "el", "es"] # everything will be alphabetical
    print("Working on {} languages".format(len(all_languages)))
    for lang in all_languages:
        lang_pair = "{}-{}".format(*sorted([lang,"en"]))
        # make directory for lang pair if doesn't exist
        target_dir = os.path.join(args.target_dir, lang_pair)
        os.makedirs(target_dir, exist_ok=True)
        if not args.file_ids:
            overlaps = find_overlapping_files(os.path.join(args.source_dir, lang_pair), target_dir=target_dir)
        else:    
            file_path = os.path.join(args.file_ids, '{}_file_ids'.format(lang_pair)
            with open(filepath, 'rb') as fin:
                overlaps = pickle.load(fin)
        copy_files(overlaps, args.source_dir, target_dir, lang)


