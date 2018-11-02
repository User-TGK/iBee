from flask import Flask, render_template, request
from highcharts import Highchart
import sqlite3
from HighChartsGraphCreator import HighChartsGraphCreator, TimeInterval
from SensorNode import SensorNode

app = Flask(__name__)

"""
	Function that starts the FLASK webserver.
	Args:
		database_name the name of the database the webserver has to communicate with
"""
def start_GUI(database_name):
	global database
	database = database_name
	app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


"""
	The index of the webserver.
	Returns:
		a list of dynamic sensor types on the page. 
"""  
@app.route('/')
def index():
	## Create connection with the database.
	conn = sqlite3.connect(database)
	c = conn.cursor()

	## Select all the sensor nodes.
	c.execute("SELECT ClusterLocation, HiveNumber FROM Beehive ")
	query_node_id = c.fetchall()
	sensor_nodes = []

	## Create all the sensor node objects.
	for column in query_node_id:
		sensor_node = SensorNode(column[1], column[0])
		sensor_nodes.append(sensor_node)

	conn.commit()
	c.execute("SELECT Quantity FROM Quantities ")
	quantities_query = list(c.fetchall())
	## Close the connection.
	conn.commit()
	conn.close()
	return render_template('index.html', sensor_nodes = sensor_nodes, quantities = quantities_query)

"""
Function that returns a "page not found" error message when an invalid URL was entered
"""
@app.errorhandler(404)
def page_not_found(e):
	return (render_template('404.html'))

"""
	This will return the graph page based on the selection of the users input.
	Args:
	node_id contains the node id of the sensor id 
	sensor_name is a dict with the specific sensor name 
	Returns:
		a list of dynamic sensor types on the page. 
"""  
@app.route('/graph/<string:node_id>/<string:quantity>/', methods=['GET', 'POST'])
def graph_page(node_id, quantity):
	node_id = node_id
	quantity = quantity
	custom_start_date = ''
	custom_end_date = ''
	## Selected time_interval is by default today
	time_interval = TimeInterval.TODAY
	graph_creator = HighChartsGraphCreator(node_id, database)

	if request.method == 'POST':
    		
    	## time_interval is a custom time interval (date to date)
		if request.form['action'] == "Selecteer een datum":
			time_interval = TimeInterval.CUSTOM
			custom_start_date = str(request.form['start_date'])
			custom_end_date = str(request.form['end_date'])

		## time_interval is today
		elif request.form['action'] == "vandaag":
			time_interval = TimeInterval.TODAY

		## time_interval is yesterday
		elif request.form['action'] == "gisteren":
			time_interval = TimeInterval.YESTERDAY

		## time_interval is last week
		elif request.form['action'] == "vorige week":
			time_interval = TimeInterval.LAST_WEEK

	graph_data = graph_creator.create_graph(custom_start_date, custom_end_date, quantity, time_interval).renderTo

	try:
		return render_template('graphing.html', node_id = node_id, quantity = quantity, graph_data = graph_data)

	except Exception, e:
		return(str(e))
