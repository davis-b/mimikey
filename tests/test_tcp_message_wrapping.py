from mimikey.protocol import tcp

def test_prefix():
	message = 'abc'
	result = tcp._prefix(message)
	assert(len(result) == 1)
	assert(tcp.header.unpack(result)[0] == 3)

def test_wrap_unwrap():
	separator = tcp.MessageSeparator()
	message = 'abc'.encode('utf-8')
	wrapped = tcp.wrap(message)
	unwrapped = separator.unwrap(wrapped)[0]
	assert(unwrapped == message)

	# Making sure repeated calls do not affect each other.
	message = 'zyxwvuts'.encode('utf-8')
	wrapped = tcp.wrap(message)
	unwrapped = separator.unwrap(wrapped)[0]
	assert(unwrapped == message)

def _encode(string):
	return string.encode('utf-8')
def test_partial_streamed_messages():
	# Testing not only splitting multiple messages from a single buffer,
	# but also the ability to handle partial messages.
	a = _encode('abc')
	b = _encode('defghijklmno')
	c = _encode('pqrstuv')
	d = _encode('qwertyuiop')
	expected = [a, b, c]

	separator = tcp.MessageSeparator()
	assert(separator._can_unwrap_next_header() == False)
	separator.buffer = tcp.wrap(a) + tcp.wrap(b) + tcp.wrap(c)
	assert(separator._can_unwrap_next_header() == True)
	assert(separator._can_unwrap_next_message() == False)

	result = separator.unwrap(tcp._prefix(d))
	assert(result == expected)

	assert(separator._can_unwrap_next_header() == False)
	assert(separator._can_unwrap_next_message() == False)
	assert(separator.current_message_len == len(d))

	separator.buffer = d
	assert(separator._can_unwrap_next_message() == True)
	separator.buffer = d[:-1]
	assert(separator._can_unwrap_next_message() == False)

	separator.buffer = d
	assert(separator.unwrap(d)[0] == d)


def test_streamed_messages():
	# TCP is a data streaming protocol, we are testing if we can reliably
	# split streams into distinct packets.
	a = _encode('abc')
	b = _encode('defghijklmno')
	c = _encode('pqrstuv')
	expected = [a, b, c]

	separator = tcp.MessageSeparator()
	separator.buffer = tcp.wrap(a) + tcp.wrap(b)
	result = separator.unwrap(tcp.wrap(c))
	assert(result == expected)
	assert(separator._can_unwrap_next_header() == False)
	assert(separator._can_unwrap_next_message() == False)
	assert(separator.current_message_len == 0)

if __name__ == '__main__':
	test_partial_streamed_messages()
	test_prefix()
	test_streamed_messages()
	test_wrap_unwrap()