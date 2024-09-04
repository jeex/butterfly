import webview
import webview.menu as wm
import sys
import webbrowser

from helpers.general import Mainroad

class Window:
	_venster = None
	_wprops = [100, 100, 800, 400, False, False]
	_title = f'CPNITS Butterfly {Mainroad.version}'

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
			minimized=False,
			focus=True,
			confirm_close=False,
			text_select=True,
		)

		self.venster.events.closing += self.on_closing
		self.venster.events.closed += self.on_closed
		# self.venster.events.resized += self.resizing
		self.venster.events.moved += self.on_venster_props
		self.venster.events.maximized += self.on_venster_props
		# self.venster.events.minimized += self.on_venster_props

		webview.start(menu=self.make_menu(), ssl=False)

	def resizing(self):

		pass

	def soft_refresh(self):
		props = Mainroad.get_props()
		if props is None:
			self.venster.destroy()
		try:
			props['last_url'] = '/'
			Mainroad.set_props(props)
		except:
			pass
		self.venster.destroy()

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
				wm.MenuAction('Soft Refresh', self.soft_refresh),
				wm.MenuAction('Force Refresh & Close', self.force_refresh),
				wm.MenuAction('Check for updates', self.check_updates),
				]
	        ),
		]

	def on_closed(self):
		pass

	def on_closing(self):
		self.on_venster_props()

	def on_loaded(self):
		# bij elke reload van url
		self.venster.title = f'{self._title}'

	def on_venster_props(self):
		if self.venster.minimized or self.venster.x < 0 or self.venster.y < 0:
			# do not store minimizer in window props
			return
		self._wprops = [
			self.venster.x,
			self.venster.y,
			self.venster.width,
			self.venster.height,
			self.venster.maximized,
			False
		]
		Mainroad.set_window_props(self._wprops)


