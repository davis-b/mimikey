server_port_tcp = 7430
server_port_udp = 7440
# client_port_udp = 7450
max_port_changes = 5
# byte_order = 'big'
assert((server_port_udp - server_port_tcp) > max_port_changes)

import struct
_greeting_message = 'mimikey 01.00'
Greeting = struct.Struct('! {}s'.format(len(_greeting_message)))
greeting_message = Greeting.pack(_greeting_message.encode('utf-8'))
assert(Greeting.unpack(greeting_message)[0].decode('utf-8') == _greeting_message)

# Unsigned short, representing the server's TCP port.
GreetingReciprocation = struct.Struct('! H')