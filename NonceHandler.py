"""
---------------------------------
Project: iBee
Date: 02-12-2017
Last updated: 13-12-2017
Libraries: time, calendar, random, sqlite3
Description: contains all functionality to generate a nonce and a list with all sensornode objects and their nonces
---------------------------------
"""

from random import randint
from  SensorNodeNonce import SensorNodeNonce
from datetime import datetime
import calendar
import sqlite3
import time

class NonceHandler:
	
	"""
	The constructor of the NonceHandler class.
	Args:
		db_name the name of the database the incoming data has to be stored in.

	"""
	def __init__(self, db_name):
		self.db_name = db_name
		self.list_sensor_nodes = []

	"""
		Function that rotates the value using a bitshift.
		Returns:
			a rotated value.
	"""
	def lrotate(self,a, n):
		return (a << n) | (a >> (16 - n))

	"""
		Function that returns a binary hash based of a key and a nonce value.
		Args:
			nonce contains random generated number between 255 and 65000.
		Returns:
			the generated binary hash.
	"""
	def myhash(self, node_id, nonce):
		MAGIC = 0xB819 ## 16 bits value: 47129
		START_VAL = 0x7F03 ## 16 bits value: 32515

		PSK = str(self.get_psk(node_id))
		w2 = list(PSK)
		
		## convert characters to ints.
		for i in range(len(w2)):
		   w2[i] = ord(w2[i])

		ret = START_VAL

		for i in range(len(w2)):
			w2[i] = MAGIC % w2[i]
			w2[i] = self.lrotate(w2[i], i)
			if (i & 2):
				w2[i] ^= nonce & 0xFF
			else:
				w2[i] ^= nonce >> 8
			w2[i] = self.lrotate(w2[i], 3)
			w2[i] = w2[i] & 0xff
			
		ret += w2[0]
		ret += w2[1]
		ret += w2[6]
		ret += w2[7]
		ret += w2[2] << 8
		ret += w2[3] << 8
		ret += w2[4] << 8
		ret += w2[5] << 8

		self.lrotate(ret, 4)
		ret &= 0xffff
		return ret           

	"""
		Function that returns a random number between 255 and 65000.
		Returns:
			a random number between 255 and 65000.
	"""
	def get_nonce_number (self):
		return randint(255, 65000)

	"""
		Function that generates for every sensor node a nonce and appends the node to a sensor node list.
		Args:
			node_id contains the node_id of the node
	"""
	def append_node(self, node_id):
		end_time = self.get_current_time() + 60
		nonce = self.get_nonce_number()
		binary_nonce = self.myhash(node_id, nonce)

		for node in self.list_sensor_nodes:
			if node_id == node.node_id:
				node.nonce = nonce
				node.binary_nonce = binary_nonce
				node.end_time = end_time
				return
		new_node = SensorNodeNonce(node_id, end_time, nonce, binary_nonce)
		self.list_sensor_nodes.append(new_node)

	"""
	Function that returns the nonce for a specific node
	Args:
		node_id contains the node_id of the node
	"""
	def get_nonce(self, node_id):
		for node in self.list_sensor_nodes:
			if node_id == node.node_id:
				return node.nonce
			
	"""
	Function that returns the binary nonce (authentication token) for a specific node
	Args:
		node_id contains the node_id of the node
	"""
	def get_binary_nonce(self, node_id):
		for node in self.list_sensor_nodes:
			if node_id == node.node_id:
				return node.binary_nonce
		
	"""
	Function that checks if a nonce for a specific node exists (and isn't outdated)
	Args:
		node_id contains the node_id of the node
	Returns:
		True if a valid nonce exists, false if not
	"""
	def check_existing_nonce(self, node_id):
		for node in self.list_sensor_nodes:
			if node_id == node.node_id:
				if node.end_time >= self.get_current_time():
					return True
		return False

	"""
	Function that returns a pre-shared-key if stored in the cluster database
	Args:
		node_id contains the node_id of the node the PSK has to be returned of
	Returns:
		the PSK of the specific node_id
	"""
	def get_psk(self, node_id):
		conn = sqlite3.connect(self.db_name)
		c = conn.cursor()
		c.execute("""SELECT Beehive.PreSharedKey FROM Beehive WHERE HiveNumber = ?""",(node_id,))
		PSK = list(c.fetchone())
		conn.commit()
		conn.close()
		return PSK[0]

	"""
	Function that returns the current time
	Returns:
		the current time as unix timestamp
	"""
	def get_current_time(self):
		d = datetime.utcnow()
		unix_current_time = calendar.timegm(d.utctimetuple())
		return unix_current_time
