import os
import json
import ast
import matlab.engine
import threading

from gi.repository import Gtk, GObject
from search_endpoint import getReq, getH, write
gtk_builder_file = os.path.splitext(__file__)[0] + '.ui'

class Engine():
	def __init__(self):
		self.hashes = {}
		self.mult = False

		self.eng = matlab.engine.start_matlab('-nodisplay')
		self.builder = Gtk.Builder()
		self.builder.add_from_file(gtk_builder_file)
		self.window = self.builder.get_object('mainWindow')
		self.button = self.builder.get_object('genButton')
		self.entryJSON1 = self.builder.get_object('entryJSON1')
		self.entryJSON2 = self.builder.get_object('entryJSON2')
		self.progress = self.builder.get_object('progress')

		self.area = self.builder.get_object('area')
		self.unit = self.builder.get_object('unit')
		self.notebook = self.builder.get_object('notebook')
		self.status = self.builder.get_object('status')

		self.button.connect('button-press-event', self.signal_button_pressed)
		self.window.connect('destroy', self.signal_window_destroy)

		self.toggled = False

		self.window.resize(400, 300)
		self.window.show()

	def signal_window_destroy(self, _):
		self.window.destroy()
		Gtk.main_quit()

	def signal_button_pressed(self, _, event):
		self.zeroProg()
		threading.Thread(target=self.doEverything).start()

	def doEverything(self):
		self.hashes = {}
		toDoList = [self.entryJSON1,]
		area = self.area.get_text()
		unit = self.unit.get_text()
		if self.entryJSON2.get_text() != '':
			self.mult = True
			toDoList.append(self.entryJSON2)
		else:
			self.mult = False
		for toDo in toDoList:
			GObject.idle_add(self.incProg, "Parsing Longtitude and Latitude")
			dataPoints = ast.literal_eval(toDo.get_text())
			GObject.idle_add(self.incProg, "Getting Satelite Data")
			result = getReq(dataPoints)
			GObject.idle_add(self.incProg, "Parsing results into JSON")
			newJson = json.loads(result.text)
			GObject.idle_add(self.incProg, "Getting annual solar radiance from NASA")
			h = getH(dataPoints[0][1], dataPoints[0][0])
			GObject.idle_add(self.incProg, "Parsing excel file")
			hashed = write(newJson, dataPoints, h)
			GObject.idle_add(self.incProg, "Generating graphs in MATLAB")
			self.hashes[hashed] = self.eng.singleSolarArray('./spreadsheets/{0}.xls'.format(hashed), float(area), float(unit), hashed)
			GObject.idle_add(self.incProg, "Complete!")
		GObject.idle_add(self.displayResults)

	def incProg(self, text=None):
		ratio = 1.0/7
		ratio = ratio / 2 if self.mult else ratio
		self.progress.set_fraction(self.progress.get_fraction() + ratio)
		if text is not None:
			self.status.set_text(text)

	def zeroProg(self):
		self.progress.set_fraction(0.0)

	def displayResults(self):
		masterBox = Gtk.Box()
		win = Gtk.Window()
		for _hash in self.hashes:
			image = Gtk.Image()
			image.set_from_file("./images/{0}.jpg".format(_hash))
			label = Gtk.Label()
			labelText = "The approx. energy ouput of this proposed solar\narray is {0} killowatt-hours.".format(self.hashes[_hash])
			label.set_text(labelText)
			box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
			box.pack_start(image, True, True, 0)
			box.pack_start(label, True, True, 0)
			masterBox.pack_start(box, True, True, 0)
		win.add(masterBox)
		win.show_all()

x = Engine()
Gtk.main()
