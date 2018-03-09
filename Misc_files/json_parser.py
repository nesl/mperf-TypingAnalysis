'''
Coded By : Vikranth
'''

import json
from pprint import pprint
import os.path
import glob

text = input("Enter Keyword to be searched")

for filename in glob.iglob('E:\Keylogs\mustafa\Data/2f0b3625-db5b-4159-87c1-9c005fb8659e/**/*.json', recursive=True):
   # print(filename)

	json_data=open(filename)
	jdata = json.load(json_data)
	#pprint (jdata)
	json_data.close()

	if text in jdata['name']:
		print (filename)
		print(jdata['name'])

'''
import os.path
import glob

for filename in glob.iglob('E:\Keylogs\mustafa\Data\/**/*.json', recursive=True):
    print(filename)
'''