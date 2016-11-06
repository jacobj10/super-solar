import os
import json
import ast
import matlab.engine

from gi.repository import Gtk
from search_endpoint import getReq, getH, write
gtk_builder_file = os.path.splitext(__file__)[0] + '.ui'

class Engine():
	def __init__(self):
		eng = matlab.engine.start_matlab()
		self.builder = Gtk.Builder()
		self.builder.add_from_file(gtk_builder_file)

		self.window = self.builder.get_object('mainWindow')
		self.button = self.builder.get_object('genButton')
		self.checkbox = self.builder.get_object('writeFile')
		self.lat = self.builder.get_object('lat')
		self.lon = self.builder.get_object('lon')
		self.entryJSON = self.builder.get_object('entryJSON')
		self.area = self.builder.get_object('area')
		self.unit = self.builder.get_object('unit')
		self.notebook = self.builder.get_object('notebook')

		self.checkbox.connect('toggled', self.signal_checkbox_toggled)
		self.button.connect('button-press-event', self.signal_button_pressed)
		self.window.connect('destroy', self.signal_window_destroy)

		self.toggled = False

		self.window.resize(800, 600)
		self.window.show()

	def signal_window_destroy(self, _):
		eng.quit()
		self.window.destroy()
		Gtk.main_quit()

	def signal_button_pressed(self, _, event):
		dataPoints = self.handleOpenTab()
		area = self.area.get_text()
		unit = self.unit.get_text()
		result = getReq(dataPoints)
		newJson = json.loads(result.text)
		h = getH(dataPoints[0][1], dataPoints[0][0])
		write(newJson, dataPoints, h)


	def signal_checkbox_toggled(self, _):
		self.toggled = not self.toggled

	def handleOpenTab(self):
		openTab = self.notebook. get_current_page() + 1
		if openTab == 1:
			return [self.lat.get_text(), self.lon.get_text()]
		elif openTab == 2:
			return ast.literal_eval(self.entryJSON.get_text())
		elif openTab == 3:
			return [ None, ]
		return None
x = Engine()
Gtk.main()
