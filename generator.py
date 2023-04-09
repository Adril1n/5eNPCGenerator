import tkinter as tk
from numpy.random import default_rng
import numpy as np
import xml.etree.ElementTree as ET

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

class MainFrame(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		
		self.vars = {}

		self.vars_list = ['Race', 'Sex', 'Occupation', 'Level']
		self.var_choices = 	{
								'Race':['Aasimar', 'Dwarf'], 
								'Sex':['Male', 'Female'], 
								'Occupation':['Barber', 'Carriage Driver', 'Domestic Servant', 'Gardener', 'Groom Guide'],
								'Level':[*np.arange(1, 21), 'Low (1-4)', 'Medium (5-9)', 'High (10-20)']
							}

		self.createGUI()

	def createGUI(self):
		self.canvas = tk.Canvas(self, width=1430, height=800, highlightthickness=0)
		self.canvas.place(relx=0, rely=0, anchor='nw')

		for var in self.vars_list:
			lbl = tk.Label(self, text=var, font=('gothic', 18))
			lbl.place(relx=0.1, rely=((0.1 + self.vars_list.index(var)/8)-0.035), anchor='c')

			string_var = tk.StringVar(self, 'Random')
			opt_m = tk.OptionMenu(self, string_var, *['Random', *self.var_choices[var]])
			opt_m.config(font=('gothic', 18), width=20)
			opt_m.place(relx=0.1, rely=(0.1 + self.vars_list.index(var)/8), anchor='c')


		self.canvas.create_line(300, 0, 300, 800, fill="black", width=20)

		gen_btn = tk.Button(self, text="Generate", font=('gothic', 40))
		gen_btn.place(relx=0.1, rely=0.9, anchor='c')


class Generator():
	def __init__(self, parent):
		self.parent = parent
		self.frames = {}

		self.rng = default_rng(seed=42)

		self.createGUI()

	def createGUI(self):
		self.parent.title('5e NPC Generator')
		self.parent.geometry('1430x800')

		container = tk.Frame(self.parent)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		## could add more frames here with for-loop
		frame = MainFrame(container)
		self.frames[MainFrame.__name__] = frame
		frame.grid(row=0, column=0, sticky='nsew')

		self.show_frame('MainFrame')

	def show_frame(self, frame_name):
		self.frames[frame_name].tkraise()

	def start(self):
		self.parent.mainloop()

Generator(tk.Tk()).start()