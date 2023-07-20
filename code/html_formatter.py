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

	mod = npc.abilities[st_ab].get_modifier() + npc.get_proficiency_bonus()
	html += f'{st_ab[:3]} {f"+{mod}" if mod >= 0 else mod} '

	return html

def statblock_skills(npc, skill):
	html = ""

	mod = npc.get_skill(skill) + npc.get_proficiency_bonus()
	html += f'{skill} {f"+{mod}" if mod >= 0 else mod} '

	return html