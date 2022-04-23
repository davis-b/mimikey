import struct
from functools import namedtuple

from keynames.interop import to_generic
from keynames.interop import from_generic2 as from_generic

# Keycode as an unsigned short, and key state as an unsigned char.
Package = struct.Struct('!H B')
Command = namedtuple('KeyCmd', ['keycode', 'state'])

def decode(data: bytes):
	generic_key, generic_state = Package.unpack(data)

	native_key = from_generic['keyboard'][generic_key]
	native_state = from_generic['key_states'][generic_state]
	return Command(native_key, native_state)

def encode(key, state):
	try:
		generic_key = to_generic['keyboard'][key]
	except KeyError:
		print('[Error] {} Could not convert {} (key id) to generic key'.format(__file__, key))
		return
	generic_state = to_generic['key_states'][state]
	return Package.pack(generic_key, generic_state)
