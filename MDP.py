"""
---------------------------------
Project: iBee
Date: 20-11-2017
Last updated: 13-12-2017
Libraries: time, sqlite3
Description: implementation of the Message Data Protocol (MDP)
---------------------------------
"""

class MDP:

	"""
	The constructor of the MDP class. This constructor will set all characteristics of the MDP protocol.
	Examples are: which message types are there; at what byte does the actual payload begin and so on.
	"""
	def __init__(self):
		self.node_id = 0
		self.message_type = 0
		self.authentication_token = 0
		self.message_types = [0, 1, 2, 3, 255]
		self.payload = []
		self.nonce_id = 255
		self.protocol_payload_begin = 3
		self.protocol_payload_end = 10
		self.protocol_nr_of_payloads = 7
		self.protocol_nr_of_parameters = 10

	"""
	Function that will check of an incoming message is a valid MDP message.
	Args:
		data the data to be checked.
	Returns:
		true if the message is a valid MDP message, false if not.
	"""
	def validate_message(self, data):
		if data.count(' ') == self.protocol_nr_of_parameters-1:
			data_array = data.split(' ')
			for value in data_array:
				try:
					float(value)
				except ValueError:
					return False

			if not (self.is_valid_node_id(int(float(data_array[0])))):
				return False
			else:
				node_id = int(float(data_array[0]))

			message_type = int(float(data_array[1]))

			if message_type == 0:
				for value in data_array[3:10]:
					if not (self.is_valid_temperature(float(value))):
						return False

			elif message_type == 1:
				for value in data_array[3:5]:
					if not (self.is_valid_temperature(float(value))):
						return False
				for value in data_array[6:10]:
					if not (self.is_valid_humidity(float(value))):
						return False

			elif message_type == 2:
				for value in data_array[3:7]:
					if not (self.is_valid_humidity(float(value))):
						return False
					if not (0 <= float(data_array[7]) < 100):
						return False
					if not (float(data_array[8]) == 1.00 or float(data_array[8]) == 0.00):
						return False

			elif message_type == 255:
				return True
		else:
			return False
		return True
	
	"""
	Function that will check if the node_id in the message is a valid node id.
	Args:
		node_id the node id to be checked.
	"""
	def is_valid_node_id(self, node_id):
		if node_id >= 1 and node_id <= 255:
			return True
		return False

	"""
	Function that will check if a value is a valid temperature value.
	Args:
		temperature the temperature to be checked.
	"""
	def is_valid_temperature(self, temperature):
		if temperature >= -40 and temperature < 80:
			return True
		return False

	"""
	Function that will check if a value is a valid humidity value.
	Args:
		humidity the humidity to be checked.
	"""
	def is_valid_humidity(self, humidity):
		if humidity >= 0 and humidity <= 100:
			return True
		return False

	"""
	Function that will parse a MDP message into a node_id, message_type and list of tuples (sensor_id on the left side, data on the right side).
	Args:
		line the line to be parsed.
	"""
	def parse_message(self, line):
		element_list = line.split(' ', self.protocol_nr_of_parameters)
		self.node_id = int(float(element_list[0]))
		self.message_type = int(float(element_list[1]))
		data = []

		for i in range(self.protocol_payload_begin, self.protocol_payload_end):
			data.append(float(element_list[i]))

		for msg_type in self.message_types:
			if msg_type == self.message_type:
				self.set_payload(msg_type, data[:])
				return None

		raise Exception("MDP parse exception. MDP message type couldn't be parsed.")

	"""
	Function that will add a sensor_id to a measurement based on the message_type.
	Args:
		msg_type the MDP message type the payload has to be set of
		data a list of measurements.
	"""
	def set_payload(self, msg_type, data):
		index = 0
		new_payload = []
		if msg_type == 2:
			del data[-1]
		for i in data:
			sensor_id = (index+1) + (msg_type*self.protocol_nr_of_payloads)
			sensor_tuple = (sensor_id, i)
			new_payload.append(sensor_tuple)
			index += 1
		self.payload = new_payload

	"""
	Function that will return the message type of a message.
	Args:
		message the message to get the message_type of
	Returns:
		-1 if the message type is invalid, else the MDP message type
	"""
	def get_message_type(self, message):
		element_list = message.split(' ', self.protocol_nr_of_parameters)
		try:
			msg_type = int(float(element_list[1]))
			for msg_type_stored in self.message_types:
				if msg_type == msg_type_stored:
					return msg_type
		except ValueError:
			msg_type = -1
		return msg_type

	"""
	Function that will get and return the node_id of a specific MDP message
	Args:
		message the message to get the message_type of
	Returns:
		-1 if the message type is invalid, else the MDP node_id
	"""
	def get_node_id(self, message):
		element_list = message.split(' ', self.protocol_nr_of_parameters)
		try:
			node_id = int(float(element_list[0]))
			return node_id
		except ValueError:
			node_id = -1
		return node_id

	"""
	Function that parses a MDP message and returns its authentication token
	Args:
		message the message the MDP instance has to find the authenticaton token of
	"""
	def get_authentication_token(self, message):
		element_list = message.split(' ', self.protocol_nr_of_parameters)
		try:
			authentication_token = int(element_list[2])
			return authentication_token
		except ValueError:
			authentication_token = -1
		return authentication_token
