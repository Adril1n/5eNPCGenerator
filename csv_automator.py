import xml.etree.ElementTree as ET
import csv

root = ET.Element('armors')

with open('armors.csv') as file:
	reader = csv.reader(file)
	dict_ = dict((rows[0], (rows[1], rows[2], rows[3], rows[4])) for rows in reader)

for key in dict_.keys():
	sub_element = ET.SubElement(root, 'armor', name=key, ac=dict_[key][0], str_req=dict_[key][1], stealth_dis=str(dict_[key][2] == 'Disadvantage'), type=dict_[key][3])

tree = ET.ElementTree(root)
ET.indent(tree, space='\t', level=0)
tree.write('armors.xml', encoding="utf-8")