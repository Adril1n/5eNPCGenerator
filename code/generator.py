import tkinter as tk
from numpy.random import default_rng, SeedSequence
import numpy as np
from PIL import Image, ImageTk
import webbrowser
import colorsys

from functools import partial
import tkinter.scrolledtext as scrolledtext


from resource_loader import ResourceLoader






def darken_color(color, factor):
	r = hex(int(int(color[1:3], 16) * min(max(factor, 0), 1)))[2:]
	g = hex(int(int(color[3:5], 16) * min(max(factor, 0), 1)))[2:]
	b = hex(int(int(color[5:7], 16) * min(max(factor, 0), 1)))[2:]

	return f"#{r.zfill(2)}{g.zfill(2)}{b.zfill(2)}"





class Formating():
	FONT_HEADER_BOLD = ('Arial-BoldMT', 20)
	FONT_DESC_BOLD = ('Arial-BoldMT', 16)

	FONT_ABILITY_TYPE = ('Arial-BoldMT', 12)
	FONT_ABILITY_MODIFIER = ('Arial', 40)
	FONT_ABILITY_SCORE = ('Arial', 22)

	@staticmethod
	def create_desc_box(canvas, desc_type, clr, detail_clr):
		x1 = canvas.bbox(canvas.find_withtag(f'text&&{desc_type}&&key')[0])[0]-5
		y1 = canvas.bbox(canvas.find_withtag(f'text&&{desc_type}&&key')[0])[1]-50
		x2 = max(list(map(lambda x: canvas.bbox(x)[2], canvas.find_withtag(f'text&&{desc_type}&&value'))))+5
		y2 = canvas.bbox(canvas.find_withtag(f'text&&{desc_type}&&key')[-1])[3]+5

		background = canvas.create_rectangle(x1, y1, x2, y2, fill=darken_color(clr, 0.3), outline=detail_clr, width=4, tags=['background', 'statblock', desc_type])
		header = canvas.create_rectangle(*canvas.bbox(background)[:3], canvas.bbox(background)[1]+40, fill=detail_clr, width=0, tags=['background', 'header', 'statblock', desc_type])
		
		header_middle_x = (canvas.bbox(header)[0]+canvas.bbox(header)[2])//2
		header_middle_y = (canvas.bbox(header)[1]+canvas.bbox(header)[3])//2
		txt = f"{desc_type.title()}s" if desc_type != 'ability' else 'Abilities'
		header_text = canvas.create_text(header_middle_x, header_middle_y, text=txt, justify=tk.CENTER, font=Formating.FONT_HEADER_BOLD, tags=['background', 'header', 'text', 'statblock', desc_type])

		divider_x1 = max([canvas.bbox(desc_type)[2] for desc_type in canvas.find_withtag(f'text&&{desc_type}&&key')])
		divider = canvas.create_rectangle(divider_x1+8, canvas.bbox(header)[3]-int(float(canvas.itemcget(background, "width"))), divider_x1+18, canvas.bbox(background)[3], fill=detail_clr, width=0, tags=['background', 'statblock', 'divide', desc_type])






# class Stat():
# 	def __init__(self, name, value):
# 		self.name = name
# 		self.value = value

# 	def format(self, canvas, index, summary_x1, summary_x2, fill_clr='#000000', outline_clr='#FFFFFF'):
# 		y = (index//2+1)*140
# 		x = [summary_x1, summary_x2][index%2]-[0, 100][index%2]

# 		background = canvas.create_rectangle(x, y, x+100, y+100, fill=fill_clr, outline=outline_clr, width=3, tags=['background'])

# 		background_x1 = (canvas.bbox(background)[0]+canvas.bbox(background)[2])//2
# 		txt_0 = canvas.create_text(background_x1, canvas.bbox(background)[1]+10, anchor='n', text=self.name.split(' ')[0], font=('Arial-BoldMT', 16))

# 		main_str = f"+{self.value}" if 'Bonus' in self.name else self.value
# 		if 'Speed' in self.name:
# 			main_str = f"{self.value} ft."

# 		txt_main = canvas.create_text(background_x1-1, (canvas.bbox(background)[1]+canvas.bbox(background)[3])//2, anchor='c', text=main_str, font=('Arial', 40))

# 		try:
# 			txt_1 = canvas.create_text(background_x1, canvas.bbox(background)[3]-10, anchor='s', text=self.name.split(' ')[1], font=('Arial-BoldMT', 16))
# 		except IndexError:
# 			pass

class Action():
	def __init__(self, a_type, a_dict):
		self.a_type = a_type
		self.a_dict = a_dict

	def __repr__(self):
		return f"{self.a_type, self.a_dict}"



class Ability():
	TYPES = ['STRENGTH', 'DEXTERITY', 'CONSTITUTION', 'INTELLIGENCE', 'WISDOM', 'CHARISMA']

	def __init__(self, name, parent):
		self.name = name
		self.parent = parent
		self.score = self.score_init()

	def score_init(self):
		rng = self.parent.rng

		if self.parent.cls_bool:
			score = sum(sorted(rng.choice(6, 4)+1)[1:])
		else:
			score = sum(rng.choice(6, 3)+1)

		return score ## max score == 18

	def add_bonus(self, bonus):
		new_score = self.score + int(bonus)
		self.score = max(min(new_score, 20), 1) if not self.parent.options['uncapped_abilities'].value else new_score

	def get_modifier(self):
		return (self.score-10)//2

	def format(self, canvas, preview=True, x_anchor=1000, y_anchor=60, val_dist=225, fill_clr='#00FF00', outline_clr='#BB66FF'):
		if preview:
			if self.name == Ability.TYPES[0]:
				canvas.create_text(x_anchor, y_anchor, text=self.name, anchor='nw', font=Formating.FONT_DESC_BOLD, tags=['text', 'ability', 'key'])
			else:
				canvas.create_text(canvas.bbox(canvas.find_withtag('text&&ability&&key')[-1])[0]+1, canvas.bbox(canvas.find_withtag('text&&ability&&key')[-1])[3]+10, text=self.name, anchor='nw', font=Formating.FONT_DESC_BOLD, tags=['text', 'ability', 'key'])
			
			modifier = self.get_modifier()
			modifer_txt = f'+{modifier}' if modifier > 0 else modifier
			canvas.create_text(x_anchor+val_dist, canvas.bbox(canvas.find_withtag('text&&ability&&key')[-1])[1], text=f"{self.score} [{modifer_txt}]", anchor='ne', font=('Arial', 16), tags=['text', 'ability', 'value'])
		else:
			dim = 100

			if self.name == Ability.TYPES[0]:
				x = x_anchor
				y = y_anchor
			else:
				x = canvas.bbox(canvas.find_withtag('background&&ability')[-1])[2]+dim//2
				y = canvas.bbox(canvas.find_withtag('background&&ability')[-1])[1]+2

			background = canvas.create_rectangle(x, y, x+dim, y+dim, fill=fill_clr, outline=outline_clr, width=3, tags=['background', 'ability'])
			type_ = canvas.create_text(x+dim//2, y+3, anchor='n', text=self.name, font=Formating.FONT_ABILITY_TYPE, tags=['text'])

			modifier = self.get_modifier()
			modifer_txt = f'+{modifier}' if modifier > 0 else modifier
			canvas.create_text(x+dim//2, y+20, anchor='n', text=modifer_txt, font=Formating.FONT_ABILITY_MODIFIER, tags=['text'])

			canvas.create_text(x+dim//2, y+dim-3, anchor='s', text=self.score, font=Formating.FONT_ABILITY_SCORE, tags=['text'])

	def __repr__(self):
		return f"{self.score, self.get_modifier()}"


class Option():
	def __init__(self, key, value, index):
		self.key = key
		self.value = value
		self.index = index

	def format(self, canvas, x_anchor=350, y_anchor=60, val_dist=225):
		if self.index == 0:
			canvas.create_text(x_anchor, y_anchor, text=f"{self.key.replace('_', ' ').title()}", anchor='nw', font=Formating.FONT_DESC_BOLD, tags=['text', 'option', 'key'])
		else:
			canvas.create_text(canvas.bbox(canvas.find_withtag('text&&option&&key')[-1])[0]+1, canvas.bbox(canvas.find_withtag('text&&option&&key')[-1])[3]+10, text=f"{self.key.replace('_', ' ').title()}", anchor='nw', font=Formating.FONT_DESC_BOLD, tags=['text', 'option', 'key'])
		
		canvas.create_text(x_anchor+val_dist, canvas.bbox(canvas.find_withtag('text&&option&&key')[-1])[1], text=f"{self.value}", anchor='nw', font=('Arial', 16), tags=['text', 'option', 'value'])



class NPC():
	LANGUAGES = [	'Aarakocran', 'Abyssal', 'Aquan', 'Auran', 'Blink', 'Bothii', 'Bullywug', 'Celestial', 'Common', 'Deep', 'Dog', 'Draconic', 
					'Dwarvish', 'Eagle', 'Elk', 'Elvish', 'Giant', 'Giant', 'Giant', 'Giant', 'Gith', 'Gnoll', 'Gnomish', 'Goblin', 'Grell', 
					'Grung', 'Hadozee', 'Halfling', 'Hook', 'Horror', 'Hulk', 'Ignan', 'Infernal', 'Ixitxachitl', 'Kothian', 'Kraul', 'Kruthik', 
					'Leonin', 'Loxodon', 'Merfolk', 'Minotaur', 'Modron', 'Olman', 'Orc', 'Otyugh', 'Owl', 'Primal', 'Primordial', 'Sahuagin', 
					'Skitterwidget', 'Slaad', 'Speech', 'Sphinx', 'Sylvan', 'Tasloi', 'Terran', 'Thri-Kreen', 'Tlincalli', 'Troglodyte', 'Umber', 
					'Undercommon', 'Vedalken', 'Vegepygmy', 'Winter', 'Wolf', 'Worg', 'Yeti', 'Yikaria'
				]

	def __init__(self, rng_obj, options):
		self.rng = rng_obj.rng
		self.seed = rng_obj.seed

		self.options = {k:Option(k, v, list(options.keys()).index(k)) for k, v in options.items()}
		self.cls_bool = self.options['occupation'].value in ResourceLoader.get_instance().get_list('classes')
		
		self.abilities = {ability_type:Ability(ability_type, self) for ability_type in Ability.TYPES}

		

		# self.generate_base()
		self.generate()

		# self.generate_ac_initiative()

	def generate(self):
		race = self.options['race'].value
		sex = self.options['sex'].value
		occupation = self.options['occupation'].value

		RL = ResourceLoader.get_instance()
		
		## NAME
		try:
			self.name = self.rng.choice(RL.get_name_list(race, sex))
		except ValueError as e:
			print("No names for that race currently. Maybe you didn't update names.xml using name_automator.py.", f'"{e}"')
			self.name = '???'

		## RACE TYPE
		self.race_type = self.rng.choice(RL.get_race_type_choices(race))

		## RACE ABILITY SCORE IMPROVEMENT
		race_asi = RL.get_race_asi(race, self.race_type)
		self.apply_race_asi_bonuses(race_asi)

		## SIZE, BASE_SPEEDS, LANGUAGES
		self.size = self.rng.choice(RL.get_size(race, self.race_type).split(';'))

		self.base_speeds = {'walking':'30', 'flying':None, 'swimming':None}
		self.base_speeds.update(RL.get_speeds(race, self.race_type))

		self.languages = RL.get_languages(race, self.race_type)

		for lan in self.languages:
			if lan == 'random':
				language_choices = NPC.LANGUAGES.copy()
				index = self.languages.index(lan)
				[language_choices.remove(a) for a in self.languages[:index]]
				self.languages[index] = self.rng.choice(language_choices)

		self.darkvision = RL.get_darkvision(race, self.race_type)


		## APPEARENCES; HEIGHT, WEIGHT, AGE
		height_weight_dict = RL.get_height_weight(race, self.race_type)

		self.height = self.get_height_weight_value(height_weight_dict, 'height')
		self.weight = self.get_height_weight_value(height_weight_dict, 'weight')


		age_list = RL.get_age(race, self.race_type)
		self.age = self.rng.integers(int(age_list[0]), high=int(age_list[1])+1)


		## RACIAL FEATURES AND ACTIONS
		self.racial_features = RL.get_racial_features(race, self.race_type)

		self.race_actions = {k:Action(v[0], v[1]) for k, v in RL.get_race_actions(race, self.race_type).items() if int(v[1]['level_req']) <= self.options['level'].value}


		## ASI AND FEATS
		if self.cls_bool: # MAYBE KEEP THIS
			self.add_asi_and_feats()


		## BASE CLASS PROFICIENCIES 
		self.proficiencies = RL.get_base_class_proficiencies(occupation)

		tools = self.proficiencies['tools'].copy()
		for tool in tools:
			if tool == 'random':
				tool_list = RL.get_equipment_list('tool')
				tool_choices = [t['name'] for t in tool_list]

				index = tools.index(tool)
				[tool_choices.remove(a) for a in tools[:index]]
				tools[index] = self.rng.choice(tool_choices)

				self.proficiencies['tools'] = tools

		skill_list = RL.get_equipment_list('skill')
		skill_choices = [s['name'] for s in skill_list]

		self.proficiencies['skills'] = list(self.rng.choice(skill_choices, size=int(self.proficiencies['skills'][0]), replace=False))

		# h_mod_split = list(map(int, height_weight_dict[f'height_modifier'].split('d')))
		# # h_mod = sum(self.rng.choice(h_mod_split[1], h_mod_split[0])+1)
		# h_mod = sum(list(map(lambda x: max(x, 1), self.rng.random(h_mod_split[0])*h_mod_split[1])))
		
		# self.height = int(height_weight_dict['height_base']) + h_mod*2.54


		# w_mod_split = list(map(int, height_weight_dict[f'weight_modifier'].split('d')))
		# # w_mod = sum(self.rng.choice(w_mod_split[1], w_mod_split[0])+1)
		# w_mod = sum(list(map(lambda x: max(x, 1), self.rng.random(w_mod_split[0])*w_mod_split[1])))

		# self.weight = int(height_weight_dict['weight_base']) + ((w_mod*h_mod)*0.45)



		


	def get_height_weight_value(self, dict_, t):
		mod_split = list(map(int, dict_[f'{t}_modifier'].split('d')))
		mod = sum(list(map(lambda x: max(x, 1), self.rng.random(mod_split[0])*mod_split[1]))) # sum(self.rng.choice(mod_split[1], mod_split[0])+1) for only 1-6 ints


		mod = mod*2.54 if t == 'height' else mod

		base = int(dict_[f'{t}_base'])
		if t == 'height':
			return round(base + mod)
		else:
			return round(base + ((self.height-int(dict_['height_base']))/2.54*mod)*0.45)



	def get_weight_bin(self):
		w_bins = {0.25:'light', 0.7:'medium', 10:'heavy'}
		w_bin = ''
		
		h_w_dict = ResourceLoader.get_instance().get_height_weight(self.options['race'].value, self.race_type)
		
		h_mod = list(map(int, h_w_dict['height_modifier'].split('d')))
		w_mod = list(map(int, h_w_dict['weight_modifier'].split('d')))

		w_max = int(h_w_dict['weight_base']) + (h_mod[0]*h_mod[1] * w_mod[0]*w_mod[1])*0.45

		for bin_ in w_bins:
			if (self.weight-int(h_w_dict['weight_base']))/(w_max-int(h_w_dict['weight_base'])) <= bin_:
				return w_bins[bin_]
				

	def get_age_bin(self):
		age_bins = {0.35:'Young', 0.75:'Middle Aged', 10:'Elderly'}

		for bin_ in age_bins:
			if self.age/int(ResourceLoader.get_instance().get_age(self.options['race'].value, self.race_type)[1]) <= bin_: ## probably a bit wrong since self.age is restricted to [3, 30] for Aarakocra and max_age == 30 
				return age_bins[bin_]

		

	def get_proficiency_bonus(self):
		return 2 + (self.options['level'].value-1)//4

	def get_hit_points(self):
		die = 8 if self.size == 'medium' else 6
		hp_arr = np.array(self.rng.choice(die, self.options['level'].value) + 1) + self.abilities['CONSTITUTION'].get_modifier()
		return max(sum(hp_arr), 1)

	def get_intiative_bonus(self):
		dex_mod = self.abilities['DEXTERITY'].get_modifier()
		initiative = f"+{dex_mod}" if dex_mod > 0 else dex_mod
		return initiative

	def get_speeds(self):
		speeds = {}
		for k, v in self.base_speeds.items():
			speeds[f"{k.title()} Speed"] = v if v is not None else int(self.base_speeds['walking'])//2

		return speeds

	def get_skill(self, name):
		skill_dict = ResourceLoader.get_instance().get_equipment_list('skill')
		skill_list = {s['name']:s['ability'] for s in skill_dict}

		for skill in skill_list:
			if skill == name:
				value = 10 + self.abilities[skill_list[skill]].get_modifier()
				value += self.get_proficiency_bonus() if skill in self.proficiencies['skills'] else 0

				return value

		return 0




	def apply_race_asi_bonuses(self, race_asi):
		for key, value in race_asi.items():
			if key == 'lineage':
				choice = self.rng.choice(['2+1', '1+1+1'])
				ability_types = Ability.TYPES.copy()

				for value in choice.split('+'):
					ability_choice = self.rng.choice(ability_types)
					self.abilities[ability_choice].add_bonus(value)
					ability_types.remove(ability_choice)

			elif key == 'choose':
				ability_types = Ability.TYPES.copy()
				try:
					ability_types.remove(list(race_asi.keys())[0])
				except ValueError:
					pass

				range_bonus = value.split(';')

				for _ in range(int(range_bonus[0])):
					ability_choice = self.rng.choice(ability_types)
					self.abilities[ability_choice].add_bonus(range_bonus[1])
					ability_types.remove(ability_choice)

			elif key == 'pick':
				choices = value.split(';')[:2]
				self.abilities[self.rng.choice(choices)].add_bonus(value.split(';')[2])

			else:
				self.abilities[key].add_bonus(value)

	def add_asi_and_feats(self):
		lvls = np.arange(self.options['level'].value)+1
		extras = {'Fighter':[6, 14], 'Rogue':[10]}

		lvls = [not bool(x % 4) for x in sorted(lvls)]

		try:
			for extra in extras[self.options['occupation'].value]:
				lvls = np.delete(lvls, extra)
				lvls = np.insert(lvls, extra-1, True)
				
		except KeyError:
			pass


		choices = {'feat':0.25, '2':0.375, '1+1':0.375}

		for lvl in np.arange(self.options['level'].value):
			if lvls[lvl]:
				choice = self.rng.choice(list(choices.keys()), p=list(choices.values()))
				if choice == 'feat':
					## ADD FEATS HERE LATER
					continue
				else:
					for bonus in choice.split('+'):
						self.abilities[self.rng.choice(Ability.TYPES)].add_bonus(bonus)


		#GET HEALTH/AC
	# def generate_ac_initiative(self):
	# 	ac = 10
	# 	self.stats['Armor Class'] = Stat('Armor Class', ac)

	# 	self.initiative = self.abilities['DEXTERITY'].modifier
	# 	self.stats['Initiative'] = Stat('Initiative', self.initiative)


	def to_html(self):
		return 'Hello'
 


class MainFrame(tk.Frame):
	def __init__(self, controller, parent):
		tk.Frame.__init__(self, parent)
		
		self.controller = controller
		self.parent = parent
		
		self.opt_string_vars = {}

		self.opt_list = ['Race', 'Occupation', 'Sex', 'Level', 'Uncapped Abilities', 'Only Class Specific Spells']
		self.opt_choices = 	{
								'Race':sorted(self.controller.resource_loader.get_list('races')), 
								'Occupation':['--CLASSES--', *sorted(self.controller.resource_loader.get_list('classes')), '--JOBS--', *sorted(self.controller.resource_loader.get_list('jobs'))],
								'Sex':['Male', 'Female'], 
								'Level':[*list(map(str, np.arange(1, 21))), '--Low (1-4)--', '--Medium (5-9)--', '--High (10-20)--', '--Crazy (21-1000)--'],
								'Uncapped Abilities':['True', 'False'],
								'Only Class Specific Spells':['True', 'False']
							}

		self.createGUI()

	def createGUI(self):
		self.canvas = tk.Canvas(self, width=1430, height=800, highlightthickness=0)
		self.canvas.place(x=0, y=0, anchor='nw')

		clr = "#" + "".join(list(map(lambda x: hex(int(x*255))[2:].zfill(2), np.random.random((3, )))))

		for opt in self.opt_list:
			lbl = tk.Label(self, text=opt, font=('Arial', 18))
			lbl.place(relx=0.1, rely=((0.1 + self.opt_list.index(opt)/10)-0.035), anchor='c')

			string_var = tk.StringVar(self, '--Random--')
			self.opt_string_vars[opt] = string_var
			
			opt_m = tk.OptionMenu(self, string_var, *['--Random--', *self.opt_choices[opt]])
			opt_m.config(font=('Arial', 18), width=20)
			opt_m.place(relx=0.1, rely=(0.1 + self.opt_list.index(opt)/10), anchor='c')


		self.gen_btn = tk.Button(self, text='Generate', font=('Good Times', 30), fg=darken_color(clr, 0.6), relief='groove', highlightbackground=clr, command=self.controller.generate)
		self.gen_btn.place(relx=0.1, rely=0.93, anchor='c')

		rng_lbl = tk.Label(self, text="RNG Seed Input", font=('Arial', 16))
		rng_lbl.place(relx=0.1, rely=0.83, anchor='s')

		self.rng_ent = tk.Entry(self)
		self.rng_ent.place(relx=0.1, rely=0.85, anchor='c')

		self.divide = self.canvas.create_rectangle(300, -1, 330, 801, fill=darken_color(clr, 0.8), outline=darken_color(clr, 0.65), width=6, tags=["statblock", "keep"])


		self.apply_opt_btn = tk.Button(self, text='Apply', font=Formating.FONT_DESC_BOLD, fg=darken_color(clr, 0.6), highlightbackground=clr, command=self.apply_opt)
		self.apply_opt_btn.place(relx=0.05, rely=0.68, anchor='c')
		self.reset_opt_btn = tk.Button(self, text='Reset', font=Formating.FONT_DESC_BOLD, fg=darken_color(clr, 0.6), highlightbackground=clr, command=self.reset_opt)
		self.reset_opt_btn.place(relx=0.15, rely=0.68, anchor='c')

		self.html_btn = tk.Button(self, text='Open Character Sheet in Safari', font=('Good Times', 45), fg=darken_color(clr, 0.6), highlightbackground=clr, command=self.controller.open_html)
		self.html_btn.place(relx=0.62, rely=0.93, anchor='c')


	def create_preview(self, npc):
		clr = Main.get_instance().clr
		detail_clr = darken_color(clr, 0.5)

		## NAME
		name_text = self.canvas.create_text(830, 35, text=npc.name, font=Formating.FONT_HEADER_BOLD)

		name_x1 = self.canvas.bbox(name_text)[0]-130
		name_y1 = self.canvas.bbox(name_text)[1]-10
		name_x2 = self.canvas.bbox(name_text)[2]+130
		name_y2 = self.canvas.bbox(name_text)[3]+10

		name_background = self.canvas.create_rectangle(name_x1, name_y1, name_x2, name_y2, fill=darken_color(clr, 0.3), outline=detail_clr, width=4, tags=['background', 'statblock', 'name'])

		## OPTIONS
		for option in npc.options:
			npc.options[option].format(self.canvas, x_anchor=400, y_anchor=120, val_dist=225)

		Formating.create_desc_box(self.canvas, 'option', clr, detail_clr)

		## ABILITIES
		for ability in npc.abilities:
			npc.abilities[ability].format(self.canvas, preview=True, x_anchor=1050, y_anchor=120, val_dist=225)

		Formating.create_desc_box(self.canvas, 'ability', clr, detail_clr)


		self.canvas.tag_lower('background')




	def apply_opt(self):
		try:
			for opt in self.opt_list:
				self.opt_string_vars[opt].set(self.controller.current_npc.options[opt.lower().replace(' ', '_')].value)

			self.rng_ent.delete(0, tk.END)
			self.rng_ent.insert(0, self.controller.current_npc.seed)

		except AttributeError:
			print('Failed to apply options, No NPC Generated')


	def reset_opt(self):
		for opt in self.opt_list:
			self.opt_string_vars[opt].set('--Random--')

		self.rng_ent.delete(0, tk.END)
		self.rng_ent.insert(0, '')


# class SheetFrame(tk.Frame):
# 	def __init__(self, controller, parent):
# 		tk.Frame.__init__(self, parent)

# 		self.controller = controller
# 		self.parent = parent

# 		self.createGUI()

# 	def createGUI(self):
# 		self.canvas = tk.Canvas(self, width=1430, height=800, highlightthickness=0)
# 		self.canvas.place(x=0, y=0, anchor='nw')

# 		return_btn = tk.Button(self, text='<<', command=partial(self.controller.change_stage, -1))
# 		return_btn.place(relx=0.05, rely=0.95, anchor='c')

# 		next_page_btn = tk.Button(self, text='>>', command=partial(self.controller.change_stage, 1))
# 		next_page_btn.place(relx=0.1, rely=0.95, anchor='c')

# 	def create_layout(self, npc):
# 		self.outline_clr = Main.get_instance().clr
# 		self.fill_clr = darken_color(self.outline_clr, 0.5)

# 		name = npc.name
# 		sex = npc.options['sex'].value
# 		race = npc.options['race'].value
# 		occupation = npc.options['occupation'].value
# 		level = npc.options['level'].value

# 		## Summary
# 		name_txt = self.canvas.create_text(120, 28, anchor='nw', text=name, font=('Arial', 24), tags=['text'])
# 		name_txt_x1 = self.canvas.bbox(name_txt)[0] + 1

# 		sex_race_txt = self.canvas.create_text(name_txt_x1, self.canvas.bbox(name_txt)[3], anchor='nw', text=f"{sex} {race}", font=('Arial', 16), tags=['text'])
# 		occupation_txt = self.canvas.create_text(self.canvas.bbox(sex_race_txt)[2], self.canvas.bbox(sex_race_txt)[1], anchor='nw', text=f" {occupation}", font=('Arial', 16), tags=['text'])
# 		level_txt = self.canvas.create_text(name_txt_x1, self.canvas.bbox(sex_race_txt)[3], anchor='nw', text=f"Level {level}", font=('Arial', 16), tags=['text'])

# 		summary_bg = self.canvas.create_rectangle(20, 20, self.canvas.bbox(occupation_txt)[2]+13, 100, fill=self.fill_clr, outline=self.outline_clr, width=3, tags=['background'])		


# 		## Proficiencies and Languages
# 		self.create_prof_and_lang()

# 		## Skills
# 		# s_txt = self.canvas.create_text()
	
# 		## Stats
# 		stats = {'Proficiency Bonus':npc.get_proficiency_bonus(), 'Hit Points':npc.get_hit_points(), 'Armor Class':10, 'Intiative':npc.get_intiative_bonus()}
# 		stats.update(npc.get_speeds())

# 		for stat in enumerate(stats):
# 			self.create_stat_background(stat[1], stats[stat[1]], stat[0], summary_bg)

# 		## Abilities
# 		ability_x_anchor = self.canvas.bbox(summary_bg)[2]+50
# 		for ability_type in npc.abilities:
# 			npc.abilities[ability_type].format(self.canvas, preview=False, x_anchor=ability_x_anchor, y_anchor=20, fill_clr=self.fill_clr, outline_clr=self.outline_clr)			





# 		self.canvas.tag_lower('background')

# 	def create_prof_and_lang(self):
# 		npc = self.controller.current_npc

# 		# p_l_txt = self.canvas.create_text(320, 140, anchor='nw', text="Hello"*100, width=250)
# 		p_l_txt = tk.Text(self, width=40, height=30, font=('Arial', 12), bg=self.fill_clr, wrap=tk.WORD, padx=8, pady=8)
# 		p_l_txt.place(x=320, y=140)
# 		# self.canvas.create_rectangle(317, 137, 624, 584, fill=self.fill_clr, outline=self.outline_clr, width=3, tags=['background'])
		
# 		p_l_txt.insert('end', 'Proficiencies and Languages', ('title'))
# 		self.insert_text_break('', p_l_txt)
	
# 		for prof in npc.proficiencies:
# 			p_l_txt.insert('end', f"{prof.title().replace('_', ' ')}\n", ('title', prof))
# 			p_l_txt.insert('end', self.get_proficiency_text(prof, npc), ('text', prof))
# 			self.insert_text_break(prof, p_l_txt)

# 		p_l_txt.insert('end', 'Languages\n', ('title', 'languages'))
# 		p_l_txt.insert('end', ', '.join(npc.languages), ('text', 'languages'))

# 		p_l_txt.tag_configure('title', font=('Arial-BoldMT', 20))
# 		p_l_txt.tag_configure('text', font=('Arial', 14))
# 		p_l_txt.tag_configure('break', font=('Arial', 16))


# 		## Senses
# 		senses_txt = tk.Text(self, width=26, height=8, font=('Arial', 12), bg=self.fill_clr, wrap=tk.WORD, padx=6, pady=6)		
# 		senses_txt.place(x=320, y=600)
# 		# self.canvas.create_rectangle(317, 597, 687, 732, fill=self.fill_clr, outline=self.outline_clr, width=3, tags=['background'])

# 		senses_txt.insert('end', 'Senses\n', ('title'))

# 		for skill in ('Perception', 'Investigation', 'Insight'):
# 			senses_txt.insert('end', npc.get_skill(skill), ('value', 'skill'))
# 			senses_txt.insert('end', f" Passive {skill}\n", ('text', 'skill'))


# 		senses_txt.tag_configure('title', font=('Arial-BoldMT', 22))
# 		senses_txt.tag_configure('value', font=('Arial-BoldMT', 20))
# 		senses_txt.tag_configure('text', font=('Arial', 14))


		


# 	def insert_text_break(self, tag, txt):
# 		txt.insert('end', f"\n{'—'*17}", ('break', tag))

# 	def get_proficiency_text(self, key, npc):
# 		if key != 'tools':
# 			func = lambda x: x.title()  
# 		else: 
# 			func = lambda x: f"{x[0].upper()}{x[1:]} tools"

# 		return ", ".join(list(map(func, npc.proficiencies[key]))) if npc.proficiencies[key] != [] else 'None'

# 	def create_stat_background(self, name, value, index, summary_bg):
# 		x = [self.canvas.bbox(summary_bg)[0], 280][index%2]-[0, 100][index%2]
# 		y = (index//2+1)*140

# 		background = self.canvas.create_rectangle(x, y, x+100, y+100, fill=self.fill_clr, outline=self.outline_clr, width=3, tags=['background'])

# 		background_x1 = (self.canvas.bbox(background)[0]+self.canvas.bbox(background)[2])//2
# 		txt_0 = self.canvas.create_text(background_x1, self.canvas.bbox(background)[1]+10, anchor='n', text=name.split(' ')[0], font=('Arial-BoldMT', 16))

# 		main_str = f"+{value}" if 'Bonus' in name else value
# 		if 'Speed' in name:
# 			main_str = f"{value}ft."

# 		txt_main = self.canvas.create_text(background_x1-1, (self.canvas.bbox(background)[1]+self.canvas.bbox(background)[3])//2, anchor='c', text=main_str, font=('Arial', 40))

# 		try:
# 			txt_1 = self.canvas.create_text(background_x1, self.canvas.bbox(background)[3]-10, anchor='s', text=name.split(' ')[1], font=('Arial-BoldMT', 16))
# 		except IndexError:
# 			pass


	
class Rng():
	def __init__(self, seed=None):
		if seed is None:
			self.seed = SeedSequence().entropy
		else:
			self.seed = seed

		self.rng = default_rng(seed=self.seed)


class Main():
	instance = None

	def __init__(self, parent):
		self.parent = parent
		self.frames = {}

		self.frame_id = 0

		self.resource_loader = ResourceLoader.get_instance()

		self.NPCs = []
		self.rng_object = Rng()

		self.createGUI()

	def createGUI(self):
		self.parent.title('5e NPC Generator')
		self.parent.geometry('1430x800')

		container = tk.Frame(self.parent)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		# for F in (MainFrame, SheetFrame, DescFrame):
		# 	frame = F(self, container)
		# 	self.frames[F.__name__] = frame
		# 	frame.grid(row=0, column=0, sticky='nsew')

		frame = MainFrame(self, container)
		self.frames['MainFrame'] = frame
		frame.grid(row=0, column=0, sticky='nsew')

		# self.parent.bind('1', partial(self.show_frame, 'MainFrame'))
		# self.parent.bind('2', partial(self.show_frame, 'SheetFrame'))
		# self.parent.bind('3', partial(self.show_frame, 'DescFrame'))

		# self.parent.bind('<Left>', partial(self.change_stage, -1))
		# self.parent.bind('<Right>', partial(self.change_stage, 1))

		self.parent.bind('<g>', self.generate)

		self.show_frame('MainFrame')

	def generate(self, event=None):
		child = self.frames['MainFrame']

		child.canvas.delete('!keep')
		opts = {}

		
		self.clr = "#" + "".join(list(map(lambda x: hex(int(x*255))[2:].zfill(2), np.random.random((3, )))))

		child.gen_btn.config(highlightbackground=self.clr, fg=darken_color(self.clr, 0.6))
		child.apply_opt_btn.config(highlightbackground=self.clr, fg=darken_color(self.clr, 0.6))
		child.reset_opt_btn.config(highlightbackground=self.clr, fg=darken_color(self.clr, 0.6))
		child.canvas.itemconfig(child.divide, fill=darken_color(self.clr, 0.8), outline=darken_color(self.clr, 0.65))
		child.html_btn.config(highlightbackground=self.clr, fg=darken_color(self.clr, 0.6))


		self.rng_object = Rng(seed=int(child.rng_ent.get())) if child.rng_ent.get() else Rng()

		rng = self.rng_object.rng

		for opt_var in child.opt_list:
			str_var = child.opt_string_vars[opt_var].get()
			
			if str_var == "--Random--":
				list_ = []

				for obj in child.opt_choices[opt_var]:
					if obj[0] != "-":
						list_.append(obj)

				var = rng.choice(list_)

			else:				
				if str_var[0] == "-":
					if opt_var == 'Level':	
						levels = {'L':(4, 1), 'M':(5, 5), 'H':(11, 10), 'C':(980, 21)}
						var = np.floor(rng.random()*levels[str_var[2]][0]+levels[str_var[2]][1]).astype('int')
					elif opt_var == 'Occupation':
						var = rng.choice(sorted(self.resource_loader.get_list(str_var[2:-2].lower())))
				else:
					var = str_var
				
			if opt_var == 'Level':
				opts[opt_var] = int(var)
			elif opt_var == 'Uncapped Abilities' or opt_var == 'Only Class Specific Spells':
				var = True if var == 'True' or var == '1' else False
				opts[opt_var] = var
			else:
				opts[opt_var] = var

		opts["rng_seed"] = self.rng_object.seed

		self.current_npc = NPC(self.rng_object, {k.lower().replace(' ', '_'):v for k, v in opts.items()})
		child.create_preview(self.current_npc)




		# ## SUBRACE
		# npc.set_tag('Subrace', self.resource_loader.get_subrace(rng, npc.get_tag('Race')))

		# ## SUBCLASS INIT
		# if npc.get_tag('class_bool'):
		# 	## SUBCLASS
		# 	npc.set_tag('Subclass', self.resource_loader.get_subclass(rng, npc.get_tag('Occupation')))

		# 	## CLASS FEATURES
		# 	npc.set_tag('Features', self.resource_loader.get_class_features(rng, npc.get_tag('Occupation'), npc.get_tag('Subclass'), npc.get_tag('Level')))


		# ## ABILITIES
		# npc.set_tag('Abilities', self.generate_abilities(rng, npc))
		# ### ABILITY SCORE IMPROVEMENTS
		# npc.set_tag('Abilities', self.add_asi_and_feats(rng, npc))


		# ## APPEARENCE AND TRAITS
		# appr = self.resource_loader.get_appearances(rng, npc.get_tag('Race'), npc.get_tag('Subrace'))


		# npc.set_tag('Appearance', {k:v for k, v in appr.items() if 'base' not in k and 'mod' not in k})

		# ## LANGUAGES AND SPEEDS
		# npc.set_tag('Languages', self.resource_loader.get_languages_or_speeds(rng, npc.get_tag('Race'), npc.get_tag('Subrace'), 'lan'))
		# npc.set_tag('Speeds', self.resource_loader.get_languages_or_speeds(rng, npc.get_tag('Race'), npc.get_tag('Subrace'), 'spd'))

		# ### HEIGHT AND WEIGHT
		# h = round(int(appr['height_base'][0]) + int(appr['height_mod'][0])*2.54)
		# w = round(int(appr['weight_base'][0]) + ((int(appr['weight_mod'][0]) * int(appr['height_mod'][0]))*0.45))
		# w_max = round(int(appr['weight_base'][0]) + ((int(appr['weight_mod'][1][1]) * int(appr['height_mod'][1][1]))*0.45))

		# npc.set_tag('Height', f"{h} cm")

		# w_dict = {0.4:'light', 0.7:'medium', 10:'heavy'}
		# w_cat = ''

		# for bin_ in w_dict:
		# 	if (w-int(appr['weight_base'][0]))/(w_max-int(appr['weight_base'][0])) <= bin_:
		# 		w_cat = w_dict[bin_]
		# 		break

		# npc.set_tag('Weight', f"{w} kg ({w_cat})")

		# ### OTHER APPEARENCES LIKE EYE COLOR AND ALL THAT BS

		# # xml.get_appearence()


		


		# ### TRAITS
		# npc.set_tag('Trait', self.resource_loader.get_traits(rng, 1))


		

		# ## CLASS RELATED AND AC 
		# if npc.get_tag('class_bool'):

		# 	## CLASS PROFICIENCIES
		# 	npc.set_tag("Class Proficiencies", self.resource_loader.get_proficiencies(rng, npc.get_tag('Occupation')))

		# 	## WEAPONS AND ARMOR
		# 	npc.set_tag("Weapon", self.resource_loader.get_weapon(rng, npc.get_tag('Class Proficiencies')['weapons']))

		# 	armr_dict = self.resource_loader.get_armor(rng, npc.get_tag('Class Proficiencies')['armor'], npc.get_tag('Abilities')['STR'][0])
		# 	npc.set_tag('Armor', f"{armr_dict['name']}, Stealth Dis.: {armr_dict['stealth_dis']}")

			


	
		

		# ## AC AND HP
		# ### AC
		# if npc.get_tag('class_bool'):
		# 	ac = int(armr_dict['ac']) + npc.get_tag('Abilities')['DEX'][1]

		# 	if 'shield' in npc.get_tag('Class Proficiencies')['armor']:
		# 		if rng.random() <= 0.25:
		# 			ac += 2
		# 			npc.set_tag('Armor', f"{npc.get_tag('Armor')}, Shield (+2): True")

		# 	npc.set_tag('AC', ac)
		# else:
		# 	npc.set_tag('AC', 10 + npc.get_tag('Abilities')['DEX'][1])

		# ### HP
		# die = 8 if 'medium' in npc.get_tag('Appearance')['size'][0] else 6
		# hp = np.array(rng.choice(die, npc.get_tag('Level')) + 1) + npc.get_tag('Abilities')['CON'][1]
		
		# npc.set_tag('Hit Points', max(sum(hp), 1))



		# self.frames['MainFrame'].NPC_GUI(npc, rng)

		# # child.canvas.bind('<Button-1>', lambda e: webbrowser.open(f"https://5e.tools/races.html#{''.join(race_url).lower().replace(' ', '_')}", new=2))



		# # child.canvas.bind('<Button-1>', lambda e: webbrowser.open(f"https://www.fantasynamegenerators.com/dnd-{npc.get_tag('Race').lower().replace(' ', '-')}-names.php", new=2))
		




		# # hsv = [*[rng.random() for _ in range(2)], min(rng.random()+0.4, 1)]
		# # hsv = [rng.random(), 0.5, rng.random()]
		# # rgb = list(map(lambda x: hex(int(x*255))[2:].zfill(2), colorsys.hsv_to_rgb(*hsv)))
		# # clr = "#" + "".join(rgb)

		# # print(hsv, rgb, clr)
		# # a = child.canvas.create_rectangle(1200, 500, 1420, 600, fill=clr)


		
		# # s = ""

		# # for item in self.vars_dict.items():
		# # 	s += f"{item[0]}: {item[1]}\n"

		# # if self.vars_dict['Occupation'] not in self.resource_loader.get_list('classes'):
		# # 	s += f"\nOccupation Description: {self.resource_loader.get_occupation_description(self.vars_dict['Occupation'])[0]}{self.resource_loader.get_occupation_description(self.vars_dict['Occupation'])[1:].lower()}\n"

		# # s += f"Subrace: {self.resource_loader.get_subrace(self.rng, self.vars_dict['Race'])}\n"



		# # child.canvas.delete(child.description)
		# # child.description = child.canvas.create_text(350, 50, anchor='nw', text=f"Description:\n\n{s}", font=('Arial', 18), width=500) 

	def open_html(self):
		try:
			html = self.current_npc.to_html()
			print(html)
		except AttributeError:
			print('No npc generated')

	def show_frame(self, frame_name, event=None):
		self.frames[frame_name].tkraise()

	def start(self):
		self.parent.mainloop()

	@staticmethod 
	def get_instance():
		if Main.instance is None:
			Main.instance = Main(tk.Tk())
		return Main.instance

if __name__ == "__main__":
	Main.get_instance().start()