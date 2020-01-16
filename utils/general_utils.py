from typing import Tuple,List


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