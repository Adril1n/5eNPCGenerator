import xml.etree.ElementTree as ET
import csv

root = ET.Element('gods')

with open('csv_files/gods.csv') as file:
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
	sub_element = ET.SubElement(root, 'god', name=key)

	for dataval in k:
		data_element = ET.SubElement(sub_element, 'dataval', key=)

tree = ET.ElementTree(root)
ET.indent(tree, space='\t', level=0)
tree.write('xml_files/gods.xml', encoding="utf-8")