import xml.etree.ElementTree as ET
import csv

root = ET.Element('traits')

with open('leftovers/dnd  - traits.csv') as file:
	reader = csv.reader(file)
	dict_ = {}
	for rows in reader:
		a = []
		for i in range(len(rows)):
			if i != 0:
				a.append(rows[i])

		dict_[rows[0]] = a

for key in dict_:
	k = dict_[key]
	sub_element = ET.SubElement(root, 'trait', name=key, description=dict_[key][0])

tree = ET.ElementTree(root)
ET.indent(tree, space='\t', level=0)
tree.write('xml_files/traits.xml', encoding="utf-8")