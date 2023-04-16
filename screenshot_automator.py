import os 

files = []

for (dirpath, dirnames, filenames) in os.walk('Race Screenshots'):
	files.extend(filenames)
	break

