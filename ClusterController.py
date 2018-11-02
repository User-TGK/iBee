"""
---------------------------------
Project: iBee
Date: 21-11-2017
Last updated: 13-12-2017
Libraries: argv, argparse, threading, time
Description: main file for the controller: handling of the parameters when the script is called.
---------------------------------

Args:
	serialport the USB port of the controller on which the gateway is connected.
	database the name of the sqlite3 database that is to be used (create and insert sql scripts allready have to be runned).
	baudrate optional argument, if the gateway isn't sending data with baudrate 115200 it can manually be altered.
"""

from DataCollection import DataCollector
from sys import argv
import argparse
import app
from threading import Thread
import time

"""
	Function that will start the GUI thread.
	Args:
		database the name of the database instance the GUI has to fetch data from
"""
def flask_thread(database):
	app.start_GUI(database)

"""
	Function that will start the data processing thread.
	Args:
		baudrate the baudrate that the gateway is sending data on
		database the name of the database instance the GUI has to fetch data from
"""
def process_thread(serialport, baudrate, database):
	data_collector = DataCollector(serialport, baudrate)
	data_collector.run_collector(database)

"""
	The 'main' function of the python script. This function will pass the command-line arguments to
	the function that use them. This function will start two threads: one for the GUI and one for the
	data processing.
"""
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("serialport", type=str, help="the serial port the gateway is placed on, for example /dev/ttyUSB0")
	parser.add_argument("database", type=str, help="the name of the sqlite3 database (.db)")
	parser.add_argument("--baudrate", type=int, help="the baudrate the gateway is sending data on, default is 115200")
	args = parser.parse_args()

	baudrate = 115200
	if args.baudrate:
		baudrate = args.baudrate
		print "******* Custom baudrate set *******"

	process_thread = Thread(target = process_thread, args = (args.serialport, baudrate, args.database, ))
	gui_thread = Thread(target = flask_thread, args = (args.database, ))
	process_thread.daemon = True
	gui_thread.daemon = True
	process_thread.start()
	gui_thread.start()

	#Keep the program alive
	while True:
		time.sleep(1)