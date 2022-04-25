from queue import Queue

from keynames.interop import key_states, keycode_names, to_generic
from mimikey import shared_data
from mimikey.protocol import CommandType, decode, keyboard
from mimikey.puppeteer.puppeteer import Puppeteer

class FakeConnection:
	def __init__(self):
		self.queue = Queue()

	def send(self, packet):
		self.queue.put(decode(packet))
	
	def send_udp(self, packet):
		self.send(packet)
	
	def close(self):
		self.queue.put(None)

def test_main_hardware_loop():
	p = Puppeteer({'pause_toggle': keycode_names['f1'], 'cycle_receiver': keycode_names['f2']})
	assert len(p.connections) == 1
	fake_connection = FakeConnection()
	# p.connections.connections[0] = fake_connection
	p.connections._on_new_connection(fake_connection)
	a = keycode_names['a']
	down = key_states['key_down']
	up = key_states['key_up']
	fake_inputs = [
		(CommandType.misc, 'cycle_receiver'),
		(CommandType.keyboard, (a, down)),
		(CommandType.keyboard, (a, up)),
	]
	for i in fake_inputs:
		p.hardware_monitor.inputs.put(i)
	p.hardware_monitor.inputs.put((None, None))
	p.main()
	assert(fake_connection.queue.get(block=False) == keyboard.Command(keycode=a, state=down))
	assert(fake_connection.queue.get(block=False) == keyboard.Command(keycode=a, state=up))
	assert(fake_connection.queue.get(block=False) == None)

	print('Puppeteer test succeeded')

if __name__ == '__main__':
	test_main_hardware_loop()