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
			speeds[speed.get('key')] = speed.get('value')

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

		h_w_dict = {h_w.tag:h_w.get('value') for h_w in race_type.find('appearences').find('height_weight')}

		return h_w_dict

	def get_age(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)
		
		age_elmt = race_type.find('appearences').find('age')

		return [age_elmt.get('maturity'), age_elmt.get('lifespan')]

	def get_racial_features(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)
		feature_xml = self.get_xml_root('features')

		feature_dict = {}
		
		for race_feature in race_type.find('features'):
			race_feature_id = race_feature.get('id')
			for feature in feature_xml:
				if feature.get('id') == race_feature_id:
					sub_features = {}
					for sub_feature in feature.findall('sub_feature'):
						sub_features[sub_feature.get('key')] = sub_feature.get('value')

					feature_dict[feature.get('id')] = {'lvl_req':feature.get('lvl_req'), 'type':feature.get('type'), 'sub_features':sub_features}

		return feature_dict

	def get_base_class_proficiencies(self, occupation_id):
		class_xml = self.get_xml_root('classes')

		prof = {'armor':[], 'weapons':[], 'tools':['random'], 'saving_throws':[], 'skills':[1]}
		
		for class_ in class_xml.findall('class'):
			if class_.get('name') == occupation_id:
				for proficiency in class_.find('proficiencies'):
					prof[proficiency.tag] = [t.get('value') for t in proficiency.findall('type')]

		return prof

	def get_equipment_list(self, l_type):
		xml = self.get_xml_root(f'{l_type}s')
		return [equipment.attrib for equipment in xml.findall(l_type)]



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

	# def get_subclass(self, rng, class_id):
	# 	subclasses = self.get_xml_root('subclasses')

	# 	subclass = [subclass for subclass in subclasses.findall('subclass') if subclass.get('class') == class_id][rng.choice(np.arange(len(subclasses.findall('subclass'))))]

	# 	return subclass.get('name')


	# def get_weapon(self, rng, prof):
	# 	weapons = self.get_xml_root('weapons')

	# 	a = []
	# 	for weapon in weapons:
	# 		if weapon.get('type') in prof:
	# 			a.append(f"{weapon.get('name')} ({weapon.get('damage')}, {weapon.get('properties')})")

	# 	if len(a) == 0:
	# 		return f"Unarmed Attack: 1 + STR MOD"
	# 	else:
	# 		return rng.choice(a)


	# def get_armor(self, rng, prof, str_):
	# 	b = prof.copy()
	# 	if 'shield' in b:
	# 		b.remove('shield')

	# 	armors = self.get_xml_root('armors')
 		
	# 	a = []
	# 	for armor in armors:
	# 		if armor.get('type') in b and int(armor.get('str_req')) <= str_:
	# 			d = {}
	# 			for att in armor.attrib:
	# 				if att != 'stealth_dis':
	# 					d[att] = armor.attrib[att]
	# 				else:
	# 					d[att] = bool(armor.attrib[att])

	# 			a.append(d)

	# 	if len(a) == 0:
	# 		return {'name':'Unarmored', 'ac':'10', 'stealth_dis':'False'}
	# 	else:
	# 		return rng.choice(a)

	# def get_class_features(self, rng, class_id, subclass_id, lvl):
	# 	classes = self.get_xml_root('classes')
	# 	subclasses = self.get_xml_root('subclasses')

	# 	a = {}

	# 	for class_ in classes:
	# 		if class_.get('name') == class_id:
	# 			for dataval in class_.findall('datadict')[0].findall('dataval'):
	# 				if dataval.get('key') == 'features':
	# 					for feat in dataval.findall('feature'):
	# 						if int(feat.get('req')) <= lvl:
	# 							key = feat.get('key')
	# 							val = feat.get('value')

	# 							if val == 'dict_lvl_choice':
	# 								aa = []

	# 								for l in feat.findall('lvl'):
	# 									if int(l.get('key')) <= lvl:
	# 										aa.extend(l.get('value').split(':'))

	# 								a[key] = f"{aa[rng.choice(np.arange(len(aa)))]}"
								
	# 							elif '|' in val:
	# 								aa = val.split('|')
	# 								ab = aa[-1].split(';')
	# 								ac = list(rng.choice(ab[1:], int(ab[0]), replace=False))
	# 								a[key] = ac

	# 							elif val == 'dict_spellcasting':
	# 								aa = {}
	# 								for prop in feat.findall('property'):
	# 									aa[prop.get('key')] = prop.get('value')

	# 								a[key] = aa

	# 							else:	
	# 								a[key] = val

	# 	for subclass in subclasses:
	# 		if subclass.get('class') == class_id and subclass.get('name') == subclass_id:
	# 			for dataval in subclass.findall('datadict')[0].findall('dataval'):
	# 				if int(dataval.get('req')) <= lvl:
	# 					key = dataval.get('key')
	# 					val = dataval.get('value')

	# 					if val == 'dict_lvl':
	# 						aa = []

	# 						if key == 'extended_spell_list':
	# 							aa.append(dataval.get('tier'))

	# 						for item in dataval.findall('item'):
	# 							if int(item.get('key')) <= lvl:
	# 								item_val = item.get('value')
	# 								if ':' in item_val:
	# 									aa.extend(item_val.split(':'))

	# 								elif ';' in item_val:
	# 									ab = item_val.split(';')
	# 									aa.extend(list(rng.choice(ab[1:], int(ab[0]), replace=False)))

	# 						a[key] = aa

	# 					else:
	# 						a[key] = val

	# 	return a

	# def get_feat(self, rng):
	# 	feats = self.get_xml_root('feats')
	# 	return list(feats)

	# def get_feat_data(self, rng, feat, npc):
	# 	a = {'name':feat.get('name')}

	# 	for dataval in feat.findall('datadict')[0].findall('dataval'):
	# 		key = dataval.get('key')
	# 		val = dataval.get('value')
	# 		if len(val) > 0:
	# 			if key == 'asi':	
	# 				if ';' in val:
	# 					aa = val.split(';')
	# 					ab = rng.choice(aa[1:], int(aa[0]), replace=False)
	# 					ac = ab[0].split(',')
	# 				else:
	# 					ac = val.split(',')

	# 				a[key] = (ac[0], ac[1])

	# 			elif key == 'extended_spell_list':
	# 				aa = val.split(':')
	# 				ab = {'tier':1}

	# 				if npc.get_tag('class_bool'):
	# 					if 'Spellcasting' not in npc.get_tag('Features'):
	# 						ab['Spellcasting Ability'] = aa[0]
	# 					else:
	# 						ab['Spellcasting Ability'] = npc.get_tag('Features')['Spellcasting']['Spellcasting Ability']

	# 				else:
	# 					ab['Spellcasting Ability'] = aa[0]

	# 				spells = []
					
	# 				for ac in aa[1:]:
	# 					ad = ac.split(',')
	# 					ae = ad[-1].split('_')
	# 					spell_list = self.get_spells(*ae, class_spec=npc.get_tag('Only Class Specific Spells'))

	# 					for _ in range(int(ad[0])):
	# 						spells.append(spell_list[rng.choice(np.arange(len(spell_list)))].get('name'))

	# 				ab['extended_spell_list'] = spells

	# 				a[key] = ab

	# 			else:
	# 				if ';' in val and dataval.get('req') is None:
	# 					aa = val.split(';')
	# 					ab = list(rng.choice(aa[1:], int(aa[0]), replace=False))

	# 					a[key] = ab[0]

	# 				elif ';' in val and dataval.get('req') is not None:
	# 					aa = dataval.get('req').split('|')

	# 					if npc.get_tag('Level') >= int(aa[0]) and rng.random() < float(aa[1]):
	# 						ab = val.split(';')
	# 						ac = list(rng.choice(ab[1:], int(ab[0]), replace=False))

	# 						a[key] = ac[0]
					
	# 				else:
	# 					a[key] = val

						

	# 	return a

	# def get_spells(self, level="", class_id="", class_spec=True):
	# 	spells = self.get_xml_root('spells')
	# 	a = []

	# 	for spell in spells:
	# 		if level == "" and class_id == "":
	# 			a.append(spell)
	# 		else:
	# 			if spell.get('level') == level and class_id in spell.get('availability') and class_spec:
	# 				a.append(spell)
	# 			elif not class_spec and spell.get('level') == level:
	# 				a.append(spell)


	# 	return a

	# def get_traits(self, rng, n):
	# 	traits = self.get_xml_root('traits')

	# 	b = {}
		
	# 	for trait in traits:
	# 		b[trait.get('name')] = trait.get('description')

	# 	keys = list(b.keys())
	# 	rng.shuffle(keys)

	# 	return {k:b[k] for k in keys[:n]}

	# def get_ability_for_skill(self, name):
	# 	skills = self.get_xml_root('skills')

	# 	for skill in skills:
	# 		if skill.get('name') == name:
	# 			return skill.get('ability')

	# 	return None


	@staticmethod
	def get_instance():
		if ResourceLoader.instance is not None:
			return ResourceLoader.instance
		else:
			ResourceLoader.instance = ResourceLoader()
			return ResourceLoader.instance


