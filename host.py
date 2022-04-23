from sys import platform

supported_platforms = ['linux', 'win32']
if platform not in supported_platforms:
	raise NotImplementedError("{} Unsupported operating system".format(platform))

from keynames.interop import generic as generic_keycodes
from keynames.interop import from_generic as from_generic_keycodes

from puppeteer import Puppeteer

if __name__ == '__main__':
	keybinds = {
		'cycle_receiver': 'f11',
		'pause_toggle': 'f10',
	}
	print('keybinds:')
	for k, v in keybinds.items():
		print(k, v)
		keybinds[k] = from_generic_keycodes[generic_keycodes[v]]
	print()

	p = Puppeteer(keybinds)
	p.main()