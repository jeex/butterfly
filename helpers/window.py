import webview
import webview.menu as wm

from helpers.globalclasses import Props

class Window:
	_venster = None
	_wprops = [100, 100, 800, 400, False, False]
	_title = 'CPNITS Butterfly'

	def __init__(self, app):
		wprops = Props.get_prop('window_props', default=None)
		if isinstance(wprops, list):
			if len(wprops) == 6:
				self._wprops = wprops

		self.venster = webview.create_window(
			self._title,
			url=app,
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
		self.venster.events.loaded += self.on_loaded

		'''webview.events.closed += on_closed
		webview.events.shown += on_shown
		webview.events.loaded += on_loaded'''

		webview.start(menu=self.make_menu(), ssl=False)

	def make_menu(self):
		return [
			wm.Menu(
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
			wm.Menu('Nothing Here', [wm.MenuAction('This will do nothing', None)]),
		]

	def on_closed(self):
		pass

	def on_closing(self):
		pass

	def on_loaded(self):
		# bij elke reload van url
		title = Props.get_prop('window_title')
		self.venster.title = f'{self._title} | {title}'

	def on_venster_props(self):
		self._wprops = [
			self.venster.x,
			self.venster.y,
			self.venster.width,
			self.venster.height,
			self.venster.maximized,
			self.venster.minimized
		]
		Props.set_prop('window_props', self._wprops)

	def set_tab(self, s: str):
		pass
