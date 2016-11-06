import os
import json
import ast
import matlab.engine
import logging

from gi.repository import Gtk, Gdk
from search_endpoint import getReq, getH, write
gtk_builder_file = os.path.splitext(__file__)[0] + '.ui'

class Engine():
	def __init__(self):
		self.eng = matlab.engine.start_matlab('-nodisplay')
		self.builder = Gtk.Builder()
		self.builder.add_from_file(gtk_builder_file)
		self.window = self.builder.get_object('mainWindow')
		self.button = self.builder.get_object('genButton')
		self.entryJSON1 = self.builder.get_object('entryJSON1')
		self.entryJSON2 = self.builder.get_object('entryJSON2')

		self.area = self.builder.get_object('area')
		self.unit = self.builder.get_object('unit')
		self.notebook = self.builder.get_object('notebook')

		self.button.connect('button-press-event', self.signal_button_pressed)
		self.window.connect('destroy', self.signal_window_destroy)

		self.toggled = False

		self.window.resize(400, 300)
		self.window.show()

	def signal_window_destroy(self, _):
		self.window.destroy()
		Gtk.main_quit()

	def signal_button_pressed(self, _, event):
		print ("Starting data collection.")
		hashes = {}
		toDoList = [self.entryJSON1,]
		area = self.area.get_text()
		unit = self.unit.get_text()
		if self.entryJSON2.get_text() != '':
			toDoList.append(self.entryJSON2)
		for toDo in toDoList:
			print ("Parsing longtitude and latitude.")
			dataPoints = ast.literal_eval(toDo.get_text())
			print ("Accessing Planet API to get map data.")
			result = getReq(dataPoints)
			newJson = json.loads(result.text)
			print ("Calculating H from NASA data.")
			h = getH(dataPoints[0][1], dataPoints[0][0])
			print ("Creating excel file.")
			hashed = write(newJson, dataPoints, h)
			print ("Creating MATLAB graphs.")
			hashes[hashed] = self.eng.singleSolarArray('./spreadsheets/{0}.xls'.format(hashed), float(area), float(unit), hashed)
		self.displayResults(hashes)

	def displayResults(self, hashes):
		masterBox = Gtk.Box()
		win = Gtk.Window()
		for _hash in hashes:
			image = Gtk.Image()
			image.set_from_file("./images/{0}.jpg".format(_hash))
			label = Gtk.Label()
			labelText = "The approx. energy ouput of this proposed solar\narray is {0} killowatt-hours per unit area.".format(hashes[_hash])
			label.set_text(labelText)
			box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
			box.pack_start(image, True, True, 0)
			box.pack_start(label, True, True, 0)
			masterBox.pack_start(box, True, True, 0)
		win.add(masterBox)
		win.show_all()

x = Engine()
Gtk.main()
