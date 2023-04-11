import xml.etree.ElementTree as ET
import csv

occps = ET.Element('occupations')

with open('occupations.csv') as file:
	reader = csv.reader(file)
	dict_ = dict((rows[0], rows[1]) for rows in reader)

for key in dict_.keys():
	occp = ET.SubElement(occps, 'occupation', name=key, description=dict_[key])

tree = ET.ElementTree(occps)
ET.indent(tree, space='\t', level=0)
tree.write('occupations.xml', encoding="utf-8")