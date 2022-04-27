import socket

from mimikey.protocol import tcp

class Connection():
	def __init__(self, tcp_connection: socket, udp_socket: socket, udp_port, remote_ip):
		self.tcp_connection = tcp_connection
		self.udp_socket = udp_socket
		self.udp_port = udp_port
		self.remote_ip = remote_ip

		# Disable Nagle's algorithm. For keyboard data, this choice seems appropriate.
		# We want packets to be sent out immediately.
		# There won't be an absurd quantity of them, so bandwith is unlikely to be an issue.
		self.tcp_connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

	def __repr__(self):
		return 'Connection ({}:{})'.format(self.remote_ip, self.udp_port)

	def send(self, packet):
		self.tcp_connection.sendall(tcp.wrap(packet))
	
	def send_udp(self, packet):
		self.udp_socket.sendto(packet, (self.remote_ip, self.udp_port))
	
	def close(self):
		self.tcp_connection.shutdown(socket.SHUT_RDWR)
		self.tcp_connection.close()
		# We specifically do not close our udp socket here
		# because it is shared between all Connections.