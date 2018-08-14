# Basic script to change file extension of all file tyes in a given directory on a unix system

import glob
import sys
import os

if len(sys.argv) != 4:
	print("Usage: python3 {} DIR EXT_FROM EXT_TO".format(sys.argv[0]))
	print("eg. python3 {} ./ png jpg".format(sys.argv[0]))
	sys.exit()

print(sys.argv[1])

dir = argv[1]
ext_from = argv[2]
ext_to = argv[3]

files = glob.glob("{}*.{}".format(dir, ext_from))

for file in files:
	new_file = file.replace(".{}".format(ext_from), ".".format(ext_to))
	os.system("mv {} {}".format(file, new_file))
	print("{} done.".format(file))


