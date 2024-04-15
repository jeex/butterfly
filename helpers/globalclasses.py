import pickle
import os, sys, pathlib
import re
import userpaths as Up
import appdirs
from PyQt6.QtWidgets import QApplication, QFileDialog

# https://pywebview.flowrl.com/examples/resize.html
from helpers.general import Casting

class Pickles:
	@classmethod
	def read(cls, path: str) -> any:
		try:
			return pickle.load(open(path, 'rb'))
		except:
			pass
		return None

	@classmethod
	def write(cls, path: str, d: dict) -> bool:
		try:
			pickle.dump(d, open(path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
			return True
		except:
			pass
		return False


class Props:
	_props_dir = str(os.path.join(appdirs.user_config_dir(), 'JeexButterfly'))
	_props_path = str(os.path.join(_props_dir, 'butterfly_props.pickle'))
	_props = dict()
	_od_path = ''
	_started = True

	@classmethod
	def get_od_path(cls) -> str:
		return cls._od_path

	@classmethod
	def is_new(cls):
		return cls._started

	@classmethod
	def get_prop(cls, key: str, default=None):
		try:
			return cls._props[key]
		except:
			return default

	@classmethod
	def set_prop(cls, key: str, val):
		cls._props[key] = val # update or create
		Pickles.write(cls._props_path, cls._props)

	@classmethod
	def init_props(cls):
		if not os.path.isdir(cls._props_dir):
			os.makedirs(cls._props_dir)
		if not os.path.isfile(cls._props_path):
			Pickles.write(cls._props_path, dict())
		cls._props = Pickles.read(cls._props_path)
		if cls._props is None:
			sys.exit(f'Kon geen settingsfile make of lezen op locatie: {cls._props_path}')

		# set initial OD path
		cls._od_path = cls.get_prop('od_path', None)
		if cls._od_path is None:
			cls._od_path = Up.get_my_documents()
			cls.init_od()

	@classmethod
	def init_od(cls):
		qt = QApplication(sys.argv)
		qt.setStyle('Breeze')
		p = QFileDialog.getExistingDirectory(caption="Waar ligt de OneDrive dir met _DATABASE erin?", directory=str(cls._od_path))
		if p is None or p == '':
			sys.exit()
		cls._od_path = p
		cls.set_prop('od_path', p)

Props.init_props()

class Sysls:
	_systempath = os.path.join(Props.get_od_path(), '_DATABASE', 'system')
	_sysls = [
		's_course',
		's_ec',
		's_gender',
		's_grading',
		's_lang',
		's_origin',
		's_program',
		's_status',
		's_stream',
		's_term',
		's_uni',
		's_user',
		's_year',
	]
	_sysmem = dict()

	@classmethod
	def init(cls):
		for syslname in cls._sysls:
			d = Pickles.read(os.path.join(cls._systempath, f"{syslname}.pickle"))
			if not d is None:
				cls._sysmem[syslname] = d

	@classmethod
	def get_sysl(cls, syslname: str) -> dict|None:
		# gets dict with id:int as key
		if syslname in cls._sysmem:
			return cls._sysmem[syslname]
		return None

	@classmethod
	def get_sysl_item(cls, syslname: str, id) -> any:
		try:
			id = int(id)
			return cls._sysmem[syslname][id]
		except:
			return None

	@classmethod
	def set_sysl_item(cls, syslname: str, id: int, value) -> bool:
		try:
			cls._sysmem[syslname][id] = value
		except:
			return False
		return cls.save_sysl(syslname)

	@classmethod
	def save_sysl(cls, syslname: str) -> bool:
		d = cls.get_sysl(syslname)
		if d is None:
			return False
		if Pickles.write(os.path.join(cls._systempath, f"{syslname}.pickle"), d):
			try:
				# reload updated sysl in mem
				cls._sysmem[syslname] = Pickles.read(os.path.join(cls._systempath, f"{syslname}.pickle"))
				return True
			except:
				pass
		return False

	@classmethod
	def make_sysl(cls, syslname: str, d) -> bool:
		if syslname not in cls._sysls:
			return False
		pad = os.path.join(cls._systempath, f"{syslname}.pickle")
		return Pickles.write(pad, d)

Sysls.init()

class Groups:
	_groupspath = os.path.join(Props.get_od_path(), '_DATABASE', 'groups')
	_sysmem = dict()
	# TODO alleen actieve groepen in geheugen
	# dus andere ophalen als gevraagd

	@classmethod
	def init(cls):
		for fname in os.listdir(cls._groupspath):
			if fname.startswith('.'):
				continue
			if not fname.endswith('.pickle'):
				continue
			d = Pickles.read(os.path.join(cls._groupspath, fname))
			try:
				id = int(fname.replace('group_', '').replace('.pickle', ''))
				cls._sysmem[id] = d
			except:
				continue

	@classmethod
	def make_group(cls, id: int, d) -> bool:
		naam = Casting.name_safe(d['name'], True)
		pad = os.path.join(cls._groupspath, f"{id}-{naam}.pickle")
		return Pickles.write(pad, d)

Groups.init()

class Students:
	_stud_p_path = os.path.join(Props.get_od_path(), '_DATABASE', 'students')
	_stud_dir_path = os.path.join(Props.get_od_path(), 'JAREN')
	_sysmem = dict()

	# TODO alleen actieve studenten in geheugen
	# dus andere ophalen als gevraagd
	@classmethod
	def init(cls):
		for fname in os.listdir(cls._stud_p_path):
			if fname.startswith('.'):
				continue
			if not fname.endswith('.pickle'):
				continue
			d = Pickles.read(os.path.join(cls._stud_p_path, fname))
			try:
				id = d['id']
				cls._sysmem[id] = d
			except:
				continue

	@classmethod
	def all(cls):
		return cls._sysmem

	@classmethod
	def get(cls, id: int) -> dict|None:
		try:
			return cls._sysmem[id]
		except:
			return None

	@classmethod
	def id_from_safename(cls, fname: str) -> int|None:
		# sdirname = f"{lang}-{d['id']}-{first}-{last}.pickle"
		try:
			id = int(fname.split('-')[0])
			return id
		except:
			return None

	@classmethod
	def generate_safename(cls, d: dict) -> str:
		first = Casting.name_safe(d['firstname'], False)
		last = Casting.name_safe(d['lastname'], False)
		return f"{d['id']}-{first}-{last}"

	@classmethod
	def make_student_pickle(cls, id: str, d) -> bool:
		ppath = os.path.join(cls._stud_p_path, f"{cls.generate_safename(d)}.pickle")
		return Pickles.write(ppath, d)

	@classmethod
	def make_student_folder(cls, id: str, d) -> bool:
		try:
			if d['s_year'] < 2020:
				return False
			if not d['s_term'] in [1, 2, 3, 4, 5, 6]:
				return False
			jaar = Sysls.get_sysl_item('s_year', d['s_year'])['name']
			term = Sysls.get_sysl_item('s_term', d['s_term'])['name']
			safename = cls.generate_safename(d)
			studpath = os.path.join(cls._stud_dir_path, jaar, term, safename)
		except:
			print('NO STUDENT DIR', d)
			return False
		if not os.path.isdir(studpath):
			os.makedirs(studpath, exist_ok=True)
		return True

Students.init()