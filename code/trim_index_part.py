import pyperclip

a = input('Here: ')

b = a.split(' ')

c = ""
for d in b:
	c += f"{d.strip()} "

pyperclip.copy(c)