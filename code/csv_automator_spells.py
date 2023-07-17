import xml.etree.ElementTree as ET
import csv

root = ET.Element('spells')

with open('leftovers/Spells.csv') as file:
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
	sub_element = ET.SubElement(root, 'spell', name=key, level=k[0], availability=f"{k[6]}, {k[7]}", casting_time=k[1])


	duration = ET.SubElement(sub_element, 'duration', value=k[2])
	sub_element.extend(duration)

	school = ET.SubElement(sub_element, 'school', value=k[3])
	sub_element.extend(school)

	range_ = ET.SubElement(sub_element, 'range', value=k[4])
	sub_element.extend(range_)

	components = ET.SubElement(sub_element, 'components', value=k[5])
	sub_element.extend(components)

	description = ET.SubElement(sub_element, 'description', value=k[8])
	sub_element.extend(description)

	higher_levles = ET.SubElement(sub_element, 'higher_levles', value=k[9])
	sub_element.extend(higher_levles)

tree = ET.ElementTree(root)
ET.indent(tree, space='\t', level=0)
tree.write('xml_files/spells.xml', encoding="utf-8")