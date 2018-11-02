from Measurement import Measurement
import time, datetime
class SensorNode :

	"""
	The constructor
	Args:
		node_id contains the node id from the sensor node.
	"""
	def __init__(self, node_id, node_location = None):
		 
		self.measurements = []
		self.node_id = node_id
		self.node_location = node_location

	def create_data_list(self, sensor_id):
		timestamps = []
		measurements = []
		for measurement in self.measurements:
			if measurement.sensor_id == sensor_id:
				str_time = datetime.datetime.fromtimestamp(int(measurement.date)).strftime("%Y-%m-%d %H:%M:%S")
				formatted_timestamp = int(datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S").strftime('%s')) * 1000
				timestamps.append(formatted_timestamp)
				measurements.append(measurement.payload)
		return zip(timestamps, measurements)

	def set_measurements(self, measurement_list):
		for measurement in measurement_list:
			new_measurement = Measurement(measurement[0], measurement[1], measurement[2], measurement[3], measurement[4])
			self.measurements.append(new_measurement)

	def get_sensor_description(self, sensor_id):
    		for measurement in self.measurements:
    			if measurement.sensor_id == sensor_id:
    				return str(measurement.sensor_description)
	"""
	A getter to get all the sensor types that only will append to the list if it not exists.
		Returns:
			sensors that contain all the sensor measurement types.
	"""
	def get_distinct_measurement_types(self):
		sensors = set()
		for s in self.measurements:
			sensors.add(s.sensor_id)
		return sensors
