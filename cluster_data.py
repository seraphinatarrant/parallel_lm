import argparse
import yaml
import sys

from sklearn.cluster import KMeans
import numpy as np


def setup_argparse():
    p = argparse.ArgumentParser()
    p.add_argument('-c', dest='config_file', default='../config/zotero.yaml',
                   help='a yaml config containing necessary API information')
    #p.add_argument('-d', dest='output_dir', default='../outputs/D4/', help='dir to write output summaries to')
    #p.add_argument('-m', dest='model_path', default='', help='path for a pre-trained embedding model')
    return p.parse_args()


def read_yaml_config(config_file):
    return yaml.load(open(config_file))

def load_corpus(data, tokenized=True):
    if tokenized


if __name__ == "__main__":
    args = setup_argparse()

    print("Reading config...")
    config = read_yaml_config(args.config_file)

    num_clusters = 2
    data = []
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(data)
    kmeans.predict
    kmeans.labels

