class SensorNodeNonce:

	"""
	Constructor of a SensorNodeNonce object
	Args:
		node_id contains the node_id of the node that needs a nonce
		end_time the (unix) time untill when a nonce is a valid nonce
		nonce the nonce for a specific sensornode
		binary_nonce the hashed version of a nonce and PSK
	Returns:
		the PSK of the specific node_id
	"""
	def __init__(self,node_id, end_time, nonce, binary_nonce):
		self.node_id = node_id
		self.end_time = end_time
		self.nonce = nonce
		self.binary_nonce = binary_nonce
