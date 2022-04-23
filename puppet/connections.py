import socket
from threading import Thread, Event
from queue import Queue

from mimikey import shared_data
from mimikey.config import our_ip
from mimikey.protocol import tcp
	
class Connection:
	def __init__(self):
		self.queue = Queue()
		self._server_tcp_addr, self._server_udp_addr = find_server_tcp_addr()

		ip = our_ip()
		self.udp = UDP(self._server_udp_addr, ip)
		self.tcp = TCP(self._server_tcp_addr, ip)
	
	def is_open(self):
		return not (self.tcp.closed or self.udp.closed)
	
	def begin_read_to_queue(self):
		""" Stores messages in a threadsafe queue for later processing. """
		def _store_messages(connection, queue):
			for msg in connection.read():
				try:
					queue.put(msg)
				except BrokenPipeError:
					queue.put(None)

		Thread(target=_store_messages, args=(self.tcp, self.queue), daemon=True).start()
		Thread(target=_store_messages, args=(self.udp, self.queue), daemon=True).start()
	
	def close(self):
		self.tcp.socket.shutdown(socket.SHUT_RDWR)
		self.tcp.socket.close()
		self.udp.socket.close()

class Protocol:
	def __init__(self):
		self.socket = None

	def _bind(self, ip):
		# port = shared_data.server_port_tcp if isinstance(self, TCP) else shared_data.server_port_udp
		port = 0
		print('binding {}:{}'.format(ip, port))
		self.socket.bind((ip, port))

	@property
	def closed(self):
		return self.socket._closed

class UDP(Protocol):
	def __init__(self, server_addr, bind_to_ip):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._read_size = 1024

		self.server_ip = server_addr[0]
		self._bind(bind_to_ip)

	def read(self):
		while not self.closed:
			msg, addr = self.socket.recvfrom(self._read_size)
			if self.server_ip and self.server_ip != addr[0]:
				print('received msg from unexpected address', addr)
				continue
			yield msg

class TCP(Protocol):
	def __init__(self, server_addr, bind_to_ip):
		self._read_size = 1024
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.message_splitter = tcp.MessageSeparator()

		self._bind(bind_to_ip)
		self.socket.connect(server_addr)

	def read(self):
		while not self.closed:
			data = self.socket.recv(self._read_size)
			for msg in self.message_splitter.unwrap(data):
				yield msg

def find_server_tcp_addr():
	connected = Event()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((our_ip(), 0))
	_broadcast(sock, shared_data.greeting_message, shared_data.server_port_udp)
	Thread(target=_keep_broadcasting, args=(connected, sock)).start()
	msg, addr = sock.recvfrom(1024)
	# tcp_port = int().from_bytes(msg, shared_data.byte_order)
	tcp_port = shared_data.GreetingReciprocation.unpack(msg)[0]
	server_ip, udp_port = addr
	connected.set()
	return ((server_ip, tcp_port), (server_ip, udp_port))

# def connect(ip, port, max_port_changes=1):
	# for port in range(port, port + shared_data.max_port_changes):
		# try:
			# connection = socket.create_connection((ip, port))
			# return connection, port
		# except ConnectionRefusedError:
			# pass
	# return None, None

def _keep_broadcasting(connected, sock):
	port = shared_data.server_port_udp
	while not connected.is_set():
		print('Broadcasting hello ping to {}+{}'.format(port, shared_data.max_port_changes))
		for i in range(shared_data.max_port_changes):
			if not connected.is_set():
				_broadcast(sock, shared_data.greeting_message, port + i)
		connected.wait(timeout=5)

def _broadcast(sock, msg, port):
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto(msg, ('<broadcast>', port))
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)

if __name__ == '__main__':
	print(our_ip())
	server = Connection()
	print(server)