"""
Receives inputs from a puppeteer and treats them as though
they were placed from hardware directly on this computer.
"""

from keynames.keyname_list import mouse_buttons
from keynames.interop import generic, from_generic

from mimikey import shared_data, protocol
from mimikey.puppet import connections
from mimikey.puppet.processor import CommandProcessor

def next_command(server):
	while server.is_open():
		msg = server.queue.get()
		cmd = protocol.decode(msg)
		if cmd:
			yield cmd
		else:
			server.close()
			break

def main():
	server = connections.Connection()
	server.begin_read_to_queue()
	processor = CommandProcessor()
	for command in next_command(server):
		if isinstance(command, protocol.keyboard.Command):
			processor.keyboard(command)
		elif isinstance(command, protocol.button.Command):
			processor.mouse_button(command)
		elif isinstance(command, protocol.mouse.Command):
			processor.mouse_move(command)

if __name__ == '__main__':
	main()