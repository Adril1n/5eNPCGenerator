import tkinter as tk
from numpy.random import default_rng, SeedSequence
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
import webbrowser
import colorsys

class Rng():
	def __init__(self):
		self.seed = SeedSequence().entropy
		self.rng = default_rng(seed=self.seed)

	def get_rng(self):
		return self.rng

	def get_seed(self):
		return self.seed

class ResourceLoader():
	def __init__(self):
		self.xml_files = {}

	def get_xml_root(self, xml_name):
		filename = xml_name + '.xml'
		try: 
			root = self.xml_files[xml_name]
		except KeyError:
			tree = ET.parse(filename)
			root = tree.getroot()
			self.xml_files[xml_name] = root
		return root

	def get_list(self, xml):
		root = self.get_xml_root(xml)
		list_ = []

		for obj in root:
			list_.append(obj.get('name'))

		return list_

	def get_occupation_description(self, occ_id):
		jobs = self.get_xml_root('jobs')
		
		for job in jobs:
			if job.get('name') == occ_id:
				return job.get('description')

		return "Nothing"

	def get_subrace(self, rng, race_id):
		races = self.get_xml_root('races')

		for race in races:
			if race.get('name') == race_id:
				return race.findall('type')[np.floor(rng.random()*(len(race.findall('type')))).astype('int')].get('name')

		return "None"

	def get_race_ability_bonuses(self, abilities, rng, race_id, subrace_id):
		races = self.get_xml_root('races')

		a = {}

		for race in races:
			if race.get('name') == race_id:
				for type_ in race.findall('type'):
					if type_.get('name') == subrace_id:
						datavals = type_.findall('datadict')[0].findall('dataval')

						for dataval in datavals:
							if dataval.get('key') == 'abilities':
								if dataval.get('value') == 'dict':
									for ability in dataval.findall('ability'):
										a[ability.get('key')] = ability.get('value')

								elif dataval.get('value') == 'dict_choice':
									ability = dataval.findall('ability')[np.floor(rng.random()*(len(dataval.findall('ability')))).astype('int')]

									keys = list(abilities.keys())

									nums = ability.get('value').split(':')
									for num in nums:
										ablt = rng.choice(keys)
										a[ablt] = num
										keys.pop(keys.index(ablt))



		return a

	def get_proficiencies(self, rng, npc_class):
		classes = self.get_xml_root('classes')

		a = {}

		for class_ in classes:
			if class_.get('name') == npc_class:
				for dataval in class_.findall('datadict')[0].findall('dataval'):
					if dataval.get('key') == 'proficiencies':
						for prof in dataval.findall('proficiency'):
							key = prof.get('key')
							val = prof.get('value')

							if ':' in val and ';' not in val:
								aa = val.split(':')
								a[key] = aa
							elif ';' in val and ':' not in val:
								aa = val.split(';')
								a[key] = list(rng.choice(aa[1:], int(aa[0])))
							elif ';' in val and ':' in val:
								aa = val.split(':')
								ab = aa[-1].split(';')
								ac = list(rng.choice(ab[1:], int(ab[0])))

								ad = []

								for p in (*aa[:-1], *ac):
									ad.append(f"{p} {key}")

								a[key] = ad
							else:
								a[key] = [val]

		

		return a

	def get_appearances(self, rng, race_id, subrace_id):
		races = self.get_xml_root('races')

		a = {}

		for race in races:
			if race.get('name') == race_id:
				for subrace in race.findall('type'):
					if subrace.get('name') == subrace_id:
						for dataval in subrace.findall('datadict')[0].findall('dataval'):
							if dataval.get('key') == 'appearances':
								for app in dataval.findall('appearance'):
									key = app.get('key')
									val = app.get('value')

									if ':' not in val and ';' not in val and '-' not in val:
										a[key] = [val]
									elif ':' in val and ';' not in val and '-' not in val:
										aa = val.split(':')
										a[key] = aa
									elif ':' not in val and ';' in val and '-' not in val:
										aa = val.split(';')
										a[key] = list(rng.choice(aa[1:], int(aa[0])))
									else:
										aa = val.split('-')
										ab = rng.integers(int(aa[0]), high=int(aa[1])+1)

										if key == 'age':
											age_dict = {0.35:'Young', 0.75:'Middle Aged', 10:'Elderly'}
											ac = ''
											for bin_ in age_dict:
												if ab/int(aa[1]) <= bin_:
													ac = age_dict[bin_]
													break

											ab = f"Age: {ab} ({ac}, {aa[0]}->{aa[1]})"

											a[key] = [ab]
										else:
											a[key] = [ab, (aa[0], aa[1])]

		return a 

	def get_languages_or_speeds(self, rng, race_id, subrace_id, tt):
		races = self.get_xml_root('races')

		a = []

		for race in races:
			if race.get('name') == race_id:
				for subrace in race.findall('type'):
					if subrace.get('name') == subrace_id:
						for dataval in subrace.findall('datadict')[0].findall('dataval'):
							d = {'lan':'language', 'spd':'speed'}

							if dataval.get('key') == f"{d[tt]}s":
								for lan in dataval.findall(d[tt]):
									key = lan.get('key')
									val = lan.get('value')

									if 'random' in key:
										l = ['Common', 'Dwarvish', 'Elvish', 'Giant', 'Gnomish', 'Goblin', 'Halfling', 'Orc', 'Abyssal', 'Celestial', 'Draconic', 'Deep Speech', 'Infernal', 'Primordial', 'Sylvan', 'Undercommon']
										l = list(filter(lambda x: x not in [y.get('key') for y in dataval.findall(d[tt])], l))
										key = rng.choice(l)

									a.append(f"{key} ({val})")

		return a


	def get_weapon(self, rng, prof):
		weapons = self.get_xml_root('weapons')

		a = []
		for weapon in weapons:
			if weapon.get('type') in prof:
				a.append(f"{weapon.get('name')} ({weapon.get('damage')}, {weapon.get('properties')})")

		if len(a) == 0:
			return f"Unarmed Attack: 1 + STR MOD"
		else:
			return rng.choice(a)


	def get_armor(self, rng, prof, str_):
		b = prof.copy()
		if 'shield' in b:
			b.remove('shield')

		armors = self.get_xml_root('armors')
 		
		a = []
		for armor in armors:
			if armor.get('type') in b and int(armor.get('str_req')) <= str_:
				d = {}
				for att in armor.attrib:
					if att != 'stealth_dis':
						d[att] = armor.attrib[att]
					else:
						d[att] = bool(armor.attrib[att])

				a.append(d)

		if len(a) == 0:
			return {'name':'Unarmored', 'ac':'10', 'stealth_dis':'False'}
		else:
			return rng.choice(a)
 				

class NPC():
	def __init__(self):
		self.tags = {}
		self.rng_object = Rng()

	def set_tag(self, key, val):
		self.tags[key] = val

	def get_tag(self, key):
		try:
			return self.tags[key]
		except KeyError:
			return None


class MainFrame(tk.Frame):
	def __init__(self, controller, parent):
		tk.Frame.__init__(self, parent)
		
		self.controller = controller
		self.parent = parent
		
		self.string_vars = {}

		self.vars_list = sorted(['Race', 'Sex', 'Occupation', 'Level', 'Uncapped Abilities'])
		self.var_choices = 	{
								'Race':sorted(self.controller.resource_loader.get_list('races')), 
								'Sex':['Male', 'Female'], 
								'Occupation':['--CLASSES--', *sorted(self.controller.resource_loader.get_list('classes')), '--JOBS--', *sorted(self.controller.resource_loader.get_list('jobs'))],
								'Level':[*list(map((str), np.arange(1, 21))), '--Low (1-4)--', '--Medium (5-9)--', '--High (10-20)--'],
								'Uncapped Abilities':['True', 'False']
							}

		self.createGUI()

	def createGUI(self):
		self.canvas = tk.Canvas(self, width=1430, height=800, highlightthickness=0)
		self.canvas.place(relx=0, rely=0, anchor='nw')

		for var in self.vars_list:
			lbl = tk.Label(self, text=var, font=('gothic', 18))
			lbl.place(relx=0.1, rely=((0.1 + self.vars_list.index(var)/8)-0.035), anchor='c')

			string_var = tk.StringVar(self, '--Random--')
			self.string_vars[var] = string_var
			
			opt_m = tk.OptionMenu(self, string_var, *['--Random--', *self.var_choices[var]])
			opt_m.config(font=('gothic', 18), width=20)
			opt_m.place(relx=0.1, rely=(0.1 + self.vars_list.index(var)/8), anchor='c')

		# self.description = self.canvas.create_text(350, 50, anchor='nw', text=f"Description:\n", font=('gothic', 18), width=500) 

		self.canvas.create_line(300, 0, 300, 800, fill="black", width=20)
		self.canvas.create_line(867, 0, 867, 800, fill="#750E00", width=10)

		gen_btn = tk.Button(self, text='Generate', font=('Good Times', 30), fg='#9b0707', relief='groove', command=self.controller.generate)
		gen_btn.place(relx=0.1, rely=0.9, anchor='c')


class Generator():
	def __init__(self, parent):
		self.parent = parent
		self.frames = {}

		self.resource_loader = ResourceLoader()

		self.NPCs = []

		self.createGUI()

	def createGUI(self):
		self.parent.title('5e NPC Generator')
		self.parent.geometry('1430x800')

		container = tk.Frame(self.parent)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		## could add more frames here with for-loop
		frame = MainFrame(self, container)
		self.frames[MainFrame.__name__] = frame
		frame.grid(row=0, column=0, sticky='nsew')

		self.show_frame('MainFrame')

	def generate(self):
		child = self.frames['MainFrame']

		npc = NPC()

		rng = npc.rng_object.get_rng()

		## BASIC ATTRIBUTES FOR NPC: LEVEL, OCCUPATION, RACE, SEX, UNCAPPED ABILITIES
		for opt_var in child.vars_list:
			str_var = child.string_vars[opt_var].get()
			
			if str_var == "--Random--":
				list_ = []

				for obj in child.var_choices[opt_var]:
					if obj[0] != "-":
						list_.append(obj)

				var = rng.choice(list_)

			else:				
				if str_var[0] == "-":
					if opt_var == 'Level':	
						levels = {'L':(4, 1), 'M':(5, 5), 'H':(11, 10)}
						var = np.floor(rng.random()*levels[str_var[2]][0]+levels[str_var[2]][1]).astype('int')
					elif opt_var == 'Occupation':
						var = rng.choice(sorted(self.resource_loader.get_list(str_var[2:-2].lower())))
				else:
					var = str_var
				

			npc.set_tag(opt_var, var)


		## CLASS OR NOT
		npc.set_tag('class_bool', npc.get_tag('Occupation') in self.resource_loader.get_list('classes'))


		## PROFICIENCY BONUS
		npc.set_tag('proficiency_bonus', 2 + (int(npc.get_tag('Level'))-1)//4)


		## SUBRACE
		npc.set_tag('Subrace', self.resource_loader.get_subrace(rng, npc.get_tag('Race')))


		## ABILITIES
		npc.set_tag('Abilities', self.generate_abilities(npc, rng))


		## APPEARENCE 
		appr = self.resource_loader.get_appearances(rng, npc.get_tag('Race'), npc.get_tag('Subrace'))

		npc.set_tag('Appearance', {k:v for k, v in appr.items() if 'base' not in k and 'mod' not in k})


		### HEIGHT AND WEIGHT
		h = round(int(appr['height_base'][0]) + int(appr['height_mod'][0])*2.54)
		w = round(int(appr['weight_base'][0]) + ((int(appr['weight_mod'][0]) * int(appr['height_mod'][0]))*0.45))
		w_max = round(int(appr['weight_base'][0]) + ((int(appr['weight_mod'][1][1]) * int(appr['height_mod'][1][1]))*0.45))

		npc.set_tag('Height', f"{h} cm")

		w_dict = {0.4:'light', 0.7:'medium', 10:'heavy'}
		w_cat = ''

		for bin_ in w_dict:
			if (w-int(appr['weight_base'][0]))/(w_max-int(appr['weight_base'][0])) <= bin_:
				w_cat = w_dict[bin_]
				break

		npc.set_tag('Weight', f"{w} kg ({w_cat})")

		### OTHER APPEARENCES  

		# xml.get_appearence()


		## LANGUAGES AND SPEEDS
		npc.set_tag('Languages', self.resource_loader.get_languages_or_speeds(rng, npc.get_tag('Race'), npc.get_tag('Subrace'), 'lan'))
		npc.set_tag('Speeds', self.resource_loader.get_languages_or_speeds(rng, npc.get_tag('Race'), npc.get_tag('Subrace'), 'spd'))


		## CLASS RELATED AND AC 
		if npc.get_tag('class_bool'):
			## CLASS PROFICIENCIES
			npc.set_tag("Class Proficiencies", self.resource_loader.get_proficiencies(rng, npc.get_tag('Occupation')))

			## WEAPONS AND ARMOR
			npc.set_tag("Weapon", self.resource_loader.get_weapon(rng, npc.get_tag('Class Proficiencies')['weapons']))

			armr_dict = self.resource_loader.get_armor(rng, npc.get_tag('Class Proficiencies')['armor'], npc.get_tag('Abilities')['STR'][0])
			npc.set_tag('Armor', f"Armor: {armr_dict['name']} Armor, Stealth Dis.: {armr_dict['stealth_dis']}")


			## AC
			ac = int(armr_dict['ac']) + npc.get_tag('Abilities')['DEX'][1]

			if 'shield' in npc.get_tag('Class Proficiencies')['armor']:
				if rng.random() <= 0.25:
					ac += 2
					npc.set_tag('Armor', f"{npc.get_tag('Armor')}, Shield: True (+2 to AC)")

			npc.set_tag('AC', ac)

			## !! ADD FEATURES HERE AS WELL

		else:
			npc.set_tag('AC', 10 + npc.get_tag('Abilities')['DEX'][1])


		print("\n"*3, npc.tags)

		img = Image.open(f"Race Screenshots/{npc.get_tag('Subrace')}.png")
		img = img.resize((round(img.width//1.5), min(round(img.height//1.5), 750)))
		self.pImg = ImageTk.PhotoImage(image=img)

		race_desc = child.canvas.create_image(1430, 50, anchor='ne', image=self.pImg)
		race_url = [x for x in npc.get_tag('Subrace') if x not in ('(', ')')]
		# child.canvas.bind('<Button-1>', lambda e: webbrowser.open(f"https://5e.tools/races.html#{''.join(race_url).lower().replace(' ', '_')}", new=2))
		
		# hsv = [rng.random() for _ in range(3)]
		hsv = [0.91, *[rng.random() for _ in range(1)], 0.5]
		rgb = list(map(lambda x: hex(int(x*255))[2:].zfill(2), colorsys.hsv_to_rgb(*hsv)))
		clr = "#" + "".join(rgb)

		print(hsv, rgb, clr)
		a = child.canvas.create_rectangle(1200, 500, 1420, 600, fill=clr)


		
		# s = ""

		# for item in self.vars_dict.items():
		# 	s += f"{item[0]}: {item[1]}\n"

		# if self.vars_dict['Occupation'] not in self.resource_loader.get_list('classes'):
		# 	s += f"\nOccupation Description: {self.resource_loader.get_occupation_description(self.vars_dict['Occupation'])[0]}{self.resource_loader.get_occupation_description(self.vars_dict['Occupation'])[1:].lower()}\n"

		# s += f"Subrace: {self.resource_loader.get_subrace(self.rng, self.vars_dict['Race'])}\n"



		# child.canvas.delete(child.description)
		# child.description = child.canvas.create_text(350, 50, anchor='nw', text=f"Description:\n\n{s}", font=('gothic', 18), width=500) 

	def generate_abilities(self, npc, rng):
		abilities = {'DEX':10, 'STR':10, 'CON':10, 'INT':10, 'WIS':10, 'CHA':10}

		bonuses = self.resource_loader.get_race_ability_bonuses(abilities, rng, npc.get_tag('Race'), npc.get_tag('Subrace'))
		
		for ability in abilities:
			if not npc.get_tag('class_bool'):
				scores = sorted(rng.choice(6, 4)+1)[1:]
			else:
				scores = rng.choice(6, 3)+1

			try:
				var = sum(scores) + int(bonuses[ability])
			except KeyError:
				var = sum(scores)

			score = min(var, 20) if npc.get_tag('Uncapped Abilities') == 'False' else var
			abilities[ability] = (score, (score-10)//2)

		return abilities

	def show_frame(self, frame_name):
		self.frames[frame_name].tkraise()

	def start(self):
		self.parent.mainloop()

Generator(tk.Tk()).start()