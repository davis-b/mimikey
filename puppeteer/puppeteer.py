from time import sleep
from threading import Thread, Lock

from keynames.interop import key_states

from mimikey import shared_data
from mimikey.protocol import CommandType, encode
from .hardware.monitor import Monitor as HardwareMonitor
from .connections.manager import ConnectionManager

class FakeLocalConnection:
	"""
	Allows Puppeteer and connection code to pretend this is just another client.
	Instead, we pause the Puppeteer when packets are sent to us.
	By pausing the Puppeteer, we remove the grab on our keyboard and mouse, allowing
	the rest of the operating system to receive those inputs.
	To the user, this should be identical to having a local Puppet client.
	"""
	def __init__(self, puppeteer):
		self.puppeteer = puppeteer
	
	def send(self, packet):
		self.puppeteer.pause()
	
	def send_udp(self, packet):
		self.send(packet)
	
	def close(self):
		pass

class Puppeteer:
	"""
	Take input from keyboard and mouse, send to whichever connection is currently set to receive.
	"""
	def __init__(self, keybinds: dict):
		self.keybinds = keybinds
		self.paused = True
		self.lock = Lock()
		self.hardware_monitor = HardwareMonitor(self.keybinds)
		self.local_puppet = FakeLocalConnection(self)
		self.connections = ConnectionManager(self.local_puppet)
	
	def main(self):
		try:
			print('starting hardware processing loop')
			# self.unpause()
			self._hardware_loop()
		except KeyboardInterrupt:
			pass
		except Exception as e:
			print('[Error]', type(e), str(e))
			if True:
				raise e
		finally:
			print(self.__class__.__name__, 'closing')
			self.hardware_monitor.deinit()
			self.connections.close()
	
	def _hardware_loop(self):
		while True:
			kind, data = self.hardware_monitor.inputs.get()
			if kind is None:
				print('hardware input kind is None exiting.')
				break

			if kind is CommandType.misc:
				if data == 'toggle_pause':
					self.toggle_pause()
				elif data == 'cycle_receiver':
					if len(self.connections) > 1:
						if self.paused:
							self.toggle_pause()
						else:
							self.connections.cycle_active_receiver()
							if isinstance(self.connections.active_receiver, FakeLocalConnection):
								self.pause()
						for i in range(len(self.connections)):
							if i == self.connections._active_receiver_index:
								print('[*]', end=' ')
							else:
								if i == 0:
									print('[h]', end=' ')
								else:
									print('[c]', end=' ')
						print()
				else:
					print('Unknown misc command with data "{}"'.format(data))
				continue
			elif kind is CommandType.keyboard:
				pass
			elif kind is CommandType.mouse_button:
				pass
			elif kind is CommandType.mouse_movement:
				# x, y, relative_movement
				data = (data[0], data[1], True)
			else:
				print('Unexpected hardware event kind "{}" with data "{}"'.format(kind, data))
				break

			# print('sending', kind, data)
			packet = encode(kind, *data)
			# TODO look into sending mouse movements as UDP.
			# Would require adding a timestamp or packet sequence id, so that clients can drop old packets.
			# if kind is CommandType.mouse_movement:
				# self.connections.send_udp(packet)
			self.connections.send(packet)
	
	def pause(self):
		'''
		When do we pause?
		When we cycle recipient to ourselves. -> main thread
		When we lose our last network connection. -> network thread
		Can check to see if we have a receiver before sending, or return an error if sending without receiver.
		That puts the pause call into the main thread execution.
		Therefore, a lock is not needed.
		Callbacks from the network code are not needed either.
		'''
		if not self.paused:
			self.paused = True
			self.hardware_monitor.ungrab_peripherals()
			self.connections.reset_active_receiver()
	
	def unpause(self):
		# self.connections will always contain at least one connection (our own native one)
		# Only unpause when there is another connection to receive input, otherwise we'll 
		# only be locking ourselves out of input locally.
		if self.paused and len(self.connections) > 1:
			self.paused = False
			self.hardware_monitor.grab_peripherals()
			self.connections.cycle_active_receiver()
		elif len(self.connections) <= 1:
			print('Could not unpause as we do not have any active nonlocal connections')
	
	def toggle_pause(self):
		print('toggling pause', 'off' if self.paused else 'on')
		if self.paused:
			self.unpause()
		else:
			self.pause()