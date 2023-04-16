import os 
import csv

files = []

with open("leftovers/dnd  - Races.csv") as csv_f:
	reader = csv.reader(csv_f)
	l = [f"{rows[0]} ({rows[1]})" for rows in reader]

for (dirpath, dirnames, filenames) in os.walk('Race Screenshots'):
	files.extend(filenames)
	break

files = sorted(files)
files.remove('.DS_Store')

for i in range(len(files)):
	file = files[i]
	print(file, f"{l[i]}.png")
	os.rename(f"Race Screenshots/{file}", f"Race Screenshots/{l[i]}.png")