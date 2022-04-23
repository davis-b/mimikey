from keywatch import KeyboardGrab, KeyGrab, MouseGrab
from keynames.interop import key_states, mouse_states
from mal import Cursor

class PassiveGrabber:
	"""
	A passive key grabber.
	Receives events for specific keys only,
	and does not prevent other programs from receiving those events.
	Allows us to implement global hotkeys.
	Designed to be used while the active grabber is stopped.
	"""
	def __init__(self):
		self._passive_keyboard = KeyGrab()
		self._passive_keyboard.start()

	def deinit(self):
		if self._passive_keyboard.living.is_set():
			self._passive_keyboard.stop()

	def grab_key(self, function, keycode, modifiers, call_after_release: bool):
		return self._passive_keyboard.bind(function, keycode, modifiers, call_after_release)
	
	def clear_grabs(self):
		self._passive_keyboard.unbind_all()


class ActiveGrabber:
	"""
	Actively grabs keyboard and mouse events.
	While active, other programs will not receive these events.
	Events will be passed to the given callback functions.
	"""
	def __init__(self, on_keypress, on_mouse_button, on_mouse_movement):
		self._on_keypress = on_keypress
		self._on_mouse_button = on_mouse_button
		self._on_mouse_movement = on_mouse_movement

		# Used to move the cursor to a reliable starting position before grabbing.
		self._cursor = Cursor()
		self._starting_cursor_pos = (0, 0)

		self._keyboard = None
		self._mouse = None
	
	def deinit(self):
		if self._keyboard != None and self._keyboard.living.is_set():
			self._keyboard.stop()
		if self._mouse != None and self._mouse.living.is_set():
			self._mouse.stop()
		self._cursor.move_to(*self._starting_cursor_pos)
	
	def _init_peripherals(self):
		""" Prepare the keyboard and mouse active-grabbers, but do not start them yet. """
		self._keyboard = KeyboardGrab()
		self._mouse = MouseGrab()
		self._mouse.set_movement_fn(self._mouse_movement_processor)

		# This is the function that will be ran on keyboard & mouse thread startup.
		self._keyboard.input_loop = self._keyboard_reader
		self._mouse.input_loop = self._mouse_reader
	
	def start(self):
		# We must ensure the cursor is not near any edge of the monitor,
		# and thus has room to move freely in all directions.
		# The simplest way to do this is by moving it to a known good spot (500, 500)
		# When stopping our grab, we want to move the cursor back to its starting location,
		# hence we record that now.
		self._starting_cursor_pos = self._cursor.pos
		self._cursor.move_to(500, 500)

		if self._keyboard is None or self._mouse is None:
			self._init_peripherals()

		self._keyboard.start()
		self._mouse.start()
	
	def stop(self):
		try:
			self._keyboard.stop()
			self._mouse.stop()
			self._cursor.move_to(*self._starting_cursor_pos)
		except AttributeError as e:
			print('Grabber has been stopped without ever being started.', e)
	
	def _keyboard_reader(self):
		for keycode, modifiers, keyup in self._keyboard._input():
			keystate = key_states['key_up'] if keyup else key_states['key_down']
			self._on_keypress(keycode, keystate)

	def _mouse_movement_processor(self, pos, delta):
		"""
		Receives mouse movement data from MouseGrab.
		Forwards the movement delta to our _on_mouse_movement function.
		"""
		self._on_mouse_movement(delta[0], delta[1])

	def _mouse_reader(self):
		for event in self._mouse._input():
			if len(event) == 3:
				button, modifiers, button_up = event
				button_state = mouse_states['mouse_up'] if button_up else mouse_states['mouse_down']
				self._on_mouse_button(button, button_state)
			else:
				raise EnvironmentError('Mouse input event yielded unexpected number of variables')

if __name__ == '__main__':
	from time import sleep
	from keynames import keycode_names
	def kb(*event):
		print('keypress', event)
	
	def mbtn(*event):
		print('mouse button', event)
			
	def mmove(*event):
		print('mouse movement', event)

	grabber = ActiveGrabber(kb, mbtn, mmove)
	passive = PassiveGrabber()
	grabber.start()
	print('grabbing for 3s')
	sleep(3)
	grabber.stop()
	print('grabber stopped')

	keyname = 'f5'
	keycode = keycode_names[keyname]
	passive.grab_key(lambda: kb(keyname), keycode, 0, True)
	print('Now grabbing single key [{}] for 5s'.format(keyname))
	sleep(5)
	passive._passive_keyboard.stop()