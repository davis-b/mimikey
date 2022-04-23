import struct

# Header is a single unsigned byte
# representing length (in bytes) of this message.
header = struct.Struct('! B')

def _prefix(message):
	return header.pack(len(message))

def wrap(message):
	return _prefix(message) + message

class MessageSeparator:
	"""
	Unwraping is a bit different than wrapping.
	This is due to TCP being a data streaming protocol.
	We are using it to transmit distinct messages.
	As such, we store partially delivered application layer messages
	until we can completely recombine them.
	"""
	def __init__(self):
		self.buffer = bytes()
		self.current_message_len = 0

	def unwrap(self, partial: bytes):
		"""
		Returns None if no full messages were unwrapped.
		Otherwise, returns a list of unwrapped messages.
		"""
		self.buffer = self.buffer + partial
		messages = []
		while True:
			if self._can_unwrap_next_message():
				messages.append(self._unwrap_next())
			if self._can_unwrap_next_header():
				self.current_message_len = self._unwrap_next_header()
			else:
				return messages

	def _can_unwrap_next_message(self):
		return self.current_message_len <= len(self.buffer) and self.current_message_len != 0
	
	def _unwrap_next(self):
		msg_bytes = self.buffer[:self.current_message_len]
		self.buffer = self.buffer[self.current_message_len:]
		self.current_message_len = 0
		return msg_bytes

	def _can_unwrap_next_header(self):
		return len(self.buffer) >= header.size and self.current_message_len == 0
	
	def _unwrap_next_header(self):
		header_bytes = self.buffer[:header.size]
		self.buffer = self.buffer[header.size:]
		return header.unpack(header_bytes)[0]