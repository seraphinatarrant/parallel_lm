import sys
import os
import itertools
from functools import reduce

langs = sys.argv[1:]
sets = []

for lang in langs:
	sets.append(set(os.listdir(lang)))

filelist = reduce(set.intersection, sets)

# check that they have the same tags
for lang in langs:
	outfile = open("corpus.{}".format(lang), "w")
	pathnames = [os.path.join(i, j) for (i, j) in itertools.product([lang], filelist)]
	dumps = [open(i, "r").readlines() for i in pathnames]
	for d in dumps:
		for line in d:
			outfile.write(line)
	
	
