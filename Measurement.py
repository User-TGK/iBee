class Measurement:

	"""    
	The constructor of the measurement class
	Args:
		sensor_id contains the id of the sensor.
		sensor_name contains the name of the sensor.
		payload this is the payload that the sensor has measured.
		time this is time of the measurement.
	"""
	def __init__ (self, sensor_id, quantity, sensor_description, payload, date):
		self.sensor_id = sensor_id
		self.quantity = quantity
		self.sensor_description = sensor_description
		self.payload = payload
		self.date = date