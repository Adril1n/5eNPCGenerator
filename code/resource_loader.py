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
		
		for feature in race_type.find('features'):
			feature_id = feature.get('id')
			for feature_desc in feature_xml:
				if feature_desc.get('id') == feature_id:
					feature_dict[feature_id] = feature_desc.get('description')

		return feature_dict

	def get_race_actions(self, race_id, race_type_id):
		race_type = self.get_race_type(race_id, race_type_id)
		actions_xml = self.get_xml_root('actions')

		actions_dict = {}
		
		for race_action in race_type.find('actions'):
			action_id = race_action.get('id')
			for action in actions_xml:
				if action.get('id') == action_id:
					attribs = action.attrib.copy()
					attribs.pop('id')
					attribs.pop('type')
					actions_dict[action_id] = [action.attrib.copy()['type'], attribs]

		return actions_dict



	

	# def get_race_ability_bonuses(self, abilities, rng, race_id, subrace_id):
	# 	races = self.get_xml_root('races')

	# 	a = {}

	# 	for race in races:
	# 		if race.get('name') == race_id:
	# 			for type_ in race.findall('type'):
	# 				if type_.get('name') == subrace_id:
	# 					datavals = type_.findall('datadict')[0].findall('dataval')

	# 					for dataval in datavals:
	# 						if dataval.get('key') == 'abilities':
	# 							if dataval.get('value') == 'dict':
	# 								for ability in dataval.findall('ability'):
	# 									a[ability.get('key')] = ability.get('value')

	# 							elif dataval.get('value') == 'dict_choice':
	# 								ability = dataval.findall('ability')[rng.choice(np.arange(len(dataval.findall('ability'))))] 

	# 								keys = list(abilities.keys())

	# 								nums = ability.get('value').split(':')
	# 								for num in nums:
	# 									ablt = rng.choice(keys)
	# 									a[ablt] = num
	# 									keys.pop(keys.index(ablt))



	# 	return a

	# def get_proficiencies(self, rng, npc_class):
	# 	classes = self.get_xml_root('classes')

	# 	a = {}

	# 	for class_ in classes:
	# 		if class_.get('name') == npc_class:
	# 			for dataval in class_.findall('datadict')[0].findall('dataval'):
	# 				if dataval.get('key') == 'proficiencies':
	# 					for prof in dataval.findall('proficiency'):
	# 						key = prof.get('key')
	# 						val = prof.get('value')

	# 						if ':' in val and ';' not in val:
	# 							aa = val.split(':')
	# 							a[key] = aa
	# 						elif ';' in val and ':' not in val:
	# 							aa = val.split(';')
	# 							a[key] = list(rng.choice(aa[1:], int(aa[0]), replace=False))
	# 						elif ';' in val and ':' in val:
	# 							aa = val.split(':')
	# 							ab = aa[-1].split(';')
	# 							ac = list(rng.choice(ab[1:], int(ab[0]), replace=False))

	# 							ad = []

	# 							for p in (*aa[:-1], *ac):
	# 								ad.append(f"{p} {key}")

	# 							a[key] = ad
	# 						else:
	# 							a[key] = [val]

		

	# 	return a

	# def get_appearances(self, rng, race_id, subrace_id):
	# 	races = self.get_xml_root('races')

	# 	a = {}

	# 	for race in races:
	# 		if race.get('name') == race_id:
	# 			for subrace in race.findall('type'):
	# 				if subrace.get('name') == subrace_id:
	# 					for dataval in subrace.findall('datadict')[0].findall('dataval'):
	# 						if dataval.get('key') == 'appearances':
	# 							for app in dataval.findall('appearance'):
	# 								key = app.get('key')
	# 								val = app.get('value')

	# 								if ':' not in val and ';' not in val and '-' not in val:
	# 									a[key] = [val]
	# 								elif ':' in val and ';' not in val and '-' not in val:
	# 									aa = val.split(':')
	# 									a[key] = aa
	# 								elif ':' not in val and ';' in val and '-' not in val:
	# 									aa = val.split(';')
	# 									a[key] = list(rng.choice(aa[1:], int(aa[0]), replace=False))
	# 								else:
	# 									aa = val.split('-')
	# 									ab = rng.integers(int(aa[0]), high=int(aa[1])+1)

	# 									if key == 'age':
	# 										age_dict = {0.35:'Young', 0.75:'Middle Aged', 10:'Elderly'}
	# 										ac = ''
	# 										for bin_ in age_dict:
	# 											if ab/int(aa[1]) <= bin_:
	# 												ac = age_dict[bin_]
	# 												break

	# 										ab = f"{ab} ({ac})"

	# 										a[key] = [ab]
	# 									else:
	# 										a[key] = [ab, (aa[0], aa[1])]

	# 	return a 

	# def get_languages_or_speeds(self, rng, race_id, subrace_id, tt):
	# 	races = self.get_xml_root('races')

	# 	a = []

	# 	for race in races:
	# 		if race.get('name') == race_id:
	# 			for subrace in race.findall('type'):
	# 				if subrace.get('name') == subrace_id:
	# 					for dataval in subrace.findall('datadict')[0].findall('dataval'):
	# 						d = {'lan':'language', 'spd':'speed'}

	# 						if dataval.get('key') == f"{d[tt]}s":
	# 							for lan in dataval.findall(d[tt]):
	# 								key = lan.get('key')
	# 								val = lan.get('value')

	# 								if 'random' in key:
	# 									l = ['Common', 'Dwarvish', 'Elvish', 'Giant', 'Gnomish', 'Goblin', 'Halfling', 'Orc', 'Abyssal', 'Celestial', 'Draconic', 'Deep Speech', 'Infernal', 'Primordial', 'Sylvan', 'Undercommon']
	# 									l = list(filter(lambda x: x not in [y.get('key') for y in dataval.findall(d[tt])], l))
	# 									key = rng.choice(l)

	# 								a.append(f"{key} ({val})")

	# 	return a


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

	# def get_subclass(self, rng, class_id):
	# 	subclasses = self.get_xml_root('subclasses')

	# 	subclass = [subclass for subclass in subclasses.findall('subclass') if subclass.get('class') == class_id][rng.choice(np.arange(len(subclasses.findall('subclass'))))]

	# 	return subclass.get('name')

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


