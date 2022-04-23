import socket

# How many clients can connect to our server?
max_connections = 5

def our_ip():
	""" Returns the caller's ip within their local subnet. """
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.connect(('10.255.255.255', 1))
		ip = sock.getsockname()[0]
		sock.close()
	except:
		# ip = '127.0.0.1'
		ip = '0.0.0.0'
	return ip
