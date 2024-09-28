import bleach
from datetime import datetime
import pytz
import time
import pathlib
import os
from urllib.parse import quote_plus as kwoot
import re
import pickle
import sys
from pprint import pprint as ppp
from ftplib import FTP
import io
import webbrowser

import appdirs
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

class Pickles:
	@classmethod
	def read(cls, path: str) -> any:
		try:
			return pickle.load(open(path, 'rb'))
		except:
			pass
		return None

	@classmethod
	def write(cls, path: str, d: dict|list) -> bool:
		try:
			pickle.dump(d, open(path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
			return True
		except Exception as e:
			print(e)
		return False

	@classmethod
	def delete(cls, path: str) -> bool:
		try:
			os.remove(path)
			return True
		except:
			return False

class Mainroad:
	forca = list()
	version = '1.08'
	devdev = False
	logging = False
	updateurl = 'cpnits.com/butterfly.html'

	@classmethod
	def get_empty_settings(cls) -> dict:
		return dict(
			window=[],
			onedrive='',
			magda=['docent'],
			alias='',
			password='',
			version=cls.version,
			viewid=0,
			logging=False,
		)

	@classmethod
	def toggle_logging(cls):
		cls.logging = not cls.logging
		print('cls.logging', cls.logging)
		props = cls.get_props()
		props['logging'] = cls.logging
		cls.set_props(props)

	@classmethod
	def test_settings_thing(cls, thing) -> bool:
		# checks if settingsfile is ok
		if not isinstance(thing, dict):
			cls.loglog(f"test_settings_thing 1: {thing}")
			return False
		for key in cls.get_empty_settings():
			if not key in thing.keys():
				cls.loglog(f"test_settings_thing 2: {key} not in {thing}")
				return False
		if thing['onedrive'] == '':
			cls.loglog(f"test_settings_thing 3: no onedrive in {thing}")
			return False
		if thing['alias'] == '':
			cls.loglog(f"test_settings_thing 4: na alias in {thing}")
			return False
		if thing['password'] == '':
			cls.loglog(f"test_settings_thing 5: no password in {thing}")
			return False
		if not os.path.isdir(thing['onedrive']):
			cls.loglog(f"test_settings_thing 6: OneDrive not valid in {thing}")
			return False
		return True

	@classmethod
	def before_webview_start(cls) -> bool:
		# get user settings path
		cls.force_access('settings', cls.get_settings_dir())
		settings_path = cls.get_settings_path()
		user_settings = Pickles.read(settings_path)
		while not cls.test_settings_thing(user_settings):
			empty = cls.get_empty_settings()
			odpath = cls.ask_onedrive_path() # always valid path, or exit
			empty['onedrive'] = odpath
			user = cls.ask_login(odpath) # always valid login or exit : alias, password, magda
			empty['alias'] = user['alias']
			empty['password'] = user['password']
			empty['magda'] = user['magda']
			cls.loglog(f"{empty}")
			Pickles.write(settings_path, empty)
			user_settings = Pickles.read(settings_path)
			print('HIER???')

		cls.force_access('onedrive', cls.get_onedrive_path())

		# OneDrive path is ok, login via current user-settings must CHECK
		if cls.check_login(user_settings['onedrive'], user_settings['password']) is None:
			cls.force_reset()
			cls.exit_message("Butterfly needs to reset [password]. Please try again.")

		# then check version
		if not cls.check_version(user_settings):
			cls.force_reset()
			cls.exit_message("Butterfly needs to reset [newer version]. Please try again.")

		# set logging
		if 'logging' in user_settings:
			cls.logging = user_settings['logging']
		else:
			cls.logging = False
		print('logging webstart', cls.logging)

		# last: if update required
		message = cls.get_message(newline=' ')
		if message is None:
			return True

		if cls.updateurl in message:
			# open browser to new version
			webbrowser.open(f"https://{cls.updateurl}", new=0, autoraise=True)
		if '!' in message:
			# update required
			cls.force_reset()
			cls.exit_message(message)
		return True
		# ready

	@classmethod
	def get_message(cls, newline=' ') -> str|None:
		path = os.path.join(cls.get_onedrive_path(), 'DO_NOT_DELETE.txt')
		try:
			lines = list()
			with open(path, 'r') as f:
				lines = f.readlines()
			return newline.join(lines)
		except:
			return None

	@classmethod
	def force_reset(cls):
		settingspath = cls.get_settings_path()
		try:
			os.remove(settingspath)
		except:
			pass

	@classmethod
	def ask_onedrive_path(cls):
		# asks for and returns path of one-drive, using Tk
		while True:
			root = tk.Tk()
			root.withdraw()
			odpath = filedialog.askdirectory(title='Open OneDrive dir _BUTTERFLY')
			if odpath is None or odpath == '': # cancel
				cls.exit_message('No Open OneDrive dir _BUTTERFLY given.')

			if not odpath.endswith('_BUTTERFLY'):
				continue
			# correct path, test it, EXIT if wrong
			cls.force_access('onedrive', odpath)
			if os.path.isdir(odpath):
				# return path
				return odpath

	@classmethod
	def ask_login(cls, odpath) -> dict:
		while True:
			root = tk.Tk()
			root.withdraw()
			password = simpledialog.askstring('Password', 'Enter your password')
			if password is None or password.strip() == '':
				cls.exit_message('No Password given.')

			# check give password
			user = cls.check_login(odpath, password=password)
			if user is None:
				continue
			else:
				user['password'] = password
				return user
			# repeat

	@classmethod
	def check_login(cls, odpath, password: str) -> dict|None:
		users = Pickles.read(f"{odpath}/system/s_srs.pickle")
		for user in users: # users is list
			if user['password'] == password:
				return user
		return None

	@classmethod
	def check_version(cls, user_settings) -> bool:
		if not 'version' in user_settings:
			return False
		return user_settings['version'] == cls.version

	@classmethod
	def force_access(cls, name, accessdir):
		if name in cls.forca:
			return

		if name == 'settings':
			try:
				os.makedirs(accessdir, exist_ok=True)
			except Exception as e:
				cls.loglog(f"Force access to dir [{accessdir}] failed. \n\t e = {e}")
				cls.exit_message(f"Force access to dir [{accessdir}] failed. \n\t e = {e}")

		try:
			with open(os.path.join(accessdir, 'access.txt'), 'w') as f:
				f.write(f"Forcing access to [{name}] \n\t{accessdir} \n\t@ {Timetools.now_string()}")
				cls.loglog(f"Forcing access to [{name}] \n\t{accessdir} \n\t@ {Timetools.now_string()}")
				cls.forca.append(name)
		except Exception as e:
			cls.exit_message(f"Force access to [{name}] failed. \n\t e = {e}")
		try:
			pass
			os.remove(os.path.join(accessdir, 'access.txt'))
		except:
			pass
		cls.loglog(f"Force access to [{name}] GELUKT")

	@classmethod
	def exit_message(cls, message: str):
		root = tk.Tk()
		root.withdraw()
		tk.messagebox.showinfo(title='Butterfly Exit', message=f'Butterfly Exit: {message}')
		sys.exit(1)

	@classmethod
	def get_settings_dir(cls) -> str:
		sd = appdirs.user_config_dir()
		if not os.path.isdir(sd):
			cls.exit_message(f'Bizar. Your computer has no {sd} path.')
		return os.path.join(appdirs.user_config_dir(), 'JeexButterfly')

	@classmethod
	def get_settings_path(cls) -> str:
		# no testing involved
		settings_dir = cls.get_settings_dir()
		settings_path = os.path.join(settings_dir, 'butterfly.pickle')
		return settings_path

	@classmethod
	def get_desktop_path(cls) -> str:
		try:
			desktop = os.path.join(pathlib.Path.home(), 'Desktop')
			return desktop
		except Exception as e:
			return ''

	@classmethod
	def get_onedrive_path(cls):
		# only for use after first init.
		settings_path = cls.get_settings_path()
		settings = Pickles.read(settings_path)
		if settings is None:
			cls.exit_message('ERROR: No Settings found [1].')
		try:
			return settings[f'onedrive']
		except:
			# geen onedrive in settings
			cls.exit_message('ERROR: No OneDrive found [2].')

	@classmethod
	def get_system_path(cls):
		return os.path.join(cls.get_onedrive_path(), 'system')

	@classmethod
	def get_emails_path(cls):
		return os.path.join(cls.get_onedrive_path(), 'emails')

	@classmethod
	def get_views_path(cls):
		return os.path.join(cls.get_onedrive_path(), 'views')

	@classmethod
	def get_studentpickles_path(cls):
		return os.path.join(cls.get_onedrive_path(), 'students')

	@classmethod
	def get_student_dirs_path(cls):
		# is dir up from onedrive_path / _JAREN
		upper = os.path.dirname(cls.get_onedrive_path())
		return os.path.join(upper, '_JAREN')

	@classmethod
	def get_window_props(cls) -> list|None:
		propspad = cls.get_settings_path()
		props = Pickles.read(propspad)
		try:
			return props['window']
		except:
			return None

	@classmethod
	def get_prop(cls, name: str):
		props = cls.get_props()
		try:
			return props[name]
		except:
			return None

	@classmethod
	def get_props(cls) -> dict | None:
		propspad = cls.get_settings_path()
		props = Pickles.read(propspad)
		try:
			return props
		except:
			return None

	@classmethod
	def set_props(cls, props: dict):
		propspad = cls.get_settings_path()
		try:
			Pickles.write(propspad, props)
		except Exception as e:
			pass

	@classmethod
	def set_window_props(cls, window_props) -> bool:
		propspad = cls.get_settings_path()
		props = Pickles.read(propspad)
		if props is None:
			return False
		props['window'] = window_props
		return Pickles.write(propspad, props)

	@classmethod
	def loglog(cls, t: str):
		cls.logging = cls.get_prop('logging')
		if cls.logging:
			desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
			pad = os.path.join(desktop, 'loglog.log')
			with open(pad, 'a') as f:
				f.write(t + '\n')


class BaseClass:
	@classmethod
	def get_model(cls) -> dict:
		return dict()

	@classmethod
	def get_empty(cls) -> dict:
		m = cls.get_model()
		newm = dict()
		for key, val in m.items():
			newm[key] = val['default']
		return newm


# General function for type casting
class Casting:
	@classmethod
	def name_safe(cls, s: str, nums: bool) -> str:
		# removes all none-word chars
		parts = s.replace('-', ' ').split(' ')
		nieuw = []
		for p in parts:
			if nums:
				p = re.sub(r'[^a-zA-Z0-9_]', '', p, count=1000).lower().strip()
			else:
				p = re.sub(r'[^a-zA-Z_]', '', p, count=1000).lower().strip()
			if p != '':
				nieuw.append(p)
		return '-'.join(nieuw)

	@classmethod
	def str_(cls, erin, default: str|None='') -> str|None:
		try:
			return str(erin)
		except:
			return default

	@classmethod
	def int_(cls, erin, default: int|None=0) -> int|None:
		try:
			return int(erin)
		except:
			return default

	@classmethod
	def float_(cls, erin, default=0.0) -> float:
		try:
			return float(erin)
		except:
			return default

	@classmethod
	def bool_(cls, erin, default=True) -> bool:
		try:
			return bool(erin)
		except:
			return default

	@classmethod
	def listint_(cls, erin, default=[]):
		try:
			for i in range(len(erin)):
				erin[i] = int(erin[i])
			return erin
		except:
			return default

	@classmethod
	def liststr_(cls, erin, default=[]):
		try:
			for i in range(len(erin)):
				erin[i] = str(erin[i])
			return erin
		except:
			return default

	@classmethod
	def cast(cls, erin, intotype, default=None) -> any:
		if intotype == int:
			if default is None:
				return cls.int_(erin)
			else:
				return cls.int_(erin, default=default)
		elif intotype == float:
			if default is None:
				return cls.float_(erin)
			else:
				return cls.float_(erin, default=default)
		elif intotype == bool:
			if default is None:
				return cls.bool_(erin)
			else:
				return cls.bool_(erin, default=default)
		return str(erin).strip()

	@classmethod
	def typecast_list(cls, l: list, t: type) -> list:
		try:
			return list(map(t, l))
		except Exception as e:
			return []


# General functions for working with time
class Timetools:
	TTIMESTRING = "%Y%m%dT%H00"
	DATETIME_LOCAL = "%Y-%m-%dT%H:%M"
	DATETIMESTRING = "%Y-%m-%d %H:%M:%S"
	DATETIMESTRING_NL = "%d-%m-%Y %H:%M:%S"
	DATESTRING = "%Y-%m-%d"
	DATESTRING_NL = "%d-%m-%Y"
	BIRTH = '1972-02-29'

	# TODO zorgen dat altijd de juiste NL tijd is.

	@classmethod
	def dtlocal_2_ts(cls, tts: str):
		try:
			dt = datetime(
				year=int(tts[0:4]),
				month=int(tts[5:7]),
				day=int(tts[8:10]),
				hour=int(tts[11:13]),
				minute=int(tts[14:16])
			)
			return int(dt.timestamp())
		except:
			return Timetools.td_2_ts(cls.BIRTH)

	@classmethod
	def dtonixzips_2_tms(cls, tts: str):
		try:
			dt = datetime(
				year=int(tts[0:4]),
				month=int(tts[5:7]),
				day=int(tts[8:10]),
				hour=int(tts[11:13]),
				minute=int(tts[14:16]),
				second=int(tts[17:19]),
				microsecond=int(tts[20:])
			)
			return int(dt.timestamp() * 1000)
		except Exception as e:
			return Timetools.td_2_ts(cls.BIRTH) * 1000

	@classmethod
	def td_2_ts(cls, datum: str) -> int:
		# convert date-string yyyy-mm-dd to seconds timestamp
		try:
			dt = datetime(
				year=int(datum[0:4]),
				month=int(datum[5:7]),
				day=int(datum[8:10]),
			)
			return int(dt.timestamp())
		except:
			return Timetools.td_2_ts(cls.BIRTH)

	@classmethod
	def tdtime_2_ts(cls, datumtijd: str) -> int:
		# convert date-string yyyy-mm-dd to seconds timestamp
		try:
			dt = datetime(
				year=int(datumtijd[0:4]),
				month=int(datumtijd[5:7]),
				day=int(datumtijd[8:10]),
				hour=int(datumtijd[11:13]),
				minute=int(datumtijd[14:16]),
				second=int(datumtijd[17:19]),
			)
			return int(dt.timestamp())
		except:
			return Timetools.td_2_ts(cls.BIRTH)

	@classmethod
	def ts_2_td(cls, timest: int, rev=False, withtime=False, local=False) -> str:
		# convert seconds to datestring yyyy-mm-dd
		if local:
			dstr = cls.DATETIME_LOCAL
		elif withtime:
			if rev:
				dstr = cls.DATETIMESTRING
			else:
				dstr = cls.DATETIMESTRING_NL
		else:
			if rev:
				dstr = cls.DATESTRING
			else:
				dstr = cls.DATESTRING_NL
		try:
			return datetime.fromtimestamp(timest, pytz.timezone("Europe/Amsterdam")).strftime(dstr)
		except:
			return ''

	@classmethod
	def now(cls) -> float:
		return time.time()

	@classmethod
	def now_secs(cls) -> int:
		# for normal use
		return int(cls.now())

	@classmethod
	def now_milisecs(cls) -> int:
		# for use in generating unique numbers
		return int(cls.now() * 1000)

	@classmethod
	def now_nanosecs(cls) -> int:
		# not preferred
		return int(cls.now() * 1000000)

	@classmethod
	def ts_2_datetimestring(cls, ts: int|float|None, rev=False, noseconds=False):
		if rev:
			dstr = cls.DATETIMESTRING
		else:
			dstr = cls.DATETIMESTRING_NL
		if noseconds:
			dstr = dstr[:-3]
		if ts is None:
			ts = cls.now()
		if isinstance(ts, int):
			if len(str(ts)) > 11:
				ts = ts / 1000 # nanoseconds
		if not isinstance(ts, float):
			ts = Casting.float_(ts, 0) # adding trailing zero's representing ms and ns
		return datetime.fromtimestamp(ts, pytz.timezone("Europe/Amsterdam")).strftime(dstr)

	@classmethod
	def ts_2_datestring(cls, ts: int | float | None, rev=False):
		if rev:
			dstr = cls.DATESTRING
		else:
			dstr = cls.DATESTRING_NL

		if ts is None:
			ts = cls.now()
		if isinstance(ts, int):
			if len(str(ts)) > 13:
				ts = ts / 1000000  # nanoseconds
			elif len(str(ts)) > 11:
				ts = ts / 1000  # milliseconds
		if not isinstance(ts, float):
			ts = Casting.float_(ts, 0)  # adding trailing zero's representing ms and ns
		return datetime.fromtimestamp(ts, pytz.timezone("Europe/Amsterdam")).strftime(dstr)

	@classmethod
	def now_string(cls) -> str:
		return datetime.fromtimestamp(cls.now(), pytz.timezone("Europe/Amsterdam")).strftime(cls.DATETIMESTRING)
		# return str(datetime.strptime(timestamp, cls.DATETIMESTRING))

	@classmethod
	def datetimenow(cls):
		return datetime.now()

	@classmethod
	def draaiom(cls, erin):
		# changes yyyy-mm-dd into dd-mm-yyyy and vv
		try:
			d = erin.split('-')
			return f'{d[2]}-{d[1]}-{d[0]}'
		except:
			return erin

# General functions for List and Dict manipulation
class ListDicts:
	@staticmethod
	def is_intersect(a: list, b: list) -> bool:
		# returns if values in a are also in b
		try:
			return len(set(a) & set(b)) > 0
		except:
			return False

	@staticmethod
	def all_a_in_b(needles: list, haystack: list) -> bool:
		# checks if all items a are in b.
		# a is the list with required items, b is the list to be checked
		for item in needles:
			if not item in haystack:
				return False
		return True

	@staticmethod
	def sortlistofdicts(lijst: list, sleutel: str|int, reverse=False) -> list:
		try:
			return sorted(lijst, key=lambda d: d[sleutel], reverse=reverse)
		except:
			return lijst


class IOstuff:
	@classmethod
	def make_empty_record(cls, model: dict) -> dict:
		empty = dict()
		for key in model:
			empty[key] = model[key]['default']
		return empty

	# ----------------- cleaning input -----------------
	@classmethod
	def normalize(cls, d: dict, empty_record: dict):
		normalized = dict()
		for key in empty_record:
			if key in d:
				normalized[key] = d[key]
			else:
				normalized[key] = empty_record[key]
		return normalized

	@classmethod
	def normalize_keys(cls, record, emptyrecord) -> dict:
		return cls.normalize(record, emptyrecord)

	@classmethod
	def check_required_keys(cls, keys, reqlist) -> bool:
		# IMP ALWAYS run this before running other defs
		# checks if all required fields are in form
		return ListDicts.all_a_in_b(reqlist, keys)

	@classmethod
	def sanitize(cls, erin):
		return cls.bleken(erin, tags=[])

	@classmethod
	def bleken(cls, erin, tags=[]):
		try:
			erin = bleach.clean(erin, tags=tags, strip=True, strip_comments=True)
		except:
			pass
		if not isinstance(erin, str):
			return ''
		elif erin in ['None', 'none', 'null', 'Null']:
			erin = ''
		return erin

	@classmethod
	def crunch_singles(cls, requestdata, keys) -> dict|None:
		# returns None if key not exists
		result = dict()
		for key in keys:
			try:
				result[key] = cls.sanitize(requestdata[key])
			except:
				return None
		return result

	@classmethod
	def crunch_multi(cls, vals, key) -> list:
		# returns empty list if key not exists
		try:
			for i in range(len(vals)):
				vals[i] = cls.sanitize(vals[i])
			return vals
		except:
			return list()

	# ------------- generic object functions ---------
	@classmethod
	def get_lijst(cls, lijstname: str) -> dict:
		pass
		'''try:
			return lijsten.get_lijst(lijstname)
		except:
			return dict()
'''
	# ------------- ajax functions ----------------
	@classmethod
	def ajaxify(cls, a: any) -> any:
		def iterate_list(l: list) -> list:
			for i in range(len(l)):
				if isinstance(l[i], dict):
					l[i] = iterate_dict(l[i])
				elif isinstance(l[i], list):
					l[i] = iterate_list(l[i])
				else:
					# single value
					pass
			return l
		def iterate_dict(d: dict) -> dict:
			for key in d.keys():
				if isinstance(d[key], dict):
					d[key] = iterate_dict(d[key])
				elif isinstance(d[key], list):
					d[key] = iterate_list(d[key])
				else:
					# single value
					pass
			return d
		if isinstance(a, list):
			a = iterate_list(a)
		elif isinstance(a, dict):
			a = iterate_dict(a)
		# single type value
		else:
			pass
		return a

# ======= as object embedded with data for jinja only =========
class JINJAstuff:
	record = dict()
	model = dict()
	def __init__(self, record, model):
		self.record = record
		self.model = model
		self.lijsten = None # lijsten

	def __del__(self):
		pass

	# ------------- jinja functions only ----------------
	def _id(self):
		try:
			return self.record['id']
		except:
			return ''

	def _kwoot(self, erin):
		# also removes double spaces
		erin = re.sub(' +', ' ', erin)
		return kwoot(erin, safe='', encoding='utf-8', errors='replace')

	def _get_lijst(self, lijstname: str) -> dict:
		try:
			return self.lijsten.get_lijst(lijstname)
		except:
			return dict()

	def _has(self, key) -> bool:
		# key is in record
		return key in self.record

	def _is(self, key: str, val: any) -> bool:
		# compares given val with key-val in current record
		if val is None:
			return False
		return val == self.record[key]

	def _in(self, record_key: str, needle: any) -> bool:
		# checks if give value is in val (list, str, dict)
		try:
			return needle in self.record[record_key]
		except:
			return False

	def _try(self, key, default: any = '') -> any:
		# gets a key from an object if possible
		try:
			return self.record[key]
		except:
			return default

	def _trydeeper(self, key, deepkey, default: any=''):
		one = self._try(key, default=default)
		try:
			return one[deepkey]
		except:
			return one

	def _try_l(self, key, default: any = '') -> any:
		# tries to get value from connected Lijst, if not, default
		val = self._try(key, default=None)  # value from record
		if self.model is None or val is None:
			return default

		try:
			sysl = self.model[key]['lijst']  # name of lijst from lijsten module
			de_lijst = self._get_lijst(sysl)
			return de_lijst[val]
		except:
			return default

	def _bleach(self, key, default='') -> str:
		# bleach flaptext
		tekst = self._try(key, default='')
		try:
			return bleach.clean(
				tekst,
				tags={'b', 'i', 'em', 'br', 'strong', 'small', 'h1', 'h2', 'h3', 'h4', 'h5'},
			    attributes={},
				protocols={},
				strip=True,
				strip_comments=True
			)
		except:
			return ''

	def set_flash(self, key: str, msg: str):
		if not hasattr(self, 'flashes'):
			self.flashes = dict()
		self.flashes[key] = msg

	# with jinja-object giving feedback
	def get_flash(self, key) -> str:
		try:
			return f'<p class="flashed" data-flash="{key}">{self.flashes[key]}</p>'
		except:
			return ''

	def mark_flash(self, key):
		try:
			if key in self.flashes:
				return ' mark-input '
		except:
			pass
		return ''

	def get_record(self):
		return self.record


class FtpAnta:
	# url = 'cpnits.com'
	# user = 'cpnitswebsite@cpnits.com'
	# password = 'CpnitsWebsite'
	# htmldir = 'public_html'

	def __init__(self, url, user, password, basedir):
		self.url = url
		self.user = user
		self.password = password
		self.basedir = basedir
		try:
			self.anta = FTP(self.url, self.user, self.password)
			self.anta.cwd(self.basedir)
		except:
			pass

	def has_indexhtml(self) -> bool:
		try:
			return 'index.html' in self.anta.nlst()
		except:
			return False

	def get_indexhtml(self) -> any:
		# https://stackoverflow.com/questions/30449269/how-can-i-send-a-stringio-via-ftp-in-python-3
		file = io.BytesIO()
		try:
			with file as fp:
				self.anta.retrbinary(f'RETR index.html', fp.write)
				# file_wrapper = io.TextIOWrapper(file, encoding='utf-8')
				return file.getvalue().decode()
		except:
			return None

	def put_indexhtml(self, html: str) -> bool:
		file = io.BytesIO()
		file_wrapper = io.TextIOWrapper(file, encoding='utf-8')
		file_wrapper.write(html)
		file.seek(0)
		try:
			return bool(self.anta.storbinary(f"STOR index.html", file))
		except:
			return False

	def goto_path(self, path: str):
		pass
	'''
	def get_file(self, path: str) -> bool:
		try:
			name = path.split('/')[-1]
			return bool(self.anta.storbinary(f"STOR {name}", file))
		except:
			return False

	def put_file(self, path: str) -> bool:
		try:
			name = path.split('/')[-1]
			return bool(self.anta.storbinary(f"STOR {name}", file))
		except:
			return False
	'''

'''
userspath = os.path.join(Mainroad.get_system_path(), 's_srs.pickle')
userslist = [{'magda': ['docent'], 'alias': 'Iris', 'password': 'trwnvcksghdes'},
 {'magda': ['administratie', 'docent', 'beheer'],
  'alias': 'Jaqueline',
  'password': 'bnuskvbdhyswk'},
 {'magda': ['docent'],
  'alias': 'Sarah',
  'password': 'tgjklncdhsdlobg'},
 {'magda': ['administratie', 'docent', 'beheer', 'admin'],
  'alias': 'Victor',
  'password': 'nr1'},
 {'magda': ['administratie', 'docent', 'beheer'],
  'alias': 'Marcel',
  'password': 'sxtdncdklchnbd'}]

Pickles.write(userspath, userslist)
userslist = Pickles.read(userspath)
ppp(userslist)
'''