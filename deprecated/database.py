import os
import pathlib
import shutil
import sys
import re

from helpers.globalclasses import Props, Pickles


'''
class Database:
	_mainpath = None
	_system_pkls = [
		'origin',
		'uni',
		'program',
		'status',
		'course',
		'ec',
		'stream',
		'user',
		'lang',
		'gender',
		'year',
		'term',
		'grading',
	]

	@classmethod
	def name_safe(cls, s: str) -> str:
		# removes all none-word chars
		return re.sub(r'[^a-zA-Z]', '', s).lower()

	@classmethod
	def _pickle_read(cls, ppath) -> any:
		return Pickles.read(ppath)

	@classmethod
	def _pickle_write(cls, ppath: str, data) -> bool:
		return Pickles.write(ppath, data)

	@classmethod
	def check_sanity(cls) -> bool:
		try:
			cls._mainpath = Props._od_path
			maindirs =  os.listdir(cls._mainpath)
		except:
			return False
		if not 'JAREN' in maindirs or not '_DATABASE' in maindirs:
			sys.exit('No JAREN or _DATABASE')

		# check existance of _DATABASE dir
		dbdirs = os.listdir(os.path.join(cls._mainpath, '_DATABASE'))
		if not 'system' in dbdirs or not 'groups' in dbdirs or not 'students' in dbdirs:
			sys.exit('No valid _DATABASE')

		# check existance of JAREN dir
		jarendirs = os.listdir(os.path.join(cls._mainpath, 'JAREN'))
		for dir in jarendirs:
			if dir.startswith('.'):
				jarendirs.remove(dir)
				continue
			if not dir.isnumeric():
				sys.exit(f'Invalid dir {dir} in JAREN. Remove before restart.')

		# check if exist, else make
		for sp in cls._system_pkls:
			fname = os.path.join(cls._mainpath, '_DATABASE', 'system', f'sys_{sp}.pickle')
			if not os.path.isfile(fname):
				if not Pickles.write(fname, dict()):
					sys.exit(f'Could not make {fname}')
			spd = Pickles.read(fname)
			if spd is None:
				sys.exit(f'Could not open {fname}')

		return True

	@classmethod
	def get_group(cls, id: int) -> list|dict|None:
		fname = os.path.join(cls._mainpath, '_DATABASE', 'groups', f'group_{id}.pickle')
		return cls._pickle_read(fname)

	@classmethod
	def set_group(cls, id: int, group: dict) -> bool:
		fname = os.path.join(cls._mainpath, '_DATABASE', 'groups', f'group_{id}.pickle')
		return cls._pickle_write(fname, group)

	@classmethod
	def get_system(cls, sp: str) -> dict | None:
		if not sp in cls._system_pkls:
			return None
		fname = os.path.join(cls._mainpath, '_DATABASE', 'system', f'sys_{sp}.pickle')
		return cls._pickle_read(fname)

	@classmethod
	def set_system(cls, sp: str, d: dict) -> bool:
		if not sp in cls._system_pkls:
			return False
		fname = os.path.join(cls._mainpath, '_DATABASE', 'system', f'sys_{sp}.pickle')
		return cls._pickle_write(fname, d)

	@classmethod
	def get_student(cls, id: int) -> list | dict | None:
		fname = os.path.join(cls._mainpath, '_DATABASE', 'students', f'student_{id}.pickle')
		return cls._pickle_read(fname)

	@classmethod
	def set_student(cls, id: int, student: dict) -> bool:
		fname = os.path.join(cls._mainpath, '_DATABASE', 'students', f'student_{id}.pickle')
		return cls._pickle_write(fname, student)

	@classmethod
	def make_student_html(cls, id: int) ->bool:
		# creates HTML file with all student data
		return True

	# no system for:
			# gender m/v/n
			# ec 15/30
			# lang nl/en

if not Database.check_sanity():
	Props.init_od()
	if not Database.check_sanity():
		exit('No sane database available')
		
'''