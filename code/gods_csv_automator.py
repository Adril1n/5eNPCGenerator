import xml.etree.ElementTree as ET
import csv

root = ET.Element('gods')

with open('csv_files/gods.csv') as file:
	reader = csv.reader(file)
	dict_ = {}
	headers = []
	for row in reader:
		headers = row
		break

	for rows in reader:
		a = []
		for i in range(len(rows)):
			if i != 0:
				a.append(rows[i])

		dict_[rows[0]] = a

headers.remove('Deity')

for key in dict_:
	k = dict_[key]

	name_desc = key.split(', ')

	sub_element = ET.SubElement(root, 'god', name=name_desc[0])

	desc = ET.SubElement(sub_element, 'dataval', key='description', value=name_desc[1])
	sub_element.extend(desc)

	for header in headers:
		sub_sub_element = ET.SubElement(sub_element, 'dataval', key=header.lower().replace(' ', '_'), value=k[headers.index(header)])
		sub_element.extend(sub_sub_element)

tree = ET.ElementTree(root)
ET.indent(tree, space='\t', level=0)
tree.write('xml_files/gods.xml', encoding="utf-8")