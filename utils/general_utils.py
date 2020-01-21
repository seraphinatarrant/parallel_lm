import csv
from typing import Tuple, List, Dict

from collections import defaultdict

UD_LANGUAGES= ['cs', 'gl', 'pt', 'ro', 'ru', 'sv', 'ur', 'el', 'et', 'fi', 'he', 'hsb', 'lv', 'no',
              'tr', 'uk', 'bg', 'bxr', 'ca', 'da', 'de', 'en', 'es', 'eu', 'fa', 'fr', 'ga', 'hi',
              'hr', 'hu', 'id', 'it', 'ja', 'kk', 'kmr', 'ko', 'la', 'sk', 'sl', 'sme', 'sr', 'ta',
              'vi', 'zh', 'af', 'ar', 'cop', 'cu', 'got', 'grc', 'nl', 'pl', 'ug'] # 53 total


def extract_languages(text: str) -> Tuple:
    """gets the two lang codes from a wikimatrix tsv name. Format: WikiMatrix.ar-bn.tsv"""
    p1, p2, p3 = text.split(".")
    src_lang, tgt_lang = p2.split("-")
    return src_lang, tgt_lang



def get_language_list(filepath: str, threshold: int=10000, format="wikimatrix") -> List:
    """reads a list of languages from a text file, based on a given format and threshold"""
    all_langs = []
    # wikimatrix is in the format tsv_name num_sents
    with open(filepath, "r") as fin:
        for line in fin:
            text, num = line.split()
            if int(num) > threshold:
                lang_pair = extract_languages(text)
                all_langs.append(lang_pair)
    return all_langs

def read_func_words(csv_path:str) -> Dict[List]:
    lang2tok = defaultdict(list)
    with open(csv_path, "r", newline="") as csvin:
        reader = csv.reader(csvin)
        for i, line in enumerate(reader):
            if i == 0:
                continue  # skip header
            lang2tok[line[1]].append(line[3])
    return lang2tok