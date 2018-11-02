"""
---------------------------------
Project: iBee
Date: 20-11-2017
Last updated: 13-12-2017
Libraries: time, sqlite3
Description: the ProcessData class will validate, parse and store MDP messages.
---------------------------------
"""

import time
import sqlite3
from MDP import MDP
from NonceHandler import NonceHandler
from datetime import datetime
import calendar

class ProcessData:

	"""
	The constructor of the ProcessData class.
	Args:
		db_name the name of the database the incoming data has to be stored in.

	"""
	def __init__(self, db_name):
		self.db_name = db_name
		self.mdp_instance = MDP()
		self.db_instance = sqlite3.connect(db_name)
		self.nonce_handler = NonceHandler(db_name)

	"""
	Function that calls the MDP validation function (information expert).
	Args:
		line the incoming message (-line) to be checked.
	Returns: 
		true if valid MDP message, else false.
	"""
	def is_valid(self, line):
		return self.mdp_instance.validate_message(line)

	"""
	Function that calls the MDP parsing function and than calls the insertion functions.
	Args:
		line the message (-line) to be parsed.
	"""
	def parse_message(self, line):
		self.mdp_instance.parse_message(line)
		self.insert_message(self.mdp_instance.node_id, self.mdp_instance.payload)

	"""
	Function that inserts a complete MDP (1 out of 3) message to the database.
	Args:
		node_id the node_ID that sent the MDP message.
		mapped_data the data that is stored in a list of tuples; at the left side the sensor_id, at the right side the data that was measured.
	"""
	def insert_message(self, node_id, mapped_data):
		for sensor_id, data in mapped_data:
			self.insert_single_measurement(node_id, sensor_id, data)

	"""
	Function that calls the nonce_handler function to check if a valid nonce exists
	Args:
			node_id the node_id of the node that has a nonce to be checked.
	"""
	def check_existing_nonce(self, node_id):
		return self.nonce_handler.check_existing_nonce(node_id)
	
	"""
	Function that calls the nonce_handler function to get a generated nonce for a specific node
	Args:
			node_id the id of the beehive the nonce is a part of
	"""
	def get_nonce(self, node_id):
		return self.nonce_handler.get_nonce(node_id)

	"""
	Function that calls the nonce_handler function to get a binary nonce a specific node
	Args:
		node_id the id of the beehive the binary nonce (authentication token) is a part of
	"""
	def get_binary_nonce(self, node_id):
		return self.nonce_handler.get_binary_nonce(node_id)
	
	"""
	Function that calls the nonce_handler function to generate a new nonce for a specific node
	Args:
			node_id the id of the beehive the nonce is a part of
	"""
	def generate_nonce(self, node_id):
		self.nonce_handler.append_node(node_id)
		
	"""
	Function that adds a single measurement to the database. In this function the timestamp will be added.
	Args:
		node_id the identifier of the beehive the node is placed.
		sensor_id the sensor_id of the sensor that measured the data (determined in MDP).
		data the data that the measurement returned.
	"""
	def insert_single_measurement(self, node_id, sensor_id, data):
		timestamp = int(time.time())
		self.db_instance.execute('''INSERT INTO Measurement (ClusterLocation, HiveNumber, MeasurementDate, MeasurementType, MeasurementValue) VALUES(?, ?, ?, ?, ?)''', ("Nijmegen, Technvovium 4.29", str(node_id), str(timestamp), str(sensor_id), str(data)))
		self.db_instance.commit()

	"""
	Function that checks if an authentication token is the same as the local generated authentication token
	Args:
	node_id the id of the node the local authentication token has to be requested of
	authentication_token the authentication token of the incoming message
	"""
	def check_authentication(self, node_id, authentication_token):
		if self.get_binary_nonce(node_id) == authentication_token:
			return True
		return False