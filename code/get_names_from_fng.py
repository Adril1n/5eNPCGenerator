import pyautogui
import tkinter
import time

# root = tkinter.Tk()
# root.bind("<Button-1>", lambda x: print(pyautogui.position()))

# root.title('Test')
# root.geometry('2560x1600')

# root.mainloop()


range_ = int(input("Number of rounds here: "))
try:
	time.sleep(2)

	pyautogui.moveTo(475, 840)
	pyautogui.click()

	pyautogui.moveTo(500, 500)

	for _ in range(33):
		pyautogui.press('down')

	for a in range(range_):
		pyautogui.moveTo(475, 840)
		pyautogui.click()

		pyautogui.moveTo(521, 557)
		pyautogui.click()

		pyautogui.moveTo(742, 520)
		pyautogui.dragTo(222, 234, button='left')
		pyautogui.hotkey('command', 'c')

		pyautogui.moveTo(800, 830)
		pyautogui.click()
		pyautogui.moveTo(500, 500)
		pyautogui.hotkey('command', 'v')

		pyautogui.press('enter')

except KeyboardInterrupt:
	quit()