import tkinter as tk
from numpy.random import default_rng
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk

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
								'Occupation':['--CLASSES--', *sorted(self.controller.resource_loader.get_list('classes')), '--JOBS--', *sorted(self.controller.resource_loader.get_list('occupations'))],
								'Level':[*list(map((str), np.arange(1, 21))), '--Low (1-4)--', '--Medium (5-9)--', '--High (10-20)--'],
								'Uncapped Abilities':['True', 'False']
							}

		self.createGUI()

	def createGUI(self):
		self.canvas = tk.Canvas(self, width=1430, height=800, highlightthickness=0)
		self.canvas.place(relx=0, rely=0, anchor='nw')

		self.text_lbls = {}

		for var in self.vars_list:
			lbl = tk.Label(self, text=var, font=('gothic', 18))
			lbl.place(relx=0.1, rely=((0.1 + self.vars_list.index(var)/8)-0.035), anchor='c')

			string_var = tk.StringVar(self, '--Random--')
			self.string_vars[var] = string_var
			
			opt_m = tk.OptionMenu(self, string_var, *['--Random--', *self.var_choices[var]])
			opt_m.config(font=('gothic', 18), width=20)
			opt_m.place(relx=0.1, rely=(0.1 + self.vars_list.index(var)/8), anchor='c')

			lbl2 = tk.Label(self, text=f"{var}: ?", font=('gothic', 18))
			lbl2.place(relx=0.23, rely=(0.1 + 0.05*(self.vars_list.index(var))), anchor='w')

			self.text_lbls[var] = lbl2

		self.canvas.create_line(300, 0, 300, 800, fill="black", width=20)

		gen_btn = tk.Button(self, text='Generate', font=('Good Times', 30), fg='#9b0707', relief='groove', command=self.controller.generate)
		gen_btn.place(relx=0.1, rely=0.9, anchor='c')


class Generator():
	def __init__(self, parent):
		self.parent = parent
		self.frames = {}

		self.rng = default_rng(seed=42)
		self.resource_loader = ResourceLoader()

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
		self.rng = default_rng()

		child = self.frames['MainFrame']

		vars_dict = {}

		for opt_var in child.vars_list:
			str_var = child.string_vars[opt_var].get()
			
			if str_var == "--Random--":
				list_ = []

				for obj in child.var_choices[opt_var]:
					if obj[0] != "-":
						list_.append(obj)

				var = self.rng.choice(list_)

			else:				
				if opt_var == 'Level':
					levels = {'L':(3, 1), 'M':(4, 5), 'H':(10, 10)}
					if str_var[2] in levels.keys():
						var = round(self.rng.random()*levels[str_var[2]][0]+levels[str_var[2]][1])
					else:
						var = str_var
				
				if opt_var == 'Occupation':
					if str_var == '--CLASSES--':
						var = self.rng.choice(sorted(self.resource_loader.get_list('classes')))
					elif str_var == '--JOBS--':
						var = self.rng.choice(sorted(self.resource_loader.get_list('occupations')))
					else:
						var = str_var

			vars_dict[opt_var] = var

			child.text_lbls[opt_var].config(text=f"{opt_var}: {var}")
			# lbl = tk.Label(child., text=f"{opt_var}: {vars_dict[opt_var]}", font=('gothic', 18)).place(x=350, y=50+(75*(list(child.var_choices.keys()).index(opt_var))), anchor='w')
			
			# child.text_canvas.create_text(350, 50+(75*(list(child.var_choices.keys()).index(opt_var))), text=f"{opt_var}: {vars_dict[opt_var]}", anchor='w')


	def show_frame(self, frame_name):
		self.frames[frame_name].tkraise()

	def start(self):
		self.parent.mainloop()

Generator(tk.Tk()).start()