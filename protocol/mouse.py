import struct
from functools import namedtuple

# x/y as signed shorts,
# and if x/y are relative a movement or an exact position as a bool.
Package = struct.Struct('!h h ?')
Command = namedtuple('MouseCmd', ['x', 'y', 'relative',])

def decode(data: bytes):
	return Command(*Package.unpack(data))

def encode(x, y, relative):
	return Package.pack(x, y, relative)