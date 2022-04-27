"""
Takes hardware input and sends it along
"""
from queue import Queue

from keynames.interop import key_states
from mimikey.protocol import CommandType

if __name__ == '__main__':
	from grabber import ActiveGrabber, PassiveGrabber
else:
	from .grabber import ActiveGrabber, PassiveGrabber

class Monitor:
	def __init__(self, keybinds):
		self._keybinds = keybinds
		self.inputs = Queue()
		self.grabbed = ActiveGrabber(self._keyboard, self._mouse_button, self._mouse_movement)
		self.global_hotkeys = PassiveGrabber()
		self._set_global_hotkeys()
		self._last_keypress = (None, None)

	def deinit(self):
		self.global_hotkeys.deinit()
		self.grabbed.deinit()

	def grab_peripherals(self):
		print(self.__class__.__name__, 'ungrabbing global hotkeys')
		self.global_hotkeys.clear_grabs()
		print(self.__class__.__name__, 'starting hardware grabs')
		self.grabbed.start()
	
	def ungrab_peripherals(self):
		print(self.__class__.__name__, 'stopping hardware grabs')
		self.grabbed.stop()
		print(self.__class__.__name__, 'successfully stopped hardware grabs')
		print(self.__class__.__name__, 'passively grabbing global hotkeys')
		self._set_global_hotkeys()

	def _keyboard(self, key, keystate):
		if key == self._keybinds['pause_toggle']:
			if keystate == key_states['key_up']:
				if self._last_keypress[0] == key and self._last_keypress[1] != keystate:
					self._push_pause_toggle()
		elif key == self._keybinds['cycle_receiver']:
			if keystate == key_states['key_up']:
				if self._last_keypress[0] == key and self._last_keypress[1] != keystate:
					self._push_cycle_receiver()
		else:
			self.inputs.put((CommandType.keyboard, (key, keystate)))
		self._last_keypress = (key, keystate)

	def _mouse_button(self, button, button_state):
		self.inputs.put((CommandType.mouse_button, (button, button_state)))
	
	def _mouse_movement(self, x, y):
		self.inputs.put((CommandType.mouse_movement, (x, y)))
	
	def _set_global_hotkeys(self):
		self.global_hotkeys.grab_key(self._push_pause_toggle, self._keybinds['pause_toggle'], 0, True)
		self.global_hotkeys.grab_key(self._push_cycle_receiver, self._keybinds['cycle_receiver'], 0, True)
	
	def _push_pause_toggle(self):
		self.inputs.put((CommandType.misc, ('toggle_pause')))
	
	def _push_cycle_receiver(self):
		self.inputs.put((CommandType.misc, ('cycle_receiver')))

if __name__ == '__main__':
	from time import sleep
	from keynames import keycode_names

	def print_sleep(seconds):
		for i in range(seconds):
			# print('.', end='', flush=True)
			print('\r' + '.' * (seconds - (i + 1)), end=' ' * seconds, flush=True)
			sleep(1)
		print()
	
	def read_queue(queue):
		while True:
			try:
				yield queue.get_nowait()
			except:
				return

	keybinds = {
		'cycle_receiver': keycode_names['a'],
		'pause_toggle': keycode_names['s'],
	}

	m = Monitor(keybinds)
	print('monitor created')
	print_sleep(1)
	for i in read_queue(m.inputs):
		print(i)
	m.grab_peripherals()
	print('monitor started')
	print_sleep(3)
	for i in read_queue(m.inputs):
		print(i)
	m.ungrab_peripherals()
	m.grab_peripherals()
	print('monitor stopped and started again')
	print_sleep(2)
	for i in read_queue(m.inputs):
		print(i)
	m.deinit()