from threading import Thread
from time import sleep
from struct import error as struct_error
import socket

from mimikey import shared_data
from mimikey import config
from .connection import Connection

class ConnectionRecruiter():
	"""
	Recruiter expects clients to first send a broadcast.
	It will respond using UDP, sending our TCP port as a message.
	Client then connects to the TCP port.
	"""
	def __init__(self, recruitment_callback):
		self.recruitment_callback = recruitment_callback
		self.remaining_connections = config.max_connections
		self.port_tcp = shared_data.server_port_tcp
		self.port_udp = shared_data.server_port_udp
		self.buffersize = 1024
		self.ip = ''
		self.open_socket_tcp = None
		self.open_socket_udp = None

		# Tracks the udp port each ip initially contacted us from.
		# Assumes each client has a unique ip.
		self.ip_udp_ports = {}

	def start(self):
		# self.ip = config.our_ip() # Client unable to find this host when using our ip like so
		self.create_sockets()
		if self.open_socket_tcp is None or self.open_socket_udp is None:
			quit()
		self.begin_recruitment()

	def create_sockets(self):
		self.open_socket_tcp = self._create_listening_socket()
		self.open_socket_udp = self._create_udp_socket()

	def begin_recruitment(self):
		Thread(target=self.recruit, args=(), daemon=True).start()
		Thread(target=self.wait_for_broadcast, args=(), daemon=True).start()

	def _create_listening_socket(self, backlog=1):
		open_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		open_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		for self.port_tcp in range(self.port_tcp, self.port_tcp + shared_data.max_port_changes):
			try:
				open_socket.bind((self.ip, self.port_tcp))
				print('TCP socket created at {}:{}'.format(self.ip, self.port_tcp))
				open_socket.listen(backlog)
				return open_socket
			except socket.error as error:
				print('TCP bind failure in {}. {}'.format(__file__, error))

	def _create_udp_socket(self, backlog=1):
		open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		for self.port_udp in range(self.port_udp, self.port_udp + shared_data.max_port_changes):
			try:
				open_socket.bind((self.ip, self.port_udp))
				print('UDP socket created at {}:{}'.format(self.ip, self.port_udp))
				return open_socket
			except socket.error as error:
				print('UDP bind failure in {}. {}'.format(__file__, error))

	def recruit(self):
		while not self.open_socket_tcp._closed and self.remaining_connections > 0:
			try:
				connection, address = self.open_socket_tcp.accept()
			except OSError as e:
				print('OSError prevented tcp connection acception.', e)
				break
			try:
				udp_port = self.ip_udp_ports.pop(address[0])
			except KeyError:
				print('Could not accept {} as a TCP connection because it has not initiated contact with our UDP socket {}'.format(
					address, (self.open_socket_udp, self.port_udp)
				))
				continue
			conn = Connection(
				connection,
				self.open_socket_udp,
				udp_port,
				address[0],
			)
			self.recruitment_callback(conn)

	def wait_for_broadcast(self):
		our_info = shared_data.GreetingReciprocation.pack(self.port_tcp)
		while not self.open_socket_tcp._closed and self.remaining_connections > 0:
			print('waiting for udp broadcast')
			msg, addr = self.open_socket_udp.recvfrom(self.buffersize)
			try:
				unpacked_msg = shared_data.Greeting.unpack(msg)[0].decode('utf-8')
			except struct_error:
				print('received invalid broadcast', addr, msg)
				continue
			try:
				check, version = unpacked_msg.split()
			except ValueError:
				print('received invalid broadcast', addr, msg)
				continue

			if check == shared_data._greeting_message.split()[0]:
				print('Received broadcast from ({}) | {} version {}'.format(addr, check, version))
				self.open_socket_udp.sendto(our_info, addr)
				self.ip_udp_ports[addr[0]] = addr[1]
			else:
				print('Received invalid broadcast from ({}) | {} version {}'.format(addr, check, version))

	def close(self):
		try:
			self.open_socket_tcp.shutdown(socket.SHUT_RDWR)
		except OSError:
			pass
		self.open_socket_tcp.close()
		self.open_socket_udp.close()