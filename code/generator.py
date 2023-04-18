import tkinter as tk
from numpy.random import default_rng, SeedSequence
import numpy as np
from PIL import Image, ImageTk
import webbrowser
import colorsys

from resource_loader import ResourceLoader

class Rng():
	def __init__(self):
		self.seed = SeedSequence().entropy
		self.rng = default_rng(seed=self.seed)

	def get_rng(self):
		return self.rng

	def get_seed(self):
		return self.seed

 				

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

		self.vars_list = (['Level', 'Occupation', 'Race', 'Sex', 'Uncapped Abilities', 'Only Class Specific Spells', 'Number of Traits'])
		self.var_choices = 	{
								'Race':sorted(self.controller.resource_loader.get_list('races')), 
								'Sex':['Male', 'Female'], 
								'Occupation':['--CLASSES--', *sorted(self.controller.resource_loader.get_list('classes')), '--JOBS--', *sorted(self.controller.resource_loader.get_list('jobs'))],
								'Level':[*list(map((str), np.arange(1, 21))), '--Low (1-4)--', '--Medium (5-9)--', '--High (10-20)--', '--Crazy (21-100)--', '--Why? (101-1000)--'],
								'Uncapped Abilities':['True', 'False'],
								'Only Class Specific Spells':['True', 'False'],
								'Number of Traits':[*list(map(str, np.arange(1, 11)))]
							}

		self.createGUI()

	def createGUI(self):
		self.canvas = tk.Canvas(self, width=1430, height=800, highlightthickness=0)
		self.canvas.place(relx=0, rely=0, anchor='nw')

		for var in self.vars_list:
			lbl = tk.Label(self, text=var, font=('gothic', 18))
			lbl.place(relx=0.1, rely=((0.1 + self.vars_list.index(var)/10)-0.035), anchor='c')

			string_var = tk.StringVar(self, '--Random--')
			self.string_vars[var] = string_var
			
			opt_m = tk.OptionMenu(self, string_var, *['--Random--', *self.var_choices[var]])
			opt_m.config(font=('gothic', 18), width=20)
			opt_m.place(relx=0.1, rely=(0.1 + self.vars_list.index(var)/10), anchor='c')

		# self.description = self.canvas.create_text(350, 50, anchor='nw', text=f"Description:\n", font=('gothic', 18), width=500) 

		self.canvas.create_line(300, 0, 300, 800, fill="black", width=20)
		# self.canvas.create_line(867, 0, 867, 800, fill="#750E00", width=10)

		gen_btn = tk.Button(self, text='Generate', font=('Good Times', 30), fg='#9b0707', relief='groove', command=self.controller.generate)
		gen_btn.place(relx=0.1, rely=0.9, anchor='c')


class Generator():
	def __init__(self, parent):
		self.parent = parent
		self.frames = {}

		self.resource_loader = ResourceLoader.get_instance()

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

		npc.set_tag('rng', npc.rng_object.get_seed())

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
						levels = {'L':(4, 1), 'M':(5, 5), 'H':(11, 10), 'C':(80, 21), 'W':(900, 101)}
						var = np.floor(rng.random()*levels[str_var[2]][0]+levels[str_var[2]][1]).astype('int')
					elif opt_var == 'Occupation':
						var = rng.choice(sorted(self.resource_loader.get_list(str_var[2:-2].lower())))
				else:
					var = str_var
				
			if opt_var == 'Level' or opt_var == 'Number of Traits':
				npc.set_tag(opt_var, int(var))
			elif opt_var == 'Uncapped Abilities' or opt_var == 'Only Class Specific Spells':
				var = True if var == 'True' else False
				npc.set_tag(opt_var, var)
			else:
				npc.set_tag(opt_var, var)


		## CLASS OR NOT
		npc.set_tag('class_bool', npc.get_tag('Occupation') in self.resource_loader.get_list('classes'))


		## PROFICIENCY BONUS
		npc.set_tag('proficiency_bonus', 2 + (npc.get_tag('Level')-1)//4)


		## SUBRACE
		npc.set_tag('Subrace', self.resource_loader.get_subrace(rng, npc.get_tag('Race')))


		## ABILITIES
		npc.set_tag('Abilities', self.generate_abilities(rng, npc))
		### ABILITY SCORE IMPROVEMENTS
		npc.set_tag('Abilities', self.add_asi_and_feats(rng, npc))


		## APPEARENCE AND TRAITS
		appr = self.resource_loader.get_appearances(rng, npc.get_tag('Race'), npc.get_tag('Subrace'))

		npc.set_tag('Appearance', {k:v for k, v in appr.items() if 'base' not in k and 'mod' not in k})

		### TRAITS
		npc.set_tag('Traits', self.resource_loader.get_traits(rng, npc.get_tag('Number of Traits')))


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

		### OTHER APPEARENCES LIKE EYE COLOR AND ALL THAT BS

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

			## SUBCLASS
			npc.set_tag('Subclass', self.resource_loader.get_subclass(rng, npc.get_tag('Occupation')))

			## CLASS FEATURES
			npc.set_tag('Features', self.resource_loader.get_class_features(rng, npc.get_tag('Occupation'), npc.get_tag('Subclass'), npc.get_tag('Level')))


	
		

		## AC AND HP
		### AC
		if npc.get_tag('class_bool'):
			ac = int(armr_dict['ac']) + npc.get_tag('Abilities')['DEX'][1]

			if 'shield' in npc.get_tag('Class Proficiencies')['armor']:
				if rng.random() <= 0.25:
					ac += 2
					npc.set_tag('Armor', f"{npc.get_tag('Armor')}, Shield: True (+2 to AC)")

			npc.set_tag('AC', ac)
		else:
			npc.set_tag('AC', 10 + npc.get_tag('Abilities')['DEX'][1])

		### HP
		die = 8 if 'medium' in npc.get_tag('Appearance')['size'][0] else 6
		hp = np.array(rng.choice(die, npc.get_tag('Level')) + 1) + npc.get_tag('Abilities')['CON'][1]
		
		npc.set_tag('Hit Points', sum(hp))



		print("\n"*3, npc.tags)



		img = Image.open(f"Race Screenshots/{npc.get_tag('Subrace')}.png")
		img = img.resize((min(round(img.width//1.5), 850), min(round(img.height//1.5), 750)))
		self.p_img = ImageTk.PhotoImage(image=img)

		race_desc = child.canvas.create_image(1430, 50, anchor='ne', image=self.p_img)
		race_url = [x for x in npc.get_tag('Subrace') if x not in ('(', ')')]

		# child.canvas.bind('<Button-1>', lambda e: webbrowser.open(f"https://5e.tools/races.html#{''.join(race_url).lower().replace(' ', '_')}", new=2))



		# child.canvas.bind('<Button-1>', lambda e: webbrowser.open(f"https://www.fantasynamegenerators.com/dnd-{npc.get_tag('Race').lower().replace(' ', '-')}-names.php", new=2))
		




		# hsv = [*[rng.random() for _ in range(2)], min(rng.random()+0.4, 1)]
		# hsv = [rng.random(), 0.5, rng.random()]
		# rgb = list(map(lambda x: hex(int(x*255))[2:].zfill(2), colorsys.hsv_to_rgb(*hsv)))
		# clr = "#" + "".join(rgb)

		# print(hsv, rgb, clr)
		# a = child.canvas.create_rectangle(1200, 500, 1420, 600, fill=clr)


		
		# s = ""

		# for item in self.vars_dict.items():
		# 	s += f"{item[0]}: {item[1]}\n"

		# if self.vars_dict['Occupation'] not in self.resource_loader.get_list('classes'):
		# 	s += f"\nOccupation Description: {self.resource_loader.get_occupation_description(self.vars_dict['Occupation'])[0]}{self.resource_loader.get_occupation_description(self.vars_dict['Occupation'])[1:].lower()}\n"

		# s += f"Subrace: {self.resource_loader.get_subrace(self.rng, self.vars_dict['Race'])}\n"



		# child.canvas.delete(child.description)
		# child.description = child.canvas.create_text(350, 50, anchor='nw', text=f"Description:\n\n{s}", font=('gothic', 18), width=500) 

	def generate_abilities(self, rng, npc):
		abilities = {'DEX':10, 'STR':10, 'CON':10, 'INT':10, 'WIS':10, 'CHA':10}

		bonuses = self.resource_loader.get_race_ability_bonuses(abilities, rng, npc.get_tag('Race'), npc.get_tag('Subrace')) 
		
		for ability in abilities:
			if npc.get_tag('class_bool'):
				rolls = sorted(rng.choice(6, 4)+1)[1:]
			else:
				rolls = rng.choice(6, 3)+1

			try:
				var = sum(rolls) + int(bonuses[ability])
			except KeyError:
				var = sum(rolls)

			score = min(var, 20) if not npc.get_tag('Uncapped Abilities') else var
			abilities[ability] = (score, (score-10)//2)

		return abilities

	def add_asi_and_feats(self, rng, npc):
		bonuses = {'DEX':0, 'STR':0, 'CON':0, 'INT':0, 'WIS':0, 'CHA':0}

		lvls = np.arange(npc.get_tag('Level'))+1
		
		if npc.get_tag('Occupation') == 'Fighter':
			lvls.extend([6, 14])
		if npc.get_tag('Occupation') == 'Rogue':
			lvls.extend([10])

		lvls = [not bool(x % 4) for x in sorted(lvls)]
 
		choices = ['feat', '2', '1+1', '3+-1']
		feats = self.resource_loader.get_feat(rng)

		npc_feats = {}
		
		for lvl in np.arange(npc.get_tag('Level')):
			if lvls[lvl]:
				choice = rng.choice(choices)
				if choice == 'feat':
					try:
						feat = feats[rng.choice(np.arange(len(feats)))]
					except ValueError: ## if len(feats) > num_feats
						continue

					feat_data = self.resource_loader.get_feat_data(rng, feat, npc)
					if 'asi' in feat_data.keys():
						bonuses[feat_data['asi'][0]] += int(feat_data['asi'][1])

					npc_feats[feat_data['name']] = {k:feat_data[k] for k in feat_data.keys() if k not in ('name', 'asi')}
					feats.remove(feat)

				else:
					aa = choice.split('+')
					for ab in aa:
						bonuses[rng.choice(list(bonuses.keys()))] += int(ab)
		
		if npc_feats != {}:
			npc.set_tag('feats', npc_feats)
		
		final = {}
		for ability in bonuses:
			var = npc.get_tag('Abilities')[ability][0] + bonuses[ability]
			score = min(var, 20) if not npc.get_tag('Uncapped Abilities') else var

			final[ability] = (score, (score-10)//2)

		return final

	def show_frame(self, frame_name):
		self.frames[frame_name].tkraise()

	def start(self):
		self.parent.mainloop()

Generator(tk.Tk()).start()