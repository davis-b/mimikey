import socket

from mimikey.puppet import connections as c
from mimikey.puppeteer import connections as con

def setup_udp(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	for _ in range(10):
		try:
			sock.bind(('', port))
		except:
			port += 1
		else:
			return sock, port

def setup_server():
	return 0

def test_our_ip():
	# The program should still work despite this failing.
	# Binding to '0' should simply bind us to all IPv4 addresses.
	ip = c.our_ip()
	assert(ip != '0.0.0.0')

def test_broadcast():
	port = 9452
	message = 'a'.encode('utf-8')
	server, server_port = setup_udp(port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	c._broadcast(sock, message, server_port)
	received = server.recvfrom(1024)
	assert(received[0] == message)

# def test_integration():
# 	server = setup_server()
# 	c.Connection()

if __name__ == '__main__':
	test_broadcast()
	test_our_ip()