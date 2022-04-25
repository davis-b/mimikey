import struct

from keynames import interop as keys
from mimikey import protocol as packaging

def test_button():
	button = packaging.button

	for button_state in keys.mouse_states.values():
		for button_id in keys.mouse_buttons.values():
			expected_result = button.Command(button_id, button_state)
			inner = button.encode(*expected_result)
			result = button.decode(inner)
			assert(result == expected_result)

def test_keyboard():
	kb = packaging.keyboard

	for state in keys.key_states.values():
		for key in keys.keycode_names.values():
			expected_result = kb.Command(key, state)
			inner = kb.encode(*expected_result)
			result = kb.decode(inner)
			assert(result == expected_result)

def test_mouse_movement():	
	mouse = packaging.mouse

	for relative in (True, False):
		for x in range(0, 3000, 500):
			for y in range(0, 2000, 400):
				expected_result = mouse.Command(x, y, relative)
				inner = mouse.encode(*expected_result)
				result = mouse.decode(inner)
				assert(result == expected_result)

def test_outer_packaging():
	expected_result = packaging.mouse.Command(100, 200, True)
	inner = packaging.mouse.encode(*expected_result)
	outer = packaging.OuterCommand.pack(packaging.CommandType.mouse_movement.value)
	packet = outer + inner
	result = packaging.decode(packet)
	assert(result == expected_result)

	outer = packaging.OuterCommand.pack(packaging.CommandType.mouse_button.value)
	packet = outer + inner
	try:
		result = packaging.decode(packet)
	except struct.error as e:
		pass # success
	else:
		raise ValueError('Expected a decoding error')

def test_encoding():
	data = (123, 3000, False)
	expected = packaging.mouse.Command(*data)
	packet = packaging.encode(packaging.CommandType.mouse_movement, *data)
	result = packaging.decode(packet)
	assert(result == expected)

	try:
		packet = packaging.encode(packaging.CommandType.keyboard, *data)
	except:
		pass
	else:
		raise ValueError('Expected an encoding error')

def test_empty_packet():
	empty = bytearray()
	assert(len(empty) == 0)
	result = packaging.decode(empty)
	assert(result is None)

if __name__ == '__main__':
	test_button()
	test_empty_packet()
	test_encoding()
	test_keyboard()
	test_mouse_movement()
	test_outer_packaging()