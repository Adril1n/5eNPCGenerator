import xml.etree.ElementTree as ET
import numpy as np

class ResourceLoader():
	instance = None

	def __init__(self):
		self.xml_files = {}


	def get_xml_root(self, xml_name):
		filename = 'xml_files/' +  xml_name + '.xml'
		try: 
			root = self.xml_files[xml_name]
		except KeyError:
			tree = ET.parse(filename)
			root = tree.getroot()
			self.xml_files[xml_name] = root
		return root


	def get_name_list(self, race, sex):
		names = self.get_xml_root('names')

		options = []

		for name_list in names:
			if name_list.get('race') == race:
				if name_list.get('sex') == sex or name_list.get('sex') is None:
					for name in name_list:
						options.append(name.get('value'))

		return options




	def get_list(self, xml):
		root = self.get_xml_root(xml)
		l = []

		for obj in root:
			l.append(obj.get('name'))

		return sorted(l)

	def get_occupation_description(self, occ_id):
		jobs = self.get_xml_root('jobs')
		
		for job in jobs:
			if job.get('name') == occ_id:
				return job.get('description')

		return "Nothing"

	def get_race_type_choices(self, race_id):
		races = self.get_xml_root('races')

		l = []

		for race in races:
			if race.get('name') == race_id:
				for t in race.findall('type'):
					l.append(t.get('name')) 

		return l

	def get_race_type(self, race_id, race_type_id):
		races = self.get_xml_root('races')
		
		for race in races:
			if race.get('name') == race_id:
				for race_type in race.findall('type'):
					if race_type.get('name') == race_type_id:
						return race_type
		return None

	def get_race_asi(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)

		asi_dict = {k:v for k, v in [(a.get('key'), a.get('value')) for a in race_type.find('abilities').findall('ability')]}

		return asi_dict

	def get_size(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)

		return race_type.find('size').get('value')

	def get_speeds(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)

		speeds = {}

		for speed in race_type.find('speeds'):
			speeds[speed.get('key')] = int(speed.get('value'))

		return speeds

	def get_languages(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)

		languages = []

		for language in race_type.find('languages'):
			languages.append(language.get('value'))

		return languages

	def get_darkvision(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)

		try:
			return race_type.find('darkvision').get('value')
		except AttributeError:
			return None

	def get_height_weight(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)

		h_w_dict = {h_w.tag:h_w.get('value') for h_w in race_type.find('appearances').find('height_weight')}

		return h_w_dict

	def get_age(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)
		
		age_elmt = race_type.find('appearances').find('age')

		return [age_elmt.get('maturity'), age_elmt.get('lifespan')]

	def get_racial_features(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)
		feature_xml = self.get_xml_root('features')

		feature_dict = {}
		
		for race_feature in race_type.find('features'):
			race_feature_id = race_feature.get('id')
			for feature in feature_xml:
				if race_feature_id in feature.get('id'):
					sub_features = {}
					for sub_feature in feature.findall('sub_feature'):
						sub_features[sub_feature.get('key')] = sub_feature.get('value')

					feature_dict[feature.get('id')] = {'lvl_req':feature.get('lvl_req'), 'type':feature.get('type'), 'sub_features':sub_features}

		return feature_dict

	def get_features(self, xml_type, wanted_element_id, rng):
		xml = self.get_xml_root(xml_type)
		feature_xml = self.get_xml_root('features')

		feature_dict = {}

		previous_choices = []
		
		for element in xml:
			if element.get('name') == wanted_element_id:
				for element_feature in element.find('features').findall('feature'):
					element_feature_id = element_feature.get('id')
					if element_feature_id == 'choice':
						duplicates = bool(int(element_feature.get('duplicates')))
						choices = [c.get('id') for c in element_feature.findall('choice')]
						if not duplicates:
							while True:
								element_feature_id = rng.choice(choices)
								if element_feature_id not in previous_choices:
									previous_choices.append(element_feature_id)
									break
								elif previous_choices >= choices:
									break
						else:
							element_feature_id = rng.choice(choices)
							previous_choices.append(element_feature_id)

					for feature in feature_xml:
						if element_feature_id in feature.get('id'):
							sub_features = {}
							for sub_feature in feature.findall('sub_feature'):
								sub_features[sub_feature.get('key')] = sub_feature.get('value')

							feature_dict[feature.get('id')] = {'lvl_req':feature.get('lvl_req'), 'type':feature.get('type'), 'sub_features':sub_features}

		return feature_dict

	def get_feat_asi(self, feat_id):
		feats = self.get_xml_root('feats')

		asi_dict = {}
		for feat in feats:
			if feat.get('name') == feat_id:
				asi_dict = {k:v for k, v in [(a.get('key'), a.get('value')) for a in feat.find('abilities').findall('ability')]}

		return asi_dict

	def get_feat_description(self, feat_id):
		feats = self.get_xml_root('feats')

		for feat in feats:
			if feat.get('name') == feat_id:
				return feat.find('description').get('value')

		return "N/A"

	def get_feat_description_extensions(self, feat_id):
		feats = self.get_xml_root('feats')
	
		desc_ext = []
		for feat in feats:
			if feat.get('name') == feat_id:
				for de in feat.findall('description_extension'):
					desc_ext.append([de.get('prob'), de.get('value')])

		return desc_ext

	def get_base_class_proficiencies(self, occupation_id):
		class_xml = self.get_xml_root('classes')

		prof = {'armors':[], 'weapons':[], 'tools':['random'], 'saving_throws':[], 'skills':[1]}
		
		for class_ in class_xml.findall('class'):
			if class_.get('name') == occupation_id:
				for proficiency in class_.find('proficiencies'):
					prof[proficiency.tag] = [t.get('value') for t in proficiency.findall('type')]

		return prof

	def get_equipment_list(self, l_type):
		xml = self.get_xml_root(f'{l_type}s')
		return [equipment.attrib for equipment in xml.findall(l_type)]



	def get_table(self, table_id):
		tables = self.get_xml_root('random_tables')

		items = []

		for table in tables:
			if table.get('name') == table_id:
				for item in table.findall('item'):
					items.append(item.get('value'))

		return items

	def get_subclass(self, occ_id):
		subclasses = self.get_xml_root('subclasses')

		for subclass in subclasses:
			if subclass.get('class') == occ_id:
				return subclass.get('name')

		return None

	def get_spellcasting_ability(self, occ_id, subclass_id):
		classes = self.get_xml_root('classes')
		subclasses = self.get_xml_root('subclasses')

		for class_ in classes:
			if class_.get('name') == occ_id:
				spll_casting = class_.find('spellcasting')
				if spll_casting is not None:
					return (spll_casting.get('ability'), spll_casting.get('spells_per_level'))

		for subclass in subclasses:
			if subclass.get('name') == subclass_id:
				spll_casting = subclass.find('spellcasting')
				if spll_casting is not None:
					return (spll_casting.get('ability'), spll_casting.get('spells_per_level'))

		return ('random', "0:0:0")

	def get_spell_lvl_list(self, s_l_type):
		spells = self.get_xml_root('spells')

		spl_l = []
		for spell in spells:
			if s_l_type in spell.get('availability'):
				spl_l.append(spell.get('level'))

		return spl_l

	def get_spell_list(self, s_l_type, s_lvl):
		spells = self.get_xml_root('spells')

		choices = []

		for spell in spells:
			if s_l_type in spell.get('availability') and spell.get('level')[0] == str(s_lvl):
				choices.append([spell.get('name'), spell.get('level')])

		return choices

	def get_lvl_for_spell(self, spell_name):
		spells = self.get_xml_root('spells')

		for spell in spells:
			if spell.get('name') == spell_name:
				return spell.get('level')

		return "N/A"

	def get_trait_description(self, trait_id):
		traits = self.get_xml_root('traits')

		for trait in traits:
			if trait.get('name') == trait_id:
				return trait.get('description')

		return "N/A"

	def get_pet_choices(self, cr):
		pets = self.get_xml_root('pets')

		choices = []
		for pet in pets:
			if int(pet.get('cr')) == cr:
				choices.append(pet.get('name'))

		return choices

	def get_pet_attribs(self, pet_id):
		pets = self.get_xml_root('pets')

		data_dict = {}

		for pet in pets:
			if pet.get('name') == pet_id:
				for dataval in pet.findall('dataval'):
					data_dict[dataval.get('key')] = dataval.get('value')

		return data_dict

	def get_gear_choices(self, prof, xml, str_score=0):
		gears = self.get_xml_root(xml)

		choices = []
		for gear in gears:
			if gear.get('type') in prof[xml]:
				if xml == 'armors':
					if int(gear.get('str_req')) <= str_score:
						choices.append(gear.attrib)
				else:
					choices.append(gear.attrib)

		return choices

	def get_skin_type(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)

		return race_type.find('appearances').find('skin_type').get('value')

	def get_appearance_details(self):
		appearances = self.get_xml_root('appearances')

		dict_ = {}

		for appearance in appearances.findall('appearance'):
			dict_[appearance.get('name')] = [option.get('value') for option in appearance.findall('option')]

		return dict_

	def get_gods(self):
		gods = self.get_xml_root('gods')

		gods_dict = {}

		for god in gods:
			gods_dict[god.get('name')] = {dataval.get('key'):dataval.get('value') for dataval in god.findall('dataval')}

		return gods_dict

	def get_spell_features(self, spell_id):
		spells = self.get_xml_root('spells')

		spell_features = {}

		for spell in spells:
			if spell.get('name') == spell_id:
				spell_features['level'] = spell.get('level')
				spell_features['availability'] = spell.get('availability')
				spell_features['casting_time'] = spell.get('casting_time')
				spell_features['duration'] = spell.find('duration').get('value')
				spell_features['school'] = spell.find('school').get('value')
				spell_features['range'] = spell.find('range').get('value')
				spell_features['components'] = spell.find('components').get('value')
				spell_features['description'] = spell.find('description').get('value')
				spell_features['higher_levels'] = spell.find('higher_levels').get('value')


		return spell_features









	def get_recent_npcs(self):
		npcs = self.get_xml_root('recent_npcs')

		npcs_dict = {}

		for npc in npcs:
			npcs_dict[f"{npc.get('name')}, {npc.get('race')} {npc.get('occupation')}"] = npc.get('rng')

		return npcs_dict



	@staticmethod
	def get_instance():
		if ResourceLoader.instance is not None:
			return ResourceLoader.instance
		else:
			ResourceLoader.instance = ResourceLoader()
			return ResourceLoader.instance


