import os 
import xml.etree.ElementTree as ET

root = ET.Element('names')

files = []

for (dirpath, dirnames, filenames) in os.walk('name_txt_files'):
	files.extend(filenames)
	break

files = sorted(files)
files.remove('.DS_Store')

for file in files:
	file_name_list = file.split('_')
	file_name_list = list(map(lambda a: a.title(), file_name_list))

	name_list = ET.SubElement(root, 'name_list', race=file_name_list[0]) if len(file_name_list) == 1 else ET.SubElement(root, 'name_list', race=file_name_list[0], sex=file_name_list[1])

	with open(f"name_txt_files/{file}", 'r') as f:
		for name in f.readlines():
			name_element = ET.SubElement(name_list, 'name', value=name.strip())


tree = ET.ElementTree(root)
ET.indent(tree, space='\t', level=0)
tree.write('xml_files/names.xml', encoding="utf-8")