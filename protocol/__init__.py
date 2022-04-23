# Handles converting commands to and from networking.
# from functools import namedtuple
import struct
from enum import Enum, auto, unique

from . import button, mouse, keyboard, tcp

@unique
class CommandType(Enum):
	keyboard = 1
	mouse_button = 2
	mouse_movement = 3
	misc = 4

command_types = [
	'keyboard',
	'mouse_button',
	'mouse_movement',
	'misc',
]

# Command type as an unsigned char,
OuterCommand = struct.Struct('!B')
# OuterCommand = namedtuple('OuterCommand', ['type', 'data'])

def decode(data: bytes):
	# 'Unpack' the byte to get our command type
	if len(data) == 0:
		return None
	type_ = data[0]
	message = data[1:]

	# kind = command_types[type_] 
	kind = CommandType(type_).name

	if kind == 'keyboard':
		return keyboard.decode(message)
	elif kind == 'mouse_button':
		return button.decode(message)
	elif kind == 'mouse_movement':
		return mouse.decode(message)
	elif kind == 'misc':
		print('todo: implement misc messages')
		quit()
	else:
		print('Error, unexpected decode request. Exiting early')
		print(kind, data)
		quit()

def encode(kind: CommandType, *data) -> bytes:
	if kind.name == 'keyboard':
		encoded_data = keyboard.encode(*data)
	elif kind.name == 'mouse_button':
		encoded_data = button.encode(*data)
	elif kind.name == 'mouse_movement':
		encoded_data = mouse.encode(*data)
	elif kind.name == 'misc':
		print('todo: implement misc messages')
		quit()
	else:
		print('Error, unexpected encode request. Exiting early')
		print(kind, data)
		quit()
	return OuterCommand.pack(kind.value) + encoded_data