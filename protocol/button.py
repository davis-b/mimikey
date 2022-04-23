import struct
from functools import namedtuple

from keynames.interop import to_generic
from keynames.interop import from_generic2 as from_generic

# Button ID as an unsigned short, and button state as an unsigned char.
Package = struct.Struct('!H B')
Command = namedtuple('BtnCmd', ['button', 'state'])

def decode(data: bytes):
	generic_button, generic_state = Package.unpack(data)

	native_button = from_generic['mouse'][generic_button]
	native_state = from_generic['mouse_states'][generic_state]
	return Command(native_button, native_state)

def encode(button, state):
	try:
		generic_button = to_generic['mouse'][button]
	except KeyError:
		print('[Error] {} Could not convert {} (button id) to generic button'.format(__file__, button))
		return
	generic_state = to_generic['mouse_states'][state]
	return Package.pack(generic_button, generic_state)
