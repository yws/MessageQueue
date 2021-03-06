import asyncore
import socket
import time
import logging
import sys

class Server(asyncore.dispatcher):
	max_clients     = 256
	disconnect_idle = 3600
	backlog         = 5
	quant           = 1
	
	def __init__(self, port, host = "0.0.0.0", max_clients=256, backlog=5, reuse_addr = True, disconnect_idle=3600, quant = 1):
		"""
		Constructs new Server using asyncore.dispatcher
		
		@param port		: port for listen
		@param host		: interface for listen
		@param max_clients	: server max clients
		@param backlog		: backlog for the socket
		@param disconnect_idle	: disconnect if idle for so many seconds
		@param quant		: timeout for asyncore.loop
		"""
		asyncore.dispatcher.__init__(self)

		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

		if reuse_addr:
			self.set_reuse_addr()

		self.bind( (host, port) )
		
		self.listen(backlog)
		
		self.clients      = []
		self.max_clients  = max_clients
		self.backlog      = backlog
				
		if disconnect_idle >= 0:
			self.disconnect_idle = disconnect_idle
			
		logging.info("Server started at %s:%d, maxclients %d" % (host, port, max_clients) )

	def handle_accept(self):
		# we accept anyway, else asyncore will keep handle_accept()
		socket, address = self.accept()
				
		if len(self.clients) >= self.max_clients:
			# too many connections,
			# and we close the socket here...
			socket.close()
			
			logging.info("Too many connections, reject client %s" % (address,) )
			
			return
		
		handler = self.spawn_handler(socket, address)
				
		self.clients.append(handler)
		
		logging.info("Accept client %s. Total %d of %d clients connected" % (address, len(self.clients), self.max_clients) )

	
	def spawn_handler(self, socket, address):
		#  
		#  This method must be overriden and 
		#  must return new ServerHandler object
		#  
		#  @param socket : socket from asyncore
		#  @param address : address from asyncore
		#
				
		logging.critical("Abstract method call!!!")
		
		#return ServerHandler(socket, address, Processor())

	def gc_handler(self):
		if not self.disconnect_idle:
			return
		
		if len(self.clients) is 0:
			return

		t = time.time()
		
		clients = []
				
		for client in self.clients:
			if self.disconnect_idle and t - client.lastping > self.disconnect_idle:
				logging.info("Manually disconnect client %s due to inactivity of %s seconds." % (client.address, self.disconnect_idle) )
				client.close()
			elif client.connected is False:
				print("Disconnect client %s." % (client.address,) )
			else:
				clients.append(client)
		
		self.clients = clients

	def serve_forever(self):
		logging.info("Start serving requests")
		while True:
			asyncore.loop(timeout=1, count=1)
			
			self.gc_handler()



