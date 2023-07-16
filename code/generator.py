import tkinter as tk
from numpy.random import default_rng, SeedSequence
import numpy as np
from PIL import Image, ImageTk
import os
import colorsys

from functools import partial
import tkinter.scrolledtext as scrolledtext
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter

from resource_loader import ResourceLoader






def darken_color(color, factor):
	r = hex(int(int(color[1:3], 16) * min(max(factor, 0), 1)))[2:]
	g = hex(int(int(color[3:5], 16) * min(max(factor, 0), 1)))[2:]
	b = hex(int(int(color[5:7], 16) * min(max(factor, 0), 1)))[2:]

	return f"#{r.zfill(2)}{g.zfill(2)}{b.zfill(2)}"


def generate_page_colors(main_clr, noise_range=65):
	clrs = {}
	rng = default_rng()

	r = int(main_clr[1:3], base=16)
	g = int(main_clr[3:5], base=16)
	b = int(main_clr[5:7], base=16)

	for page in ['preview', 'quick-info', 'sheet', 'text-boxes', 'pet-block']:
		c = [r, g, b]

		for i in range(len(c)):
			ch = c[i]
			rand = rng.integers(-noise_range, high=noise_range+1) #one above for high apperently
			
			c[i] = max(min(ch + rand, 255), 0)

		clrs[page] = "#" + hex(int(c[0]))[2:].zfill(2) + hex(int(c[1]))[2:].zfill(2) + hex(int(c[2]))[2:].zfill(2)

	return clrs


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

	def format(self, canvas, x_anchor=1000, y_anchor=60, val_dist=225, fill_clr='#00FF00', outline_clr='#BB66FF'):
		if self.name == Ability.TYPES[0]:
			canvas.create_text(x_anchor, y_anchor, text=self.name, anchor='nw', font=Formating.FONT_DESC_BOLD, tags=['text', 'ability', 'key'])
		else:
			canvas.create_text(canvas.bbox(canvas.find_withtag('text&&ability&&key')[-1])[0]+1, canvas.bbox(canvas.find_withtag('text&&ability&&key')[-1])[3]+10, text=self.name, anchor='nw', font=Formating.FONT_DESC_BOLD, tags=['text', 'ability', 'key'])
		
		modifier = self.get_modifier()
		modifer_txt = f'+{modifier}' if modifier > 0 else modifier
		canvas.create_text(x_anchor+val_dist, canvas.bbox(canvas.find_withtag('text&&ability&&key')[-1])[1], text=f"{self.score} [{modifer_txt}]", anchor='ne', font=('Arial', 16), tags=['text', 'ability', 'value'])
	
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


class Feature():
	def __init__(self, parent, f_id, f_type, sub_features):
		self.parent = parent
		self.f_id = f_id
		self.f_type = f_type
		self.sub_features = sub_features

		self.sub_features['description'] = Feature.apply_description_tables(self.sub_features['description'], self.parent.rng)
		getattr(self, f_type)()

	def snippet(self):
		self.parent.features[self.f_id] = self.sub_features['description']

	def action(self):
		self.parent.actions[self.f_id] = [self.sub_features['action_type'], self.sub_features['description']]

	@staticmethod
	def apply_description_tables(desc, rng):
		split_desc = desc.split('#')
		for j in split_desc:
			if j[0] == '!':
				split_desc[split_desc.index(j)] = rng.choice(ResourceLoader.get_instance().get_table(j[1:]))
			# else:
			# 	split_desc[split_desc.index(j)] = j.strip()

		return ''.join(split_desc)


class Feat():
	def __init__(self, parent, name):
		self.parent = parent
		self.name = name

		self.apply_asi()
		self.fix_description()
		self.apply_features()

	def apply_asi(self):
		self.asi = ResourceLoader.get_instance().get_feat_asi(self.name)
		self.parent.apply_race_asi_bonuses(self.asi)

	def fix_description(self):
		self.description = ResourceLoader.get_instance().get_feat_description(self.name)

		desc_exts = ResourceLoader.get_instance().get_feat_description_extensions(self.name)

		for de in desc_exts:
			if float(de[0]) >= self.parent.rng.random():
				self.description += de[1]

		self.description = Feature.apply_description_tables(self.description, self.parent.rng)

		# self.description = self.description.replace('BREAK', '\n')


	def apply_features(self):
		pass
		# getattr(foo, 'bar')()


class Spellcasting():
	SPELL_TIERS = ['At Will', '5/day', '3/day', '2/day', '1/day']
	SPELL_LEVELS = ['Cantrip', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']

	def __init__(self, parent, ability, spells_per_level_coefficients):
		self.parent = parent
		
		if ability == 'random':
			self.ability = self.parent.rng.choice(Ability.TYPES)
		else:
			self.ability = ability


		coefficient_list = list(map(float, spells_per_level_coefficients.split(':')))
		spells_per_level_func = lambda x: coefficient_list[0]*x**2+coefficient_list[1]*x+coefficient_list[2]
		avg_spells_per_level = spells_per_level_func(self.parent.get_option_value('level'))
		scale = 2 if self.parent.cls_bool else 1.25
		print(avg_spells_per_level)
		self.spells_per_level = round(abs(self.parent.rng.normal(avg_spells_per_level, scale)))

		self.spell_list_type = self.parent.get_option_value('occupation')
		if self.parent.subclass == 'Eldrich Knight' or self.parent.subclass == 'Arcane Trickster':
			self.spell_list_type = 'Wizard'

		elif not self.parent.cls_bool:
			self.spell_list_type = self.parent.rng.choice(ResourceLoader.get_instance().get_list('classes'))

		self.add_default_spells()

		### min(max(np.norm(), spl_min), spl_max), spl_min == 0 if not Paladin || Ranger -> spl_min == 1, spl_max == calculated from list of 
		### every spell sorted after spell level and taking the last in the list, removing 'Cantrip' if necissary 


	def add_default_spells(self):
		max_level = self.get_max_level()
		rng = self.parent.rng 

		min_level = 0 
		if self.spell_list_type == 'Paladin' or self.spell_list_type == 'Ranger':
			min_level = 1

		lvl = self.parent.get_option_value('level')
		loc = -0.0039*lvl**2 + 0.1875*lvl - 0.1836
		std = -0.01*lvl**2 + 0.25*lvl + 0.56

		if max_level == '5th':
			loc = loc*0.6
			std = std*0.6
		
		# print(lvl, loc, std, self.spells_per_level)
		# print(self.spells_per_level)

		count = {}
		for _ in range(self.spells_per_level):
			spl_lvl = min(max(abs(round(rng.normal(loc, std))), min_level), max_level)
			try:
				count[spl_lvl] += 1
			except:
				count[spl_lvl] = 1

		# print(count)

	def get_max_level(self):
		sorted_l = sorted(ResourceLoader.get_instance().get_spell_lvl_list(self.spell_list_type))

		try:
			max_l = sorted_l[sorted_l.index('Cantrip')-1]
		except ValueError:
			max_l = sorted_l[-1]

		return int(max_l[0])

	def add_spell_random(self, lvl, class_):
		print(lvl, class_)

	def add_spell_specific(self, name):
		print(name)


	def __repr__(self):
		return f"Spellcasting Ability: {self.ability}, Spells/Level: {self.spells_per_level}, Spell List: {self.spell_list_type}"


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

		self.features = {}
		self.actions = {}
		self.feats = {}
		self.spellcasting = None

		# self.generate_base()
		self.generate()

		# self.generate_ac_initiative()

	def generate(self):
		race = self.get_option_value('race')
		sex = self.get_option_value('sex')
		occupation = self.get_option_value('occupation')

		RL = ResourceLoader.get_instance()
		
		## NAME
		try:
			self.name = self.rng.choice(RL.get_name_list(race, sex))
		except ValueError as e:
			print("No names for that race currently. Maybe you didn't update names.xml using name_automator.py.", f'"{e}"')
			self.name = '???'

		## RACE TYPE
		self.race_type = self.rng.choice(RL.get_race_type_choices(race))

		## RACE ABILITY SCORE IMPROVEMENT & ASI/FEATS
		race_asi = RL.get_race_asi(race, self.race_type)
		self.apply_race_asi_bonuses(race_asi)

		# if self.cls_bool: # MAYBE KEEP THIS
		self.add_asi_and_feats()

		Feat(self, 'Aberrant Dragonmark')


		## SIZE, SPEEDS, LANGUAGES
		self.size = self.rng.choice(RL.get_size(race, self.race_type).split(';'))

		self.speeds = {'walking':'30', 'flying':None, 'swimming':None}
		self.speeds.update(RL.get_speeds(race, self.race_type))

		self.languages = RL.get_languages(race, self.race_type)
		for lan in self.languages:
			if lan == 'random':
				language_choices = NPC.LANGUAGES.copy()
				index = self.languages.index(lan)
				[language_choices.remove(a) for a in self.languages[:index]]
				self.languages[index] = self.rng.choice(language_choices)

		self.darkvision = RL.get_darkvision(race, self.race_type)


		## APPEARENCES; HEIGHT, WEIGHT, AGE
		self.appearances = {}
		height_weight_dict = RL.get_height_weight(race, self.race_type)

		self.appearances['height'] = self.get_height_weight_value(height_weight_dict, 'height')
		self.appearances['weight'] = self.get_height_weight_value(height_weight_dict, 'weight')


		age_list = RL.get_age(race, self.race_type)
		self.appearances['age'] = self.rng.integers(int(age_list[0]), high=int(age_list[1])+1)

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



		## RACIAL FEATURES AND ACTIONS
		race_features = RL.get_racial_features(race, self.race_type)
		self.add_features(race_features)

		## SUBCLASS
		self.subclass = RL.get_subclass(self.get_option_value('occupation'))
		### YOU CAN SET SUBCLASS HERE BECAUSE THE SUBCLASS.XML FEATURES HAVE LEVEL REQUIREMENT SO IF YOU GET THE SUBCLASS IN LEVEL 4 YOU WILL HAVE THE SUBCLASS BUT NONE OF
		### THE FEATURES
		
		## SPELLCASTING 
		cls_spellcasting = RL.get_spellcasting_ability(self.get_option_value('occupation'), self.subclass)
		self.spellcasting = Spellcasting(self, *cls_spellcasting)

		# print(self.spellcasting)


		### MAYBE TRY TO MAKE EVERY THING INTO FEATURES, AND HAVE IN THE XML FILE SO THEY HAVE A TYPE AND THEN MAKE A "FEATURE" CLASS AND 
		### HAVE GENERATION FOR EVERY TYPE OF FEATURE, LIKE 'ADDITIONAL SPELL' OR 'ADDITIONAL ACTION' AND THAT CLASS SHOULD MAYBE HAVE A 
		### PARENT VARIABLE TO BE ABLE TO DO THINGS IN THE NPC CLASS LIKE "ADD_SPELL()" FROM THE FEATURE CLASS
		### THIS COULD ALSO BE USED WHEN MAKING FEATS LATER ON, SO ITS FOR RACE, CLASS, AND FEATS

		### MAYBE HAVE A WHOLE "SPELLCASTING" CLASS 

		# self.actions = {k:Action(v[0], v[1]) for k, v in RL.get_race_actions(race, self.race_type).items() if int(v[1]['level_req']) <= self.options['level'].value}

	def get_option_value(self, key):
		return self.options[key].value

	def add_asi_and_feats(self):
		lvls = np.arange(self.options['level'].value)+1
		extras = {'Fighter':[6, 14], 'Rogue':[10]}

		feat_choices = ResourceLoader.get_instance().get_list('feats').copy()

		lvls = [not bool(x % 4) for x in sorted(lvls)]

		try:
			for extra in extras[self.options['occupation'].value]:
				lvls = np.delete(lvls, extra)
				lvls = np.insert(lvls, extra-1, True)
				
		except KeyError:
			pass


		choices = {'feat':0.2, '2':0.4, '1+1':0.4}

		for lvl in np.arange(self.options['level'].value):
			if lvls[lvl]:
				choice = self.rng.choice(list(choices.keys()), p=list(choices.values()))
				if choice == 'feat':
					for f in self.feats.keys():
						feat_choices.remove(f)

					feat = Feat(self, self.rng.choice(feat_choices))
				
				else:
					for bonus in choice.split('+'):
						self.abilities[self.rng.choice(Ability.TYPES)].add_bonus(bonus)


	def add_features(self, dict_):
		for feature_id in dict_:
			feature_dict = dict_[feature_id]
			if int(feature_dict['lvl_req']) <= self.get_option_value('level'):
				Feature(self, feature_id, feature_dict['type'], feature_dict['sub_features'])


	def get_height_weight_value(self, dict_, t):
		mod_split = list(map(int, dict_[f'{t}_modifier'].split('d')))
		mod = sum(list(map(lambda x: max(x, 1), self.rng.random(mod_split[0])*mod_split[1]))) # sum(self.rng.choice(mod_split[1], mod_split[0])+1) for only 1-6 ints


		mod = mod*2.54 if t == 'height' else mod

		base = int(dict_[f'{t}_base'])
		if t == 'height':
			return round(base + mod)
		else:
			return round(base + ((self.appearances['height']-int(dict_['height_base']))/2.54*mod)*0.45)



	def get_weight_bin(self):
		w_bins = {0.25:'light', 0.7:'medium', 10:'heavy'}
		w_bin = ''
		
		h_w_dict = ResourceLoader.get_instance().get_height_weight(self.options['race'].value, self.race_type)
		
		h_mod = list(map(int, h_w_dict['height_modifier'].split('d')))
		w_mod = list(map(int, h_w_dict['weight_modifier'].split('d')))

		w_max = int(h_w_dict['weight_base']) + (h_mod[0]*h_mod[1] * w_mod[0]*w_mod[1])*0.45

		for bin_ in w_bins:
			if (self.appearances['weight']-int(h_w_dict['weight_base']))/(w_max-int(h_w_dict['weight_base'])) <= bin_:
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
		for k, v in self.speeds.items():
			speeds[f"{k.title()} Speed"] = v if v is not None else int(self.speeds['walking'])//2

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

		#GET HEALTH/AC
	# def generate_ac_initiative(self):
	# 	ac = 10
	# 	self.stats['Armor Class'] = Stat('Armor Class', ac)

	# 	self.initiative = self.abilities['DEXTERITY'].modifier
	# 	self.stats['Initiative'] = Stat('Initiative', self.initiative)


	def to_html(self):
		html = '<html> <head> 	<link rel="stylesheet" href="CSS_PREVIEW.css"> 	<title>D&D 5e NPC Generator</title> 	<script> 		function dice_roll(die, bonus) { 			return Math.floor(Math.random() * die)+1+bonus 		} 	</script> 	<style type="text/css"> :root {'
		
		## COLORS
		page_colors = generate_page_colors(Main.get_instance().clr)
		for page_clr in list(page_colors.keys())[:-1]:
			clr = page_colors[page_clr]
			html += f'--{page_clr}-border-color: {clr}; --{page_clr}-background-color: {darken_color(clr, 0.6)};'
		
		tb_clr = page_colors['text-boxes']
		html += f'--text-boxes-spell-href-color: {tb_clr}; --text-boxes-border-color: {darken_color(tb_clr, 0.6)}; --text-boxes-background-color: {darken_color(tb_clr, 0.45)}; --text-boxes-darker-background-color: {darken_color(tb_clr, 0.3)};'

		html += '}</style> </head> <body>'
		## BODY

		# for page_clr in page_colors:
		# 	clr = page_colors[page_clr]
		# 	html += f'<div class="page" style="background: {darken_color(clr, 0.6)};border: 4px solid {clr};height: 20%;"></div>'

		### SUMMARY
		html += '<div class="page">'

		html += '<div class="preview-header"> <div class="preview-header_summary"> <div style="font-size: 32px;font-weight: bold;">'
		html += self.name
		html += '</div> <div>'
		html += f'{self.options["sex"].value} {self.options["race"].value} {self.options["occupation"].value}'
		html += '</div> <div>'
		html += f'Level {self.options["level"].value}'
		html += '</div> <div>'
		html += f'Feats: '

		html += '</div> </div> </div> </div> </div> <div>'

		### STATBLOCK
		html += '<div class="preview-content"> <div class="preview-content_statblock"> <div style="font-size:40px;font-weight: bold;"> '
		html += f'{self.name} ({self.options["occupation"].value})'
		html += '<div style="font-style: italic;"> '
		html += f'{self.size.title()} humaniod ({self.options["race"].value})'

		html += '<svg height="10" width="100%" class="npc_statblock_break"> <polyline points="0,0 670, 5 0,10"></polyline> </svg>  <div><span style="font-weight: bold;">Armor Class</span> '



		# html += '  <div class="preview-content"> <div class="preview-content_statblock"> <div style="font-size:40px;font-weight: bold;"> '

		## FINISH
		html += '</body> </html>'
		return html

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
			npc.abilities[ability].format(self.canvas, x_anchor=1050, y_anchor=120, val_dist=225)

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

		frame = MainFrame(self, container)
		self.frames['MainFrame'] = frame
		frame.grid(row=0, column=0, sticky='nsew')

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


		# ## APPEARENCE AND TRAITS
		# appr = self.resource_loader.get_appearances(rng, npc.get_tag('Race'), npc.get_tag('Subrace'))


		# npc.set_tag('Appearance', {k:v for k, v in appr.items() if 'base' not in k and 'mod' not in k})

		


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

			


	
		
	def open_html(self):
		# try:
		html = self.current_npc.to_html()
		with open("out.html", 'w') as file:
			soup = BeautifulSoup(html, features="html.parser")
			formatter = HTMLFormatter(indent=4)
			file.write(soup.prettify(formatter=formatter))


		os.system("open -a /Applications/Safari.app out.html")
		# except AttributeError:
		# 	print('No npc generated')

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