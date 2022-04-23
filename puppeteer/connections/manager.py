from threading import Thread, Lock
import socket

from .recruiter import ConnectionRecruiter

lock = Lock()

def locking(function):
	def inner(*args, **kwargs):
		with lock:
			function(*args, **kwargs)
	return inner

class ConnectionManager:
	def __init__(self, local_connection):
		self.connections = [local_connection]
		self.recruiter = ConnectionRecruiter(self._on_new_connection)
		self.recruiter.start()
		self._active_receiver_index = 0

	def cycle_active_receiver(self):
		self._active_receiver_index += 1
		self._active_receiver_index %= len(self.connections)
	
	@property
	def active_receiver(self):
		try:
			return self.connections[self._active_receiver_index]
		except IndexError:
			self.reset_active_receiver()
			return self.connections[self._active_receiver_index]
	
	def set_active_receiver(self, index):
		if index < len(self.connections):
			self._active_receiver_index = index
		else:
			self.reset_active_receiver()
	
	def reset_active_receiver(self):
		"""
		Resets active receiver to our local connection.
		"""
		# The 0'th connection should always be our own local Puppet.
		self._active_receiver_index = 0
	
	@locking
	def _on_new_connection(self, connection):
		print('new connection:', connection)
		self.connections.append(connection)
		self.recruiter.remaining_connections -= 1
	
	@locking
	def _on_connection_close(self, connection):
		position = self.connections.index(connection)
		self.recruiter.remaining_connections += 1
		if position == self._active_receiver_index:
			self.reset_active_receiver()
		elif position < self._active_receiver_index:
			# This connection being removed will cause larger indexes to shift downwards.
			# We must adust for that here.
			self._active_receiver_index -= 1
		self.connections.remove(connection)
		print('connection closed:', connection)
		if self.recruiter.remaining_connections == 1:
			self.recruiter.begin_recruitment()
	
	def send(self, packet):
		try:
			self.active_receiver.send(packet)
		except:
			self._on_connection_close(self.active_receiver)

	def send_udp(self, packet):
		self.active_receiver.send_udp(packet)

	def close(self):
		for connection in self.connections:
			connection.close()
		self.recruiter.close()

	def __len__(self):
		return len(self.connections)

	def __getitem__(self, index):
		return self.connections[index]