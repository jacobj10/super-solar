import os
import json
import ast
import matlab.engine
import threading

from gi.repository import Gtk, GObject, Gdk
from search_endpoint import getReq, getH, write
gtk_builder_file = os.path.splitext(__file__)[0] + '.ui'
cityDict = {
			'Atlanta': '[-84.49722290039061,33.84589679025757],[-84.28024291992186,33.850458953137945],[-84.26651000976561,33.61976556057674],[-84.5082092285156,33.63806091415168],[-84.49722290039061,33.84589679025757]',
			'Cleveland': '[-81.875359001045,41.35038199001244],[-81.875359001045,41.6080070078244],[-81.4199359900001,41.6080070078244],[-81.4199359900001,41.35038199001244],[-81.875359001045,41.35038199001244]',
			'NYC': '[-73.9215087890625,40.87120891742626],[-73.92562866210936,40.78392095327908],[-74.00115966796875,40.69964162534313],[-74.0533447265625,40.703806073855475],[-73.9215087890625,40.87120891742626]',
			'Orlando': '[-81.53640747070312,28.627322583094255],[-81.16836547851562,28.62973338042744],[-81.16012573242186,28.323120110852855],[-81.66824340820312,28.33762578682955],[-81.53640747070312,28.627322583094255]',
			'Pittsburgh': '[-79.95162963867186,40.5101449020018],[-79.83078002929686,40.4328369438891],[-79.96261596679689,40.36381153078335],[-80.08071899414062,40.43910847204671],[-79.95162963867186,40.5101449020018]',
			'Sacramento': '[-121.634126009992,38.387666999876615],[-121.634126009992,38.778996007314475],[-121.24218499334701,38.778996007314475],[-121.24218499334701,38.387666999876615],[-121.634126009992,38.387666999876615]',
			'San Diego': '[-117.266222008727,32.534174991827314], [-117.266222008727,33.07220700851201], [-116.85312199003701,33.07220700851201], [-116.85312199003701,32.534174991827314], [-117.266222008727,32.534174991827314]',
			'San Francisco': '[-122.5149480093,37.60448099159238], [-122.5149480093,37.83242700925851], [-122.35504399161,37.83242700925851], [-122.35504399161,37.60448099159238], [-122.5149480093,37.60448099159238]',
			'Los Angeles': '[-118.521455009776,33.90189298999998], [-118.521455009776,34.1614390095055], [-118.12130699003,34.1614390095055], [-118.12130699003,33.90189298999998], [-118.521455009776,33.90189298999998]'
			}

class Engine():
	def __init__(self):
		self.hashes = {}
		self.mult = False

		self.eng = matlab.engine.start_matlab('-nodisplay')
		self.builder = Gtk.Builder()
		self.builder.add_from_file(gtk_builder_file)
		self.window = self.builder.get_object('mainWindow')
		self.window.connect('button_press_event', self._button_press)
		self.button = self.builder.get_object('genButton')
		self.entryJSON1 = self.builder.get_object('entryJSON1')
		self.entryJSON2 = self.builder.get_object('entryJSON2')
		self.progress = self.builder.get_object('progress')
		self.notebook = self.builder.get_object('notebook')

		self.area = self.builder.get_object('area')
		self.unit = self.builder.get_object('unit')
		self.status = self.builder.get_object('status')

		self.button.connect('button-press-event', self.signal_button_pressed)
		self.window.connect('destroy', self.signal_window_destroy)

		self.toggled = False
		self._get_popup_menu()
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


	def _get_popup_menu(self):
		self.popup_menu = Gtk.Menu.new()

		menu_item = Gtk.MenuItem.new_with_label('Atlanta')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('Cleveland')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('NYC')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('Orlando')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('Pittsburgh')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('Sacramento')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('San Diego')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('San Francisco')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)
		menu_item = Gtk.MenuItem.new_with_label('Los Angeles')
		menu_item.connect('activate', self.test, menu_item.get_label())
		self.popup_menu.append(menu_item)

		self.popup_menu.show_all()

	def test(self, _, label):
		if self.notebook.get_current_page() == 0:
			self.entryJSON1.set_text(cityDict[label])
		else:
			self.entryJSON2.set_text(cityDict[label])

	def _button_press(self, _, event):
		if event.button == Gdk.BUTTON_SECONDARY:
			self.popup_menu.popup(None, None, None, None, event.button, Gtk.get_current_event_time())
			return True
		return

x = Engine()
Gtk.main()
