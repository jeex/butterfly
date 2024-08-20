import webview
import webview.menu as wm
import sys
import webbrowser

from helpers.general import Mainroad

class Window:
	_venster = None
	_wprops = [100, 100, 800, 400, False, False]
	_title = 'CPNITS Butterfly v1.04'

	def __init__(self, app):
		wprops = Mainroad.get_window_props()
		if wprops is None:
			sys.exit('Ohoh. Groot probleem')

		if isinstance(wprops, list):
			if len(wprops) == 6:
				self._wprops = wprops
		self.app = app

		self.venster = webview.create_window(
			self._title,
			app,
			x=self._wprops[0],
			y=self._wprops[1],
			width=self._wprops[2],
			height=self._wprops[3],
			maximized=self._wprops[4],
			minimized=self._wprops[5],
			focus=True,
			confirm_close=False,
		)

		self.venster.events.closing += self.on_closing
		self.venster.events.closed += self.on_closed
		self.venster.events.resized += self.on_venster_props
		self.venster.events.moved += self.on_venster_props
		self.venster.events.maximized += self.on_venster_props
		self.venster.events.minimized += self.on_venster_props

		'''
		self.venster.events.loaded += self.on_loaded
		webview.events.closed += on_closed
		webview.events.shown += on_shown
		webview.events.loaded += on_loaded'''

		webview.start(menu=self.make_menu(), ssl=False)

	def force_refresh(self):
		Mainroad.force_reset()
		self.venster.destroy()

	def stop(self):
		self.on_venster_props()
		self.venster.destroy()

	def check_updates(self):
		url = "https://cpnits.com/butterfly.html"
		webbrowser.open(url, new=0, autoraise=True)

	def make_menu(self):
		return [
			wm.Menu('Butterfly', [
				wm.MenuAction('Close', self.stop),
				wm.MenuAction('Force Refresh & Close', self.force_refresh),
				wm.MenuAction('Check for updates', self.check_updates),
				]
	        ),
		]
		''' wm.Menu(
						'Test Menu',
						[
							wm.MenuAction('Change Active Window Content', None),
							wm.MenuSeparator(),
							wm.Menu(
								'Random',
								[
									wm.MenuAction('Click Me', None),
									wm.MenuAction('File Dialog', None),
								],
							),
						],
					), 
					'''
	def on_closed(self):
		pass

	def on_closing(self):
		pass

	def on_loaded(self):
		# bij elke reload van url
		self.venster.title = f'{self._title}'

	def on_venster_props(self):
		self._wprops = [
			self.venster.x,
			self.venster.y,
			self.venster.width,
			self.venster.height,
			self.venster.maximized,
			self.venster.minimized
		]
		Mainroad.set_window_props(self._wprops)


