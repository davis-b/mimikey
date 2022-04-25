# These are tests which are harder to automate, as they innately interact with hardware.
# Thus, we perform them as more of a manual sanity check.

from keynames.interop import mouse_states, mouse_buttons, key_states, keycode_names
from mimikey.puppet.processor import CommandProcessor
from mimikey import protocol

proc = CommandProcessor()

def test_keyboard():
	data = (keycode_names['f'], key_states['key_down'])
	cmd = protocol.keyboard.Command(*data)
	proc.keyboard(cmd)
	data = (keycode_names['f'], key_states['key_up'])
	cmd = protocol.keyboard.Command(*data)
	proc.keyboard(cmd)

def test_mouse_btn():
	data = (mouse_buttons['rmb'], mouse_states['mouse_down'])
	cmd = protocol.button.Command(*data)
	proc.mouse_button(cmd)

	data = (mouse_buttons['rmb'], mouse_states['mouse_up'])
	cmd = protocol.button.Command(*data)
	proc.mouse_button(cmd)

def test_mouse_move():
	start_pos = proc._mouse.pos
	cmd = protocol.mouse.Command(3, 5, True)
	proc.mouse_move(cmd)
	end_pos = proc._mouse.pos
	
	assert(start_pos[0] == end_pos[0] - 3)
	assert(start_pos[1] == end_pos[1] - 5)

if __name__ == '__main__':
	test_mouse_move()
	test_keyboard()
	test_mouse_btn()