from highcharts import Highchart
from SensorNode import SensorNode
from enum import Enum
import time, datetime, sqlite3

class TimeInterval(Enum):
    TODAY     = 1
    YESTERDAY = 2
    LAST_WEEK = 3
    CUSTOM    = 4

class HighChartsGraphCreator:
    
    """
        Constructor of the HighChartsGraph creator object.
    """
    def __init__(self, node_id, database):
        self.node_id = node_id
        self.database = database

    def get_begin_and_end_timestamps(self, custom_start_date, custom_end_date, time_interval):
        timestamps = []
        start_date = datetime.datetime.now()
        start_date = start_date.replace(hour = 0, minute = 0, second = 0)
        end_date = start_date + datetime.timedelta(days=1)

        if time_interval == TimeInterval.CUSTOM:
            ## Convert to string
            start_date = custom_start_date
            end_date = custom_end_date

            ## convert to datetime
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

            ## set hour minute and seconds to zero.
            start_date = start_date.replace(hour = 0, minute = 0, second = 0)
            end_date = end_date.replace(hour = 0, minute = 0, second = 0)

        elif time_interval == TimeInterval.TODAY:
            start_date = datetime.datetime.now()
            start_date = start_date.replace(hour = 0, minute = 0, second = 0)
            end_date = start_date + datetime.timedelta(days=1)

        elif time_interval == TimeInterval.YESTERDAY:
            start_date = datetime.datetime.now() - datetime.timedelta(days=1)
            start_date = start_date.replace(hour = 0, minute = 0, second = 0)
            end_date = start_date + datetime.timedelta(days=1)
                
        elif time_interval == TimeInterval.LAST_WEEK:
            start_date = datetime.datetime.now()
            start_date = start_date.replace(hour = 0, minute = 0, second = 0)
            end_date = start_date
            start_date = start_date - datetime.timedelta(days=7)

        ## convert time to a unix time stamp.	
        start_date = time.mktime(start_date.timetuple())
        end_date = time.mktime(end_date.timetuple())
        timestamps.append(start_date)
        timestamps.append(end_date)

        return timestamps

    """
	    Creates the graph that will be displayed on the page. 
	    Args:
		    sensor_name This will be the name of the sensor (temp, hum, weight, state)
		    sensor_node This must be a object of sensor_node. 
	    Returns:
		    The graph that is constructed based of the sensornode values. 
    """
    def create_graph(self, custom_begin_date, custom_end_date, quantity, time_interval):
        sensor_node = SensorNode(self.node_id)
        timestamps = self.get_begin_and_end_timestamps(custom_begin_date, custom_end_date, time_interval)
        line_graph = Highchart()
        time_label = ''

        sensor_node.set_measurements(self.select_measurements(timestamps[0], timestamps[1], quantity))
        measurement_types = sensor_node.get_distinct_measurement_types()

        for m_type in measurement_types:
            data_list = sensor_node.create_data_list(m_type)
            line_graph.add_data_set(data_list, series_type='line', name=(sensor_node.get_sensor_description(m_type)))

        if time_interval == TimeInterval.TODAY or time_interval == TimeInterval.YESTERDAY:
            time_label = "'hour': '%H:%M'"
        elif time_interval == TimeInterval.LAST_WEEK:
            time_label = "'day': '%e. %b'"

        options = {
		    'title': {
		        'text': str(quantity) + " meetdata van bijenkast " + str(sensor_node.node_id)
		    },
		    'subtitle': {
			    'text': "iBee 2017-2018"
		    },
		    'xAxis': {
			    'type': "datetime",
			    'dateTimeLabelFormats': {
				    time_label
			    },
			    'title': {
				    'text': "Tijd"
			    }
		    },
		    'yAxis': {
			    'title': {
				    'text': quantity
			    }
		    }
	    }
        line_graph.set_dict_options(options)   
    	
        return line_graph

    """
	    Query that will be executed for all measurements between two times, a certain sensor name and node id.
	    Args:
		    start_date This will be used for the between in the query.
		    end_date this will also be used for the between in the query.
		    node_id This will be used to filter only for one node id.
		    sensor_name This will be used to filter only for one sensor name.
	    Returns:
		    The query values. 
    """
    def select_measurements(self, start_date, end_date, quantity):
	    conn = sqlite3.connect(self.database)
	    c = conn.cursor()
	    c.execute("""SELECT Measurement.MeasurementType, MeasurementTypes.Quantity, MeasurementTypes.Description, Measurement.MeasurementValue, Measurement.MeasurementDate
		    FROM Measurement INNER JOIN MeasurementTypes ON Measurement.MeasurementType= MeasurementTypes.MeasurementType
			    WHERE Measurement.MeasurementDate
				    BETWEEN  ? AND ? AND
					    MeasurementTypes.Quantity = ?
							    AND Measurement.HiveNumber = ?
								    ORDER BY Measurement.MeasurementDate """,(start_date, end_date, quantity, self.node_id))
	    query = c.fetchall()
	    ## Closing the connection.
	    conn.commit()
	    conn.close()
	    return query
