import tkinter as tk
from numpy.random import default_rng, SeedSequence
import numpy as np
from PIL import Image, ImageTk
import webbrowser
import colorsys

from pyperclip import copy
from time import sleep
from functools import partial
from tkinter.simpledialog import askstring

import re

from resource_loader import ResourceLoader


# class HoverWindow():
# 	def __init__(self, controller, canvas, obj, text='Hello'):
# 		self.waittime = 100
# 		self.wraplength = 100

# 		self.controller = controller
# 		self.canvas = canvas
# 		self.obj = obj
# 		self.text = text

# 		self.canvas.tag_bind(obj, '<Enter>', self.enter)
# 		self.canvas.tag_bind(obj, '<Leave>', self.leave)

# 		self.ID = None
# 		self.tw = None

# 	def enter(self, event):
# 		self.schedule()

# 	def leave(self, event):
# 		self.unschedule()
# 		self.hide()

# 	def schedule(self):
# 		self.unschedule()
# 		self.ID = self.canvas.after(self.waittime, self.show)

# 	def unschedule(self):
# 		ID = self.ID
# 		self.ID = None
# 		if ID:
# 			# self.canvas.after(self.waittime, self.show)
# 			self.canvas.after_cancel(ID)

# 	def show(self):
# 		self.tw = tk.Toplevel(self.canvas)
# 		self.tw.wm_overrideredirect(True)

# 	def hide(self):
# 		tw = self.tw
# 		self.tw = None
# 		if tw:
# 			tw.destroy()
 




class Rng():
	def __init__(self, seed=None):
		if seed is None:
			self.seed = SeedSequence().entropy
		else:
			self.seed = seed

		self.rng = default_rng(seed=self.seed)

	def get_rng(self):
		return self.rng

	def get_seed(self):
		return self.seed

 				

class NPC():
	def __init__(self):
		self.tags = {}

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

		self.vars_list = (['Level', 'Occupation', 'Race', 'Sex', 'Uncapped Abilities', 'Only Class Specific Spells'])
		self.var_choices = 	{
								'Race':sorted(self.controller.resource_loader.get_list('races')), 
								'Sex':['Male', 'Female'], 
								'Occupation':['--CLASSES--', *sorted(self.controller.resource_loader.get_list('classes')), '--JOBS--', *sorted(self.controller.resource_loader.get_list('jobs'))],
								'Level':[*list(map((str), np.arange(1, 21))), '--Low (1-4)--', '--Medium (5-9)--', '--High (10-20)--', '--Crazy (21-1000)--'],
								'Uncapped Abilities':['True', 'False'],
								'Only Class Specific Spells':['True', 'False']
							}

		self.createGUI()

	def createGUI(self):
		self.canvas = tk.Canvas(self, width=1430, height=800, highlightthickness=0)
		self.canvas.place(x=0, y=0, anchor='nw')

		# divide_clr = "#" + "".join(list(map(lambda x: hex(int(x*255))[2:].zfill(2), np.random.random((3, )))))
		divide_clr = "#555555"

		for var in self.vars_list:
			lbl = tk.Label(self, text=var, font=('Arial', 18))
			lbl.place(relx=0.1, rely=((0.1 + self.vars_list.index(var)/10)-0.035), anchor='c')

			string_var = tk.StringVar(self, '--Random--')
			self.string_vars[var] = string_var
			
			opt_m = tk.OptionMenu(self, string_var, *['--Random--', *self.var_choices[var]])
			opt_m.config(font=('Arial', 18), width=20)
			opt_m.place(relx=0.1, rely=(0.1 + self.vars_list.index(var)/10), anchor='c')

		# self.description = self.canvas.create_text(350, 50, anchor='nw', text=f"Description:\n", font=('Arial', 18), width=500) 

		self.canvas.create_line(300, 0, 300, 800, fill=divide_clr, width=20, tags=['break'])
		self.canvas.create_line(857, 0, 857, 800, fill=divide_clr, width=10, tags=['break'])

		self.canvas.create_line(310, 270, 857, 270, fill=divide_clr, width=10, tags=['break'])
		self.canvas.create_line(857, 605, 1430, 605, fill=divide_clr, width=10, tags=['break'])

		gen_btn = tk.Button(self, text='Generate', font=('Good Times', 30), fg='#9b0707', relief='groove', command=self.controller.generate)
		gen_btn.place(relx=0.1, rely=0.9, anchor='c')

		rng_lbl = tk.Label(self, text="RNG Seed Input", font=('Arial', 16)).place(relx=0.1, rely=0.83, anchor='s')

		self.rng_ent = tk.Entry(self)
		self.rng_ent.place(relx=0.1, rely=0.85, anchor='c')

	def NPC_GUI(self, npc, rng):
		self.canvas.delete('all')

		statblock_clr = "#" + "".join(list(map(lambda x: hex(int(x*255))[2:].zfill(2), rng.random((3, )))))

		print(npc.tags)

		## PARAMETERS
		self.canvas.create_text(315, 0, anchor='nw', text="Parameters:\n", font=('Arial', 24), width=547, tags=['text', 'header', 'parameter'])
		
		parameters = (*self.vars_list, 'rng_seed')
		for parameter in parameters:
			text = f"{parameter}: {npc.get_tag(parameter)}"
			text_body = self.canvas.create_text(315, 35+(parameters.index(parameter)*31), anchor='nw', text=text, font=('Arial', 13), width=542, tags=['text', 'body', 'parameter', parameter])

			self.canvas.tag_bind(text_body, '<ButtonPress-1>', partial(self.copy_text, text_body, text))
			self.canvas.tag_bind(text_body, '<ButtonPress-2>', partial(self.edit_text, text_body, text))

			if parameter == 'Occupation' and not npc.get_tag('class_bool'):
				occ = self.controller.resource_loader.get_occupation_description(npc.get_tag('Occupation'))
				occ_desc = f"{occ[0]}{occ[1:-1].lower()}"
				self.attach_tooltip(text_body, text=occ_desc, display_type='description')


		## STATBLOCK
		### CLASSIFICATION AND NAME
		self.canvas.create_text(315, 282, anchor='nw', text=f"{npc.get_tag('Name')}", font=('Baskerville', 24), width=547, tags=['text', 'header', 'statblock'], fill=statblock_clr)
		classification_body = self.canvas.create_text(315, 310, anchor='nw', text=f"{npc.get_tag('Appearance')['size'][0].title()} Humaniod ({npc.get_tag('Sex').lower()} {npc.get_tag('Race')}), any alignment", font=('Arial-ItalicMT', 13), tags=['text', 'body', 'statblock', 'classification'])
		self.add_statblock_break(classification_body, statblock_clr)
		
		###	TRAITS
		trait = npc.get_tag('Trait')
		trait_body_main = self.canvas.create_text(315, self.canvas.bbox(classification_body)[3]+15, anchor='nw', text=f"Personality Trait ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'trait'])
		
		trait_body_desc = self.canvas.create_text(self.canvas.bbox(trait_body_main)[2], self.canvas.bbox(trait_body_main)[1], anchor='nw', text=list(trait.keys())[0], font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'trait'])
		self.attach_tooltip(trait_body_desc, trait[list(trait.keys())[0]], display_type='description')
		self.add_statblock_break(trait_body_desc, statblock_clr)

	
		### BASIC STATS
		#### AC
		ac_body_main = self.canvas.create_text(315, self.canvas.bbox(trait_body_desc)[3]+15, anchor='nw', text=f"Armor Class ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'basic', 'armor class'])
		ac_body_desc = self.canvas.create_text(self.canvas.bbox(ac_body_main)[2], self.canvas.bbox(ac_body_main)[1], anchor='nw', text=f"{npc.get_tag('AC')}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'basic', 'armor class'])

		if npc.get_tag('class_bool'):
			self.canvas.itemconfigure(ac_body_desc, text=f"{npc.get_tag('AC')} ({npc.get_tag('Armor')})")

		#### HP
		hp_body_main = self.canvas.create_text(315, self.canvas.bbox(ac_body_desc)[3]+5, anchor='nw', text=f"Hit Points ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'basic', 'hit points'])
		
		lvl = npc.get_tag('Level')
		hd = 8 if 'medium' in npc.get_tag('Appearance')['size'][0] else 6
		hp_mod = npc.get_tag('Abilities')['CON'][1]*lvl

		plus, minus = "+", "-"
		hp_roll = f"{lvl}d{hd} {plus if hp_mod >= 0 else minus} {abs(hp_mod)}"
		hp_roll_avg = ((lvl*hd+(hp_mod))+(lvl+hp_mod))//2

		hp_text_var = f"Rolled: {npc.get_tag('Hit Points')} | Average: {hp_roll_avg} ({hp_roll})"
		
		hp_body_desc = self.canvas.create_text(self.canvas.bbox(hp_body_main)[2], self.canvas.bbox(hp_body_main)[1], anchor='nw', text=f"{hp_text_var}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'basic', 'hit points'])

		#### Speed
		speeds = npc.get_tag('Speeds')
		speed_body_main = self.canvas.create_text(315, self.canvas.bbox(hp_body_desc)[3]+5, anchor='nw', text=f"Speed ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'basic', 'speed'])

		speed_body_desc_1 = self.canvas.create_text(self.canvas.bbox(speed_body_main)[2], self.canvas.bbox(speed_body_main)[1], anchor='nw', text=f"{speeds[0][:-1]} ft{speeds[0][-1]} ", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'basic', 'speed'])
		if len(speeds) > 1:
			speed_body_desc_2 = self.canvas.create_text(self.canvas.bbox(speed_body_desc_1)[2], self.canvas.bbox(speed_body_desc_1)[1], anchor='nw', text=f"{speeds[1][:-1]} ft{speeds[1][-1]} ", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'basic', 'speed'])

		self.add_statblock_break(speed_body_desc_1, statblock_clr)

		### Abilities
		abilities = npc.get_tag('Abilities')

		for ability in abilities:
			ability_body_main = self.canvas.create_text(340+(list(abilities.keys()).index(ability))*80, self.canvas.bbox(speed_body_desc_1)[3]+15, anchor='nw', text=f"{ability}", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'abilities', ability])

			mod_desc = f"+{abilities[ability][1]}" if abilities[ability][1] >= 0 else f"{abilities[ability][1]}" 
			ability_body_desc = self.canvas.create_text((self.canvas.bbox(ability_body_main)[0]+self.canvas.bbox(ability_body_main)[2])/2, self.canvas.bbox(ability_body_main)[3]+3, anchor='n', text=f"{abilities[ability][0]} ({mod_desc})", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'abilities', ability])

		self.add_statblock_break(self.canvas.find_all()[-1], statblock_clr)


		### MISC STATS
		#### SAVING THROWS AND ALL THAT
		if npc.get_tag('class_bool'):

			##### SAVING THROWS
			saving_throws_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-2])[3]+15, anchor='nw', text=f"Saving Throws ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'saving_throws'])

			sts = npc.get_tag('Class Proficiencies')['saving throws']

			for st in sts:
				mod_desc = f"+{npc.get_tag('proficiency_bonus')+npc.get_tag('Abilities')[st][1]}" if npc.get_tag('proficiency_bonus')+npc.get_tag('Abilities')[st][1] >= 0 else {npc.get_tag('proficiency_bonus')+npc.get_tag('Abilities')[st][1]}

				a = f"{st} {mod_desc}, " if sts.index(st) == 0 else f"{st} {mod_desc}"
				saving_throws_desc = self.canvas.create_text(self.canvas.bbox(self.canvas.find_all()[-1])[2], self.canvas.bbox(self.canvas.find_all()[-1])[1], anchor='nw', text=a, font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'saving_throws'])

			##### SKILLS (AND TOOLS)
			skills_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Skills ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'skills'])
			skills = npc.get_tag('Class Proficiencies')['skills']

			for skill in skills:
				skill_ab = self.controller.resource_loader.get_ability_for_skill(skill)
				mod_desc = f"+{npc.get_tag('proficiency_bonus')+npc.get_tag('Abilities')[skill_ab][1]}" if npc.get_tag('proficiency_bonus')+npc.get_tag('Abilities')[skill_ab][1] >= 0 else {npc.get_tag('proficiency_bonus')+npc.get_tag('Abilities')[skill_ab][1]}

				a = f"{skill} {mod_desc}, " if skills.index(skill) < len(skills)-1 else f"{skill} {mod_desc}"
				skill_body_desc = self.canvas.create_text(self.canvas.bbox(self.canvas.find_all()[-1])[2], self.canvas.bbox(self.canvas.find_all()[-1])[1], anchor='nw', text=a, font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'skills'])

			try:
				tools = npc.get_tag('Class Proficiencies')['tools']
			except KeyError:
				tools = None

			if tools is not None:
				tools_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Tools ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'tools'])

				for tool in tools:
					a = f"{tool}, " if tools.index(tool) < len(tools)-1 else f"{tool}"
					tool_body_desc = self.canvas.create_text(self.canvas.bbox(self.canvas.find_all()[-1])[2], self.canvas.bbox(self.canvas.find_all()[-1])[1], anchor='nw', text=a, font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'tools'])

		##### SENSES
		senses_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Senses ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'senses'])
		passive_p_body_desc = self.canvas.create_text(self.canvas.bbox(self.canvas.find_all()[-1])[2], self.canvas.bbox(self.canvas.find_all()[-1])[1], anchor='nw', text=f"passive Perception {10+npc.get_tag('Abilities')['WIS'][1]}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'senses'])

		##### LANGUAGES
		languages_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Languages ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'languages'])
		
		for language in npc.get_tag('Languages'):
			desc = f"{language[:language.find('(')-1]}, " if npc.get_tag('Languages').index(language) < len(npc.get_tag('Languages'))-1 else f"{language[:language.find('(')-1]}"
			language_body_desc = self.canvas.create_text(self.canvas.bbox(self.canvas.find_all()[-1])[2], self.canvas.bbox(self.canvas.find_all()[-1])[1], anchor='nw', text=desc, font=('Arial', 13, 'underline'), tags=['text', 'body', 'desc', 'statblock', 'languages'])

			self.attach_tooltip(language_body_desc, language[language.find('(')+1:][:-1], display_type='description', underline=False)


		##### LEVEL AND PROF BONUS
		lvl_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Level ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'level'])
		lvl_body_desc = self.canvas.create_text(self.canvas.bbox(lvl_body_main)[2], self.canvas.bbox(lvl_body_main)[1], anchor='nw', text=f"{lvl}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'level'])
		
		prof_body_main = self.canvas.create_text(315, self.canvas.bbox(lvl_body_desc)[3]+3, anchor='nw', text=f"Proficiency Bonus ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'prof'])
		
		prof = npc.get_tag('proficiency_bonus')
		prof_body_desc = self.canvas.create_text(self.canvas.bbox(prof_body_main)[2], self.canvas.bbox(prof_body_main)[1], anchor='nw', text=f"+{prof}" if prof >= 0 else prof, font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'prof'])

		self.add_statblock_break(prof_body_desc, statblock_clr)


		### OVERVIEW
		name_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Name ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'name'])
		name_body_desc = self.canvas.create_text(self.canvas.bbox(name_body_main)[2], self.canvas.bbox(name_body_main)[1], anchor='nw', text=f"{npc.get_tag('Name')}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'name'])

		gender_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Gender ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'gender'])
		gender_body_desc = self.canvas.create_text(self.canvas.bbox(gender_body_main)[2], self.canvas.bbox(gender_body_main)[1], anchor='nw', text=f"{npc.get_tag('Sex')}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'gender'])
		
		race_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Race ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'race'])
		race_body_desc = self.canvas.create_text(self.canvas.bbox(race_body_main)[2], self.canvas.bbox(race_body_main)[1], anchor='nw', text=f"{npc.get_tag('Subrace')}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'race'])

		occ_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Occupation ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'occupation'])
		occ_body_desc = self.canvas.create_text(self.canvas.bbox(occ_body_main)[2], self.canvas.bbox(occ_body_main)[1], anchor='nw', text=f"{npc.get_tag('Occupation')}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'occupation'])
		
		occ = self.controller.resource_loader.get_occupation_description(npc.get_tag('Occupation'))
		occ_desc = f"{occ[0]}{occ[1:-1].lower()}"

		self.attach_tooltip(occ_body_desc, occ_desc)
		self.add_statblock_break(occ_body_desc, statblock_clr)

		blurb = f"{npc.get_tag('Name')} is a {npc.get_tag('Appearance')['age'][0][:npc.get_tag('Appearance')['age'][0].find('(')-1]} year old {npc.get_tag('Sex')} {npc.get_tag('Race')} {npc.get_tag('Occupation')}"

		blurb_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Blurb ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'blurb'])
		blurb_body_desc = self.canvas.create_text(self.canvas.bbox(blurb_body_main)[2], self.canvas.bbox(blurb_body_main)[1], anchor='nw', text=blurb, font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'blurb'])


		img = Image.open(f"Race Screenshots/{npc.get_tag('Subrace')}.png")
		img = img.resize((min(round(img.width//1.5), 573), min(round(img.height//1.5), 700)))
		self.p_img = ImageTk.PhotoImage(image=img)

		race_pic = self.canvas.create_image(1430, 0, anchor='ne', image=self.p_img, tags='picture')
		race_url = [x for x in npc.get_tag('Subrace') if x not in ('(', ')')]

		self.canvas.tag_bind(race_pic, '<ButtonPress-1>', lambda e: webbrowser.open(f"https://5e.tools/races.html#{''.join(race_url).lower().replace(' ', '_')}", new=2))



		## BREAKS
		self.canvas.create_line(300, 0, 300, 800, fill=statblock_clr, width=20, tags=['break'])
		self.canvas.create_line(857, 0, 857, 800, fill=statblock_clr, width=10, tags=['break'])

		self.canvas.create_line(310, 270, 857, 270, fill=statblock_clr, width=10, tags=['break'])
		self.canvas.create_line(857, self.canvas.bbox(race_pic)[3]+5, 1430, self.canvas.bbox(race_pic)[3]+5, fill=statblock_clr, width=10, tags=['break'])


		### APPEARENCES 
		# age_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Age ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'appearances', 'age'])
		# age_body_desc = self.canvas.create_text(self.canvas.bbox(age_body_main)[2], self.canvas.bbox(age_body_main)[1], anchor='nw', text=f"{npc.get_tag('Appearance')['age'][0]}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'appearances', 'age'])
		
		# height_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Height ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'appearances', 'height'])
		# height_body_desc = self.canvas.create_text(self.canvas.bbox(height_body_main)[2], self.canvas.bbox(height_body_main)[1], anchor='nw', text=f"{npc.get_tag('Height')}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'appearances', 'height'])
		
		# weight_body_main = self.canvas.create_text(315, self.canvas.bbox(self.canvas.find_all()[-1])[3]+3, anchor='nw', text=f"Weight ", font=('Arial-BoldMT', 13), tags=['text', 'body', 'main', 'statblock', 'appearances', 'weight'])
		# weight_body_desc = self.canvas.create_text(self.canvas.bbox(weight_body_main)[2], self.canvas.bbox(weight_body_main)[1], anchor='nw', text=f"{npc.get_tag('Weight')}", font=('Arial', 13), tags=['text', 'body', 'desc', 'statblock', 'appearances', 'weight'])
		


	def add_statblock_break(self, body, clr, mod=5):
		bounds = self.canvas.bbox(body)

		a = self.canvas.create_polygon(315, bounds[3]+mod, 800, bounds[3]+mod+2, 315, bounds[3]+mod+4, fill=clr, tags=['break'])



	def copy_text(self, body, text, *args):
		self.canvas.itemconfigure(body, text="Copied!")
		copy(text[text.find(': ')+2:])
		self.parent.after(500, partial(self.normal_text, body, text))

	def normal_text(self, body, text, *args):
		self.canvas.itemconfigure(body, text=text)

	def edit_text(self, body, text, *args):
		a = askstring('Edit Text', 'New Text Here: ')
		
		self.canvas.itemconfigure(body, text=f"{text[:text.find(': ')+2]}{a}")



	def attach_tooltip(self, body, text="", display_type='description', dash=(1, 1), underline=True):
		if underline:
			self.underline_text(body, dash=dash)

		if display_type == 'description':
			self.canvas.tag_bind(body, '<Enter>', lambda e: self.tooltip_show(e, text, display_type=display_type))
			self.canvas.tag_bind(body, '<Leave>', self.tooltip_hide)

		# elif display_type == 'spell':
		# 	self.canvas.tag_bind(body, '<ButtonPress-1>', lambda e: self.tooltip_show(e, text, display_type=display_type))


	def underline_text(self, ID, dash=(5, 1)):
		bounds = self.canvas.bbox(ID)
		coordinates = (bounds[0], bounds[3]-1, bounds[2], bounds[3]-1)
		self.canvas.create_line(coordinates, tags=[*self.canvas.gettags(ID), 'underline'], dash=dash)

	def tooltip_show(self, event, text, display_type='description'):
		self.top = tk.Toplevel(self)
		self.top.wm_overrideredirect(True)

		w = 180
		h = 100

		self.top.geometry(f"{w}x{h}")
		self.top.geometry(f"+{event.x}+{event.y-(h-40)}")
		

		lbl = tk.Label(self.top, text=text, justify='left', wraplength=w-10).place(relx=0, rely=0, anchor='nw')


	def tooltip_hide(self, event):
		self.top.destroy()



class Generator():
	def __init__(self, parent):
		self.parent = parent
		self.frames = {}

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

		## could add more frames here with for-loop
		frame = MainFrame(self, container)
		self.frames[MainFrame.__name__] = frame
		frame.grid(row=0, column=0, sticky='nsew')

		self.show_frame('MainFrame')

	def generate(self):
		child = self.frames['MainFrame']

		npc = NPC()

		if self.frames['MainFrame'].rng_ent.get():
			self.rng_object = Rng(seed=int(self.frames['MainFrame'].rng_ent.get()))
		else:			
			self.rng_object = Rng()

		rng = self.rng_object.get_rng()
		npc.set_tag('rng_seed', self.rng_object.get_seed())

		npc.set_tag('Name', 'Npc Name')

		
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
						levels = {'L':(4, 1), 'M':(5, 5), 'H':(11, 10), 'C':(980, 21)}
						var = np.floor(rng.random()*levels[str_var[2]][0]+levels[str_var[2]][1]).astype('int')
					elif opt_var == 'Occupation':
						var = rng.choice(sorted(self.resource_loader.get_list(str_var[2:-2].lower())))
				else:
					var = str_var
				
			if opt_var == 'Level':
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

		## SUBCLASS INIT
		if npc.get_tag('class_bool'):
			## SUBCLASS
			npc.set_tag('Subclass', self.resource_loader.get_subclass(rng, npc.get_tag('Occupation')))

			## CLASS FEATURES
			npc.set_tag('Features', self.resource_loader.get_class_features(rng, npc.get_tag('Occupation'), npc.get_tag('Subclass'), npc.get_tag('Level')))


		## ABILITIES
		npc.set_tag('Abilities', self.generate_abilities(rng, npc))
		### ABILITY SCORE IMPROVEMENTS
		npc.set_tag('Abilities', self.add_asi_and_feats(rng, npc))


		## APPEARENCE AND TRAITS
		appr = self.resource_loader.get_appearances(rng, npc.get_tag('Race'), npc.get_tag('Subrace'))


		npc.set_tag('Appearance', {k:v for k, v in appr.items() if 'base' not in k and 'mod' not in k})

		## LANGUAGES AND SPEEDS
		npc.set_tag('Languages', self.resource_loader.get_languages_or_speeds(rng, npc.get_tag('Race'), npc.get_tag('Subrace'), 'lan'))
		npc.set_tag('Speeds', self.resource_loader.get_languages_or_speeds(rng, npc.get_tag('Race'), npc.get_tag('Subrace'), 'spd'))

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


		


		### TRAITS
		npc.set_tag('Trait', self.resource_loader.get_traits(rng, 1))


		

		## CLASS RELATED AND AC 
		if npc.get_tag('class_bool'):

			## CLASS PROFICIENCIES
			npc.set_tag("Class Proficiencies", self.resource_loader.get_proficiencies(rng, npc.get_tag('Occupation')))

			## WEAPONS AND ARMOR
			npc.set_tag("Weapon", self.resource_loader.get_weapon(rng, npc.get_tag('Class Proficiencies')['weapons']))

			armr_dict = self.resource_loader.get_armor(rng, npc.get_tag('Class Proficiencies')['armor'], npc.get_tag('Abilities')['STR'][0])
			npc.set_tag('Armor', f"{armr_dict['name']}, Stealth Dis.: {armr_dict['stealth_dis']}")

			


	
		

		## AC AND HP
		### AC
		if npc.get_tag('class_bool'):
			ac = int(armr_dict['ac']) + npc.get_tag('Abilities')['DEX'][1]

			if 'shield' in npc.get_tag('Class Proficiencies')['armor']:
				if rng.random() <= 0.25:
					ac += 2
					npc.set_tag('Armor', f"{npc.get_tag('Armor')}, Shield (+2): True")

			npc.set_tag('AC', ac)
		else:
			npc.set_tag('AC', 10 + npc.get_tag('Abilities')['DEX'][1])

		### HP
		die = 8 if 'medium' in npc.get_tag('Appearance')['size'][0] else 6
		hp = np.array(rng.choice(die, npc.get_tag('Level')) + 1) + npc.get_tag('Abilities')['CON'][1]
		
		npc.set_tag('Hit Points', max(sum(hp), 1))



		self.frames['MainFrame'].NPC_GUI(npc, rng)

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
		# child.description = child.canvas.create_text(350, 50, anchor='nw', text=f"Description:\n\n{s}", font=('Arial', 18), width=500) 

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

			score = max(min(var, 20), 1) if not npc.get_tag('Uncapped Abilities') else var
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
				choice = rng.choice(choices, p=[0.19, 0.27, 0.27, 0.27])
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
			score = max(min(var, 20), 1) if not npc.get_tag('Uncapped Abilities') else var

			final[ability] = (score, (score-10)//2)

		return final

	def show_frame(self, frame_name):
		self.frames[frame_name].tkraise()

	def start(self):
		self.parent.mainloop()

Generator(tk.Tk()).start()