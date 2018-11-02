"""
---------------------------------
Project: iBee
Date: 20-11-2017
Last updated: 13-12-2017
Libraries: serial
Description: collects data from the serial port and calls the DataProcessor class to process the incoming data.
---------------------------------
"""

import serial
import app
from DataProcessor import ProcessData

class DataCollector():
	"""
	The constructor of the DataCollector class.
	Args: 
		serialport the serialport the gateway is running on.
		baudrate the baudrate the gateway is sending data on.
	"""
	def __init__(self, serialport, baudrate):
		self.baudrate = baudrate
		self.serialport = serialport
		self.ser = ''

	"""
	Function that checks for incoming data and calls functions to process the incoming data.
	Args:
		database_name the name of the database the data should be pushed to.
	"""
	def run_collector(self, database_name):
		data_processor = ProcessData(database_name)
		self.open_port()
		while 1:
			incoming_message = str(self.ser.readline())
			if incoming_message:
				print incoming_message
				msg_type = data_processor.mdp_instance.get_message_type(incoming_message)
				node_id = data_processor.mdp_instance.get_node_id(incoming_message)
				if incoming_message != "\n":
					if data_processor.is_valid(incoming_message) and msg_type == data_processor.mdp_instance.nonce_id:
						if (data_processor.check_existing_nonce(node_id)):
							self.send_ack(msg_type, data_processor.get_nonce(node_id))
						else:
							data_processor.generate_nonce(node_id)
							self.send_ack(msg_type, data_processor.get_nonce(node_id))
					elif data_processor.is_valid(incoming_message):
						if (data_processor.check_authentication(node_id, data_processor.mdp_instance.get_authentication_token(incoming_message))):
							self.send_ack(msg_type, 1)
							data_processor.parse_message(incoming_message)
						else:
							print "Incoming message with invalid authentication token."
							self.send_ack(msg_type, 0)
					else:
						print "Incoming message not validated."
						self.send_ack(msg_type, 0)
							
	"""
	Function that will open the serial port based on the set attributes of the object instance.
	"""
	def open_port(self):
		self.ser = serial.Serial(
			port = self.serialport,
			baudrate = self.baudrate,
			timeout = 1
		)

	"""
	Function that will let the gateway know if an acknowledge message is to be send. If the received data wasn't valid,
	no acknowledge message will be sent.
	Args:
		message_type the type of the message that failed
		result 0 or 1 depending if the message was a valid MDP message or not
	"""
	def send_ack(self, message_type, result):
		acknowledge = str(message_type)
		acknowledge += ","
		acknowledge += str(result)
		self.ser.write(acknowledge)
