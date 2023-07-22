def statblock_abilities(npc, ability_str):
	html = ""

	ability = npc.abilities[ability_str]
	html += f'<div style="text-align: center;"><span style="font-weight: bold;">{ability_str[:3]}</span><br>'
	mod = ability.get_modifier()
	html += f'{ability.score} ({f"+{mod}" if mod >= 0 else mod})'
	html += '</div>'

	return html

def statblock_saving_throws(npc, st_ab):
	html = ""

	mod = npc.abilities[st_ab].get_modifier() + npc.get_proficiency_bonus() + npc.bonuses[f"{st_ab}_saving_throw"]
	html += f'{st_ab[:3]} {f"+{mod}" if mod >= 0 else mod} '

	return html

def statblock_skills(npc, skill):
	html = ""

	mod = npc.get_skill(skill) + npc.get_proficiency_bonus()
	html += f'{skill} {f"+{mod}" if mod >= 0 else mod} '

	return html

def statblock_weapon(npc):
	html = ""

	name = npc.weapon['name']
	html += f'<div style="margin-bottom: 16px;"><span style="font-weight: bold;">{name}. </span>'
	dmg = npc.weapon['damage'].split(';')
	
	wep_th = npc.get_weapon_to_hit()
	wep_dmg = npc.get_weapon_damage()

	html += f'{f"+{wep_th}" if wep_th >= 0 else wep_th} to hit, {dmg[0]} {f"+ {wep_dmg}" if wep_dmg >= 0 else wep_dmg} {dmg[1]} damage.'
	html += '</div>'

	return html

def statblock_descriptions(npc):
	html = ""

	for feature in npc.features.keys():
		if 'Description' in feature:
			html += '<div class="preview-content_statblock_description"> <span style="font-weight: bold;">'
			html += f'{feature}. </span>'
			html += npc.features[feature].get_sub_feature('description').replace('BREAK', '<br>')
			html += '</div>'

	return html


def description_table_item(npc, appearance):
	html = ""


	html += f'<div class="preview-content_description_table_item" style="margin-right: 10px;">'

	str_ = str(npc.appearances[appearance]) if 'color' not in appearance else str(npc.appearances[appearance][1])
	html += f'{appearance.title()}<br>{str_[0].upper()}{str_[1:]}'

	if appearance == 'height':
		html += ' cm'
	elif appearance == 'weight':
		html += ' kg<br>'
		html += f'({npc.get_weight_bin().title()})'
	elif appearance == 'age':
		age_bin = npc.get_age_bin()
		html += f' (Human years: {round(age_bin[1])})<br>({age_bin[0]})'
	elif 'color' in appearance:
		html += f'<br><svg width="100" height="25" style="margin-top:3px;fill:{npc.appearances[appearance][0]};stroke-width: 2px;stroke: white;"> <rect width="100" height="25"></rect> </svg>'
	elif appearance == 'skin':
		html += f', {npc.appearance_details["skin_detail"]}'

	html += '</div>'


	return html








def preview_page(npc):
	html = ""

	html += '	<div class="preview-header"> <div class="preview-header_summary"> <div style="font-size: 32px;font-weight: bold;">'
	html += 	npc.name
	html += '	</div> <div>'
	html += f'	{npc.options["sex"].value} {npc.options["race"].value} {npc.options["occupation"].value}'
	html += '	</div> <div>'
	html += f'	Level {npc.options["level"].value}'
	html += '	</div>'

	if len(npc.feats) != 0:
		html += f'<div>Feats: {", ".join(list(npc.feats.keys()))}</div>'

	html += '</div> </div>'

	### STATBLOCK
	html += '<div class="preview-content">'
	html += '<div class="preview-content_statblock">'

	html += f'<div style="font-size:40px;font-weight: bold;">{npc.name} (Level {npc.get_option_value("level")} {f"{npc.subclass}," if npc.subclass is not None else ""} {npc.get_option_value("occupation")})</div>'
	html += f'<div style="font-style: italic;">{npc.size.title()} humaniod ({npc.get_option_value("race")})</div>'
	html += '<svg height="10" width="100%" class="npc_statblock_break"> <polyline points="0,0 700, 5 0,10"></polyline> </svg>'

	html += f'<div><span style="font-weight: bold;">Armor Class</span>{npc.get_ac()} ({npc.armor["name"]})</div>'
	html += f'<div><span style="font-weight: bold;">Hit Points:</span><span contenteditable="true">{npc.get_hit_points()}</span>/{npc.get_hit_points()}</div>'
	html += f'<div><span style="font-weight: bold;">Speed</span>: {npc.get_speeds()["Walking Speed"]} ft.</div>'
	html += '<svg height="10" width="100%" class="npc_statblock_break"> <polyline points="0,0 700, 5 0,10"></polyline> </svg>'

	html += '<div class="preview-content_statblock_abilities">'

	for ability_str in npc.abilities:
		html += statblock_abilities(npc, ability_str)

	html += '</div>' #preview-content_statblock_abilities
	html += '<svg height="10" width="100%" class="npc_statblock_break"> <polyline points="0,0 700, 5 0,10"> </polyline></svg>'

	if len(npc.proficiencies['saving_throws']) > 0:
		html += '<div> <span style="font-weight: bold;">Saving Throws </span>' 
		for st_ab in npc.proficiencies['saving_throws']:
			html += statblock_saving_throws(npc, st_ab)
		html +='</div>'


	html += '<div> <span style="font-weight: bold;">Skills </span>' 
	for skill_prof in npc.proficiencies['skills']:
		html += statblock_skills(npc, skill_prof)
	html +='</div>'

	html += '<div> <span style="font-weight: bold;">Senses </span>' 
	html += f'Passive Perception {npc.get_skill("Perception") +10}'
	if npc.darkvision is not None:
		html += f', Darkvision {npc.darkvision} ft.'
	html +='</div>'

	html += '<div> <span style="font-weight: bold;">Languages </span>' 
	html += ', '.join(npc.languages)
	html +='</div>'

	html += '<div> <span style="font-weight: bold;">Proficiency Bonus </span>' 
	html += f'+{npc.get_proficiency_bonus()}'
	html +='</div>'
	html += '<svg height="10" width="100%" class="npc_statblock_break"> <polyline points="0,0 700, 5 0,10"> </polyline></svg>'


	html += statblock_weapon(npc)
	html += f'<div style="margin-bottom: 16px;"> <span style="font-weight: bold;">{npc.armor["name"]}. </span>'
	if npc.armor['stealth_mod'] != '0':
		html += f'Disadvantage on Stealth checks due to this armor.'
	html += '</div>'

	html += statblock_descriptions(npc)
	html += '<svg height="10" width="100%" class="npc_statblock_break"> <polyline points="0,0 700, 5 0,10"> </polyline></svg>'

	html += '<a class="preview-content_statblock_href" href="#Description">Description</a> <br> <a class="preview-content_statblock_href" href="#Personality Traits">Personality Traits</a> <br> <a class="preview-content_statblock_href" href="#Features">Features</a> <br> <a class="preview-content_statblock_href" href="#Feats">Feats</a> <br> <a class="preview-content_statblock_href" href="#Actions">Actions</a> <br> <a class="preview-content_statblock_href" href="#Spellcasting">Spellcasting</a>'

	html += '</div>' #preview-content_statblock




	html += '<div class="preview-content_description">'


	html += '<div class="preview-content_description_image"></div>'
	
	html += '<div class="preview-content_description_table">'
	for appearance in npc.appearances:
		html += description_table_item(npc, appearance)
	html += '</div>'


	html += '</div>' #preview-content_description


	html += '</div>' #preview-content


	return html













def sheet_abilities(npc):
	html = ""

	for ability_str in npc.abilities:
		ability = npc.abilities[ability_str]
		html += '<div class="sheet-quick-info_abilities_ability">'


		html += f'<div class="sheet-quick-info_abilities_ability_header">{ability_str}</div>'

		html += '<div class="sheet-quick-info_abilities_ability_modifier">'
		mod = ability.get_modifier()
		html += f'<button type="button" onclick="alert(dice_roll(20, {mod}))" class="sheet-quick-info_abilities_ability_modifier_button">{f"+{mod}" if mod >= 0 else mod}</button>'
		html += '</div>'

		html += f'<div class="sheet-quick-info_abilities_ability_score">{ability.score}</div>'


		html += '</div>' #sheet-quick-info_abilities_ability

	return html

def sheet_saving_throws(npc):
	html = ""

	for ability_str in npc.abilities:
		ability = npc.abilities[ability_str]
		html += '<div class="saving-throws_container">'

		html += f'<div class="saving-throws_ability">{ability_str[:3]}</div>'

		mod = ability.get_modifier() + npc.bonuses[f"{ability_str}_saving_throw"]
		mod += npc.get_proficiency_bonus() if ability_str in npc.proficiencies['saving_throws'] else 0
		html += f'<div class="saving-throws_modifier">{f"+{mod}" if mod >= 0 else mod}</div>'

		html += '</div>'


	return html


def sheet_passive_skills(npc):
	html = ""

	for skill in ('Perception', 'Insight', 'Investigation'):
		if skill != 'Investigation':
			html += '<div class="senses_item">'
		else:
			html += '<div class="senses_item" style="margin-bottom: 0;">'

		html += f'<div class="senses_type">Passive {npc.get_skill_ability(skill)[:3]} ({skill})</div>'
		html += f'<div class="senses_score">{npc.get_skill(skill)+10}</div>'

		html += '</div>'

	return html


def sheet_prof_languages(npc):
	html = ""

	for key in ('Languages', 'Weapons', 'Armor', 'Tools'):
		k = f"{key.lower()}" if key != 'Armor' else 'armors'

		if key == 'Languages' or len(npc.proficiencies[k]) > 0:
			html += '<div class="proficiencies-languages_type">'

			html += f'<span class="proficiencies-languages_type_header">{key}<br></span>'

			if key == 'Languages':
				value = ', '.join(npc.languages)
			else:
				k = f"{key.lower()}" if key != 'Armor' else 'armors'
				value = f', '.join(list(map(lambda x: f"{x[0].upper()}{x[1:]} {key}" if x != 'shields' else f"{x[0].upper()}{x[1:]}", npc.proficiencies[k])))

			html += value

			html += '</div>'

			if key != 'Tools':
				html += '<div class="proficiencies-languages_break"></div>'



	return html


def sheet_skills(npc):
	html = ""

	skills_adv = npc.advantages['skills']
	for skill_str in skills_adv:
		html += '<tr class="skills">'
		

		adv = ['False', 'None', 'True'][max(min(skills_adv[skill_str][0]+1, 2), 0)]
		title = skills_adv[skill_str][1].replace("BREAK", "<br>")
		html += f'<td class="skills"> <div class="skills-advantage-{adv}" title="{title}"></div> </td>'

		html += f'<td class="skills">{npc.get_skill_ability(skill_str)[:3]}</td>'
		html += f'<td class="skills">{skill_str}</td>'

		mod = npc.get_skill(skill_str)
		mod += npc.get_proficiency_bonus() if skill_str in npc.proficiencies['skills'] else 0
		html += f'<td class="skills"> <button type="button" onclick="alert(dice_roll(20, {mod}))" class="skills-bonus-button">{f"+{mod}" if mod >= 0 else mod}</button> </td>'


		html += '</tr>'

	return html

def sheet_stats(npc):
	html = ""

	for stat in ('Hit Points', 'Armor Class', 'Proficiency Bonus', 'Initiative Bonus'):
		html += '<div class="stats_display">'

		split = stat.split(' ')
		html += f'{split[0]}<br>'

		if stat == 'Hit Points':
			html += f'<span class="stats_display_number"><span contenteditable="true">{npc.get_hit_points()}</span> / {npc.get_hit_points()}</span>'
		elif stat == 'Armor Class':
			html += f'<span class="stats_display_number">{npc.get_ac()}</span>'
		elif stat == 'Proficiency Bonus':
			html += f'<span class="stats_display_plus">+</span><span class="stats_display_number">{npc.get_proficiency_bonus()}</span>'
		elif stat == 'Initiative Bonus':
			mod = str(npc.get_intiative_bonus())
			html += f'<span class="stats_display_plus">{mod[0]}</span><span class="stats_display_number">{mod[1:]}</span>'

		html += f'<br>{split[1]}'


		html += '</div>'


	return html


def sheet_speeds(npc):
	html = ""

	for speed_str in npc.speeds:
		speed_values = npc.get_speeds()

		html += f'<div class="speeds_display"><p>{speed_str.title()}<br>{speed_values[f"{speed_str.title()} Speed"]} ft.</p></div>'

	return html

def sheet_defenses(npc):
	html = ""

	for t in npc.defenses:
		for defense in npc.defenses[t]:
			html += '<div class="defenses_display_item">'

			html += f'<div class="defenses_display_icon_immunity">{t[0].upper()}</div>'
			html += f'<span class="defenses_display_item_name" title="Source: {defense[1]}">{defense[0]}</span>'

			html += '</div>'

	return html


def sheet_page(npc):
	html = ""

	html += '<div class="sheet-quick-info">'



	html += '<div class="sheet-quick-info_summary">'

	html += f'<div class="sheet-quick-info_summary_name">{npc.name}</div>'
	html += f'<div>{npc.options["sex"].value} {npc.options["race"].value} {f"{npc.subclass}," if npc.subclass is not None else ""} {npc.options["occupation"].value}</div>'
	html += f'<div>Level {npc.get_option_value("level")}</div>'

	html += '</div>' #sheet-quick-info_summary


	html += '<div class="sheet-quick-info_abilities">'

	html += sheet_abilities(npc)

	html += '</div>' #sheet-quick-info_abilities



	html += '</div>' #sheet-quick-info




	html += '<div class="sheet-sections">'



	html += '<div class="sheet-sections_section_saving_throws">'
	
	html += sheet_saving_throws(npc)
	html += f'<div class="saving-throws_header" style="font-size:18px;margin: 5px 0;">Advantages/Disadvantages are displayed here: {npc.advantages["saving_throws"]}</div>'
	html += '<div class="saving-throws_header">Saving Throws</div>'

	html += '</div>' #sheet-sections_section_saving_throws



	html += '<div class="sheet-sections_section_senses">'


	html += sheet_passive_skills(npc)

	html += '<div class="senses_header">' 
	if npc.darkvision is not None:
		html += f'<p class="senses_header_darkvision">Darkvision {self.darkvision} ft.</p>' 
	else:
		html += f'<p class="senses_header_darkvision">No Darkvision</p>' 
	html += 'Senses </div>'


	html += '</div>' #sheet-sections_section_senses



	html += '<div class="sheet-sections_section_proficiencies_languages">'


	html += '<div class="proficiencies-languages_content">'
	html += sheet_prof_languages(npc)
	html += '</div>' #proficiencies-languages_content

	html += '<div class="proficiencies-languages_header">Proficiencies & Languages</div>'


	html += '</div>' #sheet-sections_section_proficiencies_languages





	html += '<div class="sheet-sections_section_skills">'
	html += '<div class="skills-table">'
	html += '<table class="skills" style="width: 95%;border: none;">'

	html += '<tr class="skills"> <th class="skills" style="width: 15%;"> <abbr title="Advantage">Adv</abbr> </th> <th class="skills" style="width: 15%;"> <abbr title="Modifier">Mod</abbr> </th> <th class="skills" style="width: 50%;">Skill</th> <th class="skills" style="width: 20%;">Bonus</th> </tr> '

	html += sheet_skills(npc)

	html += '</table>'
	html += '</div>' #skills-table
	html += '<div style="font-size: 24px;text-align: center;margin-top: 1%;">Skills</div>'
	html += '</div>' #sheet-sections_section_skills




	html += '<div class="sheet-sections_section_stats">'
	html += '<div class="stats_container">'

	html += sheet_stats(npc)

	html += '</div>' #stats_container
	html += '</div>' #sheet-sections_section_stats




	html += '<div class="sheet-sections_section_speeds">'
	html += '<div class="speeds_container">'

	html += sheet_speeds(npc)

	html += '</div>' #speeds_container
	html += '</div>' #sheet-sections_section_speeds




	html += '<div class="sheet-sections_section_defenses">'
	html += '<div class="defenses_display">'

	html += '<span class="defenses_display_header">Defenses</span>'
	html += sheet_defenses(npc)
 
	html += '</div>' #defenses_display
	html += '</div>' #sheet-sections_section_defenses





	html += '</div>' #sheet-sections

	return html













def text_boxes_description_traits(npc):
	html = ""

	html += '<div class="text-box">'



	html += '<div class="text-box-header" id="Description">Description</div>'

	html += '<div class="description-character-image">IMAGE HERE</div>'
	html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'

	html += '<div>'


	html += f'<div class="description-character-feature">{npc.name} is a {npc.appearances["age"]} year old {npc.appearances["sex"].lower()} {npc.get_option_value("race")} {f"{npc.subclass}," if npc.subclass is not None else ""} {npc.options["occupation"].value}.</div>'

	html += f'<div class="description-character-feature">{npc.pronoun} has {npc.appearances["hair color"][1].lower()} hair {npc.appearances["hair style"].lower()}, and {npc.appearances["eye color"][1].lower()} colored eyes.'
	html += f'<br><br>{npc.appearances["hair color"][1]}: <svg width="400px" height="20" style="fill:{npc.appearances["hair color"][0]};stroke-width: 2px;stroke: white;margin-bottom: -3px;"> <rect width="400px" height="20"></rect> </svg>'
	html += f'<br>{npc.appearances["eye color"][1]}: <svg width="400px" height="20" style="fill:{npc.appearances["eye color"][0]};stroke-width: 2px;stroke: white;margin-bottom: -3px;"> <rect width="400px" height="20"></rect> </svg>'
	html += '</div>'

	html += f'<div class="description-character-feature">{npc.pronoun} has {npc.appearance_details["skin_detail"]}, {npc.appearances["skin color"][1]} {npc.appearances["skin"]}.'
	html += f'<br><br>{npc.appearances["skin color"][1]}: <svg width="400px" height="20" style="fill:{npc.appearances["skin color"][0]};stroke-width: 2px;stroke: white;margin-bottom: -3px;"> <rect width="400px" height="20"></rect> </svg>'
	html += '</div>'

	html += f'<div class="description-character-feature">{npc.pronoun} stands at {npc.appearances["height"]}cm tall and weighs {npc.appearances["weight"]}kg ({npc.get_weight_bin()}).</div>'
	html += f'<div class="description-character-feature">{npc.pronoun} has {npc.appearance_details["face_shape"]} face.</div>'
	html += f'<div class="description-character-feature">Overall {npc.pronoun.lower()} is {npc.appearance_details["attractiveness"]}.</div>'
	html += f'<div class="description-character-feature">{npc.pronoun} also {npc.appearance_details["extra"].replace("their", {"She":"her", "He":"his"}[npc.pronoun])}</div>'
	html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'


	for feature in npc.features.keys():
		if 'Description' in feature:
			html += f'<div class="description-character-feature">{feature}. {npc.features[feature].get_sub_feature("description").replace("BREAK", "<br>")}</div>'
	

	html += '</div>'



	html += '<div class="text-box-header" id="Personality Traits">Personality Traits</div>'

	# !! WORSHIP 
	# <div class="description-character-feature">[WORSHIP ((None, god, claim), p=[0.5, 0.35, 0.15]): {pronoun} {worship_style} worships {god_name}, {god_desc}. 
	# ({god_alignment})]<br>
	# He doesn't worship any god. || 
	# She quietly worships Zorquan, God of the essence of dragons. (all alignments) ||
	# She proudly claims to worship the demon prince Orcus, but secretly worships Cyric, God of murder, lies, intrigue, strife, deception, illusion. (Chaotic Evil)</div>

	num_gods = len(list(filter(lambda x: 'god_name' in x, npc.worship.keys())))

	if num_gods == 0:
		html += f'<div class="description-character-feature">{npc.pronoun} doesn\'t worship any god.</div>'
	elif num_gods == 1:
		html += f'<div class="description-character-feature">{npc.pronoun} {npc.appearance_details["worship_style"]} worships <a href="https://www.google.com/search?q=dnd+{npc.worship["god_name0"]}" target="_blank" rel="noopener noreferrer">{npc.worship["god_name0"]}</a>, {npc.worship["description0"]} ({npc.worship["alignment0"]}).<br>'
		html += f'{npc.worship["god_name0"]} has the domains {npc.worship["domains0"]}, and has the symbol of a {npc.worship["symbol0"]}.'
		html += '</div>'
	else:
		html += f'<div class="description-character-feature">{npc.pronoun} {npc.appearance_details["worship_style"]} claims worships <a href="https://www.google.com/search?q=dnd+{npc.worship["god_name0"]}" target="_blank" rel="noopener noreferrer">{npc.worship["god_name0"]}</a>, but secretly '
		html += f'worships <a href="https://www.google.com/search?q=dnd+{npc.worship["god_name1"]}" target="_blank" rel="noopener noreferrer">{npc.worship["god_name1"]}</a>, {npc.worship["description1"]} ({npc.worship["alignment1"]}).<br>'
		html += f'{npc.worship["god_name1"]} has the domains {npc.worship["domains1"]}, and has the symbol of a {npc.worship["symbol1"]}.'
		html += '</div>'
	html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'

	for trait in npc.traits:
		html += f'<div class="description-character-feature">{trait}: {npc.traits[trait]}</div>'
	if len(npc.traits.keys()) > 0:
		html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'

	for pet in npc.pets:
		html += f'<div class="description-character-feature">Pet: <a href="#{npc.pets[pet]["name"]}">{npc.pets[pet]["name"]}</a> is a {pet}, size of {npc.pets[pet]["size"]}, and CR of {npc.pets[pet]["cr"].split(" (")[0]}</div>'



	html += '</div>' #text-box

	return html


def text_boxes_features_feats(npc):
	html = ""

	html += '<div class="text-box">'



	html += '<div class="text-box-header" id="Features">Features</div>'

	features = {k:npc.features[k] for k in list(filter(lambda x: 'Description' not in x, list(npc.features.keys())))}

	for feature_str in features:
		feature = features[feature_str]

		
		html += '<div class="feat_container">'

		html += f'<div class="feat_header">{feature_str}</div>'
		html += f'<div class="description-character-feature">{feature.get_sub_feature("description").replace("BREAK", "<br>")}</div>'

		html += '</div>'

		features_keys = list(features.keys())
		next_feature = features_keys[min(features_keys.index(feature_str)+1, len(features_keys)-1)].split(':')[0]
		if next_feature != feature_str.split(':')[0]:
			html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'



	if len(npc.feats.keys()) > 0:
		html += '<div class="text-box-header" id="Feats">Feats</div>'
		for feat_str in npc.feats:
			feat = npc.feats[feat_str]

			html += '<div class="feat_container">'

			html += f'<div class="feat_header">{feat_str}</div>'
			html += f'<div class="description-character-feature">{feat.get_description().replace("BREAK", "<br>")}</div>'

			html += '</div>'


	html += '</div>'


	return html

def text_boxes_actions(npc):
	html = ""
	html += '<div class="text-box">'


	html += '<div class="text-box-header" id="Actions">Actions</div>'


	# ACTIONS
	html += '<div class="list">'
	html += f'<div class="list-heading">Actions | Attacks per Action: {npc.get_attacks_per_action()}</div>'

	html += '<div class="list-content">'


	html += '<div class="list-basic"><span style="font-weight: bold;">Actions in Combat<br></span><span>Attack, Cast a Spell, Dash, Disengage, Dodge, Grapple, Help, Hide, Improvise, Ready, Search, Shove, Use an Object</span></div>'

	html += '<div class="list-snippet"><span style="font-weight: bold;">Unarmed Strike<br></span><span>You can punch, kick, head-butt, or use a similar forceful blow and deal bludgeoning damage equal to 1 + $!STRENGTH$</span></div>'
	
	if npc.weapon["name"] != 'Unarmed':
		dmg = npc.weapon['damage'].split(';')
		wep_th = npc.get_weapon_to_hit()
		wep_dmg = npc.get_weapon_damage()
		html += f'<div class="list-snippet"><span style="font-weight: bold;">{npc.weapon["name"]}<br></span>{f"+{wep_th}" if wep_th >= 0 else wep_th} to hit, {dmg[0]} {f"+ {wep_dmg}" if wep_dmg >= 0 else wep_dmg} {dmg[1]} damage.</div>'
	
	html += f'<div class="list-snippet"><span style="font-weight: bold;">{npc.armor["name"]}<br></span>'
	if npc.armor['stealth_mod'] != '0':
		html += f'Disadvantage on Stealth checks due to this armor.'
	html += '</div>'

	for action in npc.actions['action']:
		html += f'<div class="list-snippet"><span style="font-weight: bold;">{action.f_id}<br></span><span>{action.get_sub_feature("description").replace("BREAK", "<br>")}</span></div>'



	html += '</div>' # list-content

	html += '</div>' # list
	html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'


	# BONUS ACTIONS
	html += '<div class="list">'
	html += f'<div class="list-heading">Bonus Actions</div>'

	html += '<div class="list-content">'


	html += '<div class="list-basic"><span style="font-weight: bold;">Actions in Combat<br></span>'
	html += '<abbr title="When you take the Attack action and attack with a light melee weapon that you\'re holding in one hand, you can use a bonus action to attack with a different light melee weapon that you\'re holding in the other hand. You don\'t add your ability modifier to the damage of the bonus attack, unless that modifier is negative. If either weapon has the thrown property, you can throw the weapon, instead of making a melee attack with it.">Two-Weapon Fighting</abbr>'
	html += '</div>'

	for bonus_action in npc.actions['bonus']:
		html += f'<div class="list-snippet"><span style="font-weight: bold;">{bonus_action.f_id}<br></span><span>{bonus_action.get_sub_feature("description").replace("BREAK", "<br>")}</span></div>'


	html += '</div>' # list-content

	html += '</div>' # list
	html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'



	# REACTIONS
	html += '<div class="list">'
	html += f'<div class="list-heading">Reactions</div>'

	html += '<div class="list-content">'


	html += '<div class="list-basic"><span style="font-weight: bold;">Actions in Combat<br></span><span>Oppertunity Attack</span></div>'

	for reaction in npc.actions['reaction']:
		html += f'<div class="list-snippet"><span style="font-weight: bold;">{reaction.f_id}<br></span><span>{reaction.get_sub_feature("description").replace("BREAK", "<br>")}</span></div>'


	html += '</div>' # list-content

	html += '</div>' # list
	html += '<svg height="10" width="100%" class="description-character-feature-break"> <polyline points="0,5 310,0 620,5 310,10"> </polyline></svg>'



	# OTHER
	html += '<div class="list">'
	html += f'<div class="list-heading">Other</div>'

	html += '<div class="list-content">'


	html += '<div class="list-basic"><span style="font-weight: bold;">Actions in Combat<br></span><span>Interact with an Object</span></div>'

	for other in npc.actions['other']:
		html += f'<div class="list-snippet"><span style="font-weight: bold;">{other.f_id}<br></span><span>{other.get_sub_feature("description").replace("BREAK", "<br>")}</span></div>'


	html += '</div>' # list-content

	html += '</div>' # list





	html += '</div>' # text-box
	return html



def text_boxes_spellcasting(npc):
	html = ""
	html += '<div class="text-box">'

	html += '<div class="text-box-header" id="Spellcasting">Spellcasting</div>'
	html += '<div class="spell-list-header">'

	spell_mod = npc.abilities[npc.spellcasting.ability].get_modifier()
	html += f'<div class="spell-list-header-item"><span style="font-family: Roboto;">{f"+{spell_mod}" if spell_mod >= 0 else spell_mod}</span><br>Modifier ({npc.spellcasting.ability[:3]})</div>'
	spell_atk = spell_mod + npc.get_proficiency_bonus() + npc.bonuses['spell_attack']
	html += f'<div class="spell-list-header-item" style="border-width: 0;"><span style="font-family: Roboto;">{f"+{spell_atk}" if spell_atk >= 0 else spell_atk}</span><br>Spell Attack</div>'
	spell_save = 8 + npc.get_proficiency_bonus() + npc.abilities[npc.spellcasting.ability].get_modifier()
	html += f'<div class="spell-list-header-item"><span style="font-family: Roboto;">{spell_save}</span><br>Save DC</div>'

	html += '</div>' # spell-list-header



	html += '<div class="spell-tables">'


	html += '<div class="spell-header">Spell Tables</div>'

	for group in npc.spellcasting.spells:
		group_spells = npc.spellcasting.spells[group] 
		if len(group_spells) > 0:
			html += '<div class="spell-group">'
			html += f'<div class="spell-group_header">{group}</div>'

			html += '<table class="spell-tables">'
			html += '<tr class="attack"> <th class="attack" style="width: 30%;">Name</th> <th class="attack" style="width: 25%;">Time</th> <th class="attack" style="width: 20%;" >Range</th> <th class="attack">Hit/DC</th> <th class="attack" style="width: 25%;">Components</th> </tr> '

			for spell in group_spells:
				spell_features = npc.spellcasting.get_features(spell)

				html += '<tr class="attack">'


				html += f'<td class="attack"><a href="#{spell}">{spell}</a></td>'
				html += f'<td class="attack">{spell_features["casting_time"]}</td>'
				html += f'<td class="attack">{spell_features["range"].split(" (")[0]}</td>'

				st_text = spell_features['description'].split('saving throw')[0].split(' ')[-2][:3].upper()
				hit_dc_bool = st_text in [a[:3] for a in npc.abilities.keys()]
				html += f'<td class="attack">{f"+{spell_atk}" if spell_atk >= 0 else spell_atk if not hit_dc_bool else f"{spell_save} {st_text}"}</td>'

				html += f'<td class="attack">{spell_features["components"].split(" (")[0]}</td>'
				

				html += '</tr>'


			html += '</table>'

			html += '</div>' #spell-group


	html += '</div>' # spell-tables







	html += '<div class="spell-descriptions">'
	html += '<div class="spell-header">Spell Descriptions</div>'

	for group in npc.spellcasting.spells:
		group_spells = npc.spellcasting.spells[group] 
		if len(group_spells) > 0:
			html += '<div class="spell-group">'
			html += f'<div class="spell-group_header">{group}</div>'


			for spell in group_spells:
				spell_features = npc.spellcasting.get_features(spell)

				html += '<div class="spell-descriptions-spell">'



				html += f'<div class="spell-descriptions-spell-header" id="{spell}">{spell}</div>'
				

				html += f'<div class="spell-descriptions-spell-content">'

				html += f'<div style="font-style: italic;margin-bottom: 10px;">{spell_features["school"]} {spell_features["level"]}</div>'
				html += f'<div><span style="font-weight: bold;">Casting Time: </span>{spell_features["casting_time"]}</div>'
				html += f'<div><span style="font-weight: bold;">Range: </span>{spell_features["range"]}</div>'
				html += f'<div><span style="font-weight: bold;">Components: </span>{spell_features["components"]}</div>'
				html += f'<div style="margin-bottom: 10px;"><span style="font-weight: bold;">Duration: </span>{spell_features["duration"]}</div>'
				html += f'<div style="margin-bottom: 10px">{spell_features["description"]}</div>'
				html += f'<div>{spell_features["higher_levels"]}</div>'

				html += f'</div>' #spell-descriptions-spell-content



				html += '</div>' #spell-descriptions-spell


			html += '</div>' #spell-group

	html += '</div>' #spell-descriptions
 







	html += '</div>' # text-box
	return html


def text_boxes_page(npc):
	html = ""

	html += '<div class="text-boxes-container">'


	html += text_boxes_description_traits(npc)

	html += text_boxes_features_feats(npc)

	html += text_boxes_actions(npc)

	html += text_boxes_spellcasting(npc)


	html += '</div>' #text-boxes-container

	return html









def pets_pet_statblock(npc, pet_str):
	pet = npc.pets[pet_str]

	html = ""
	html += f'<div class="pet_block_statblock" id="{pet["name"]}">'



	html += f'<div class="pet_block_statblock_name">{pet["name"]} ({pet_str})</div>'
	html += f'<div class="pet_block_statblock_summary">{pet["size"]} {pet["type"]}, typically {pet["alignment"].title()}</div>'
	html += f'<div class="pet_block_statblock_break"></div>'


	html += f'<div class="pet_block_statblock_feature"><span class="pet_block_statblock_feature_title">Armor Class </span>{pet["ac"]}</div>'

	hp = pet["hp"].split(" (")[1]
	rolled_hp = sum(npc.rng.choice(int(hp.split('d')[1].split(' +')[0]), size=int(hp.split('d')[0]))) + int(hp.split('d')[1].split(' + ')[1][:-1])
	html += f'<div class="pet_block_statblock_feature"><span class="pet_block_statblock_feature_title">Hit Points </span>{rolled_hp} ({pet["hp"].split(" (")[1]}</div>'

	html += f'<div class="pet_block_statblock_feature"><span class="pet_block_statblock_feature_title">Speed </span>{pet["speed"]}</div>'
	html += '<div class="pet_block_statblock_break"></div>'


	html += '<div class="pet_block_statblock_abilities">'
	for ability_str in npc.abilities:
		score = pet[ability_str.lower()]
		mod = (int(score)-10)//2
		html += f'<div class="pet_block_statblock_abilities_ability_container"><span class="pet_block_statblock_abilities_ability">{ability_str[:3]}<br></span>{score} ({mod})</div>'
	html += '</div>'
	html += '<div class="pet_block_statblock_break"></div>'


	for pet_key in list(pet.keys())[list(pet.keys()).index('charisma')+1:]:
		if pet_key != 'name':
			if len(pet[pet_key]) > 0:
				html += f'<div class="pet_block_statblock_feature"><span class="pet_block_statblock_feature_title">{pet_key.replace("_", " ").title()} </span>{pet[pet_key].replace("BREAK", "<br>")}</div>'

			if pet_key in ('cr', 'traits', 'reactions'):
				html += '<div class="pet_block_statblock_break"></div>'




	html += '</div>' #pet_block_statblock
	return html



def pets_page(npc):
	html = ""
	html += '<div class="pet_block_container">'


	for pet_str in npc.pets:
		html += pets_pet_statblock(npc, pet_str)



	html += '</div>'
	return html











