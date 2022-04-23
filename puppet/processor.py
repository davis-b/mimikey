import parser
from mal import keyboard, mouse
from keynames.interop import mouse_states

from mimikey import shared_data

class CommandProcessor():
	def __init__(self):
		self._keyboard = keyboard.Keyboard()
		self._mouse = mouse.Cursor()
	
	def keyboard(self, cmd):
		self._keyboard.press(cmd.keycode, cmd.state)
	
	def mouse_button(self, cmd):
		if cmd.state == mouse_states['mouse_down']:
			self._mouse.btn_down(cmd.button)
		else:
			self._mouse.btn_up(cmd.button)

	def mouse_move(self, cmd):
		''' Moves the mouse.
		Can move a relative distance, or
		to a specific location. '''
		if cmd.relative:
			self._mouse.move_by(cmd.x, cmd.y)
		else:
			self._mouse.move_to(cmd.x, cmd.y)