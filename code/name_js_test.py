import js2py 

race = "Aarakocra"

eval_res, tempfile = js2py.run_file(f'/Users/adrian/Desktop/5eNPCGenerator/name_js_files/dnd{race}.js')
for _ in range(10):
	## SINGLE
	print(tempfile.nameMas().title())

	## SEX 
	print(tempfile.nameMas().title())
	print(tempfile.nameFem().title())

	## SEX && SURNAME
	print(tempfile.nameFem().title(), tempfile.nameSur().title())
	print(tempfile.nameMas().title(), tempfile.nameSur().title())