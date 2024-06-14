import os, sys, shutil
import random
import string
from copy import deepcopy
from collections import OrderedDict

from flask import current_app

from helpers.general import (
	Casting,
	Timetools,
	ListDicts,
	Pickles,
	Mainroad
)

class Props:
	_props_path = ''
	_od_path = ''
	_props = dict()
	_started = True
	_rollen = ['administratie', 'docent', 'beheer', 'admin']
	_alias = 'Victor'
	_title = ''

	def __init__(self):
		self.init_props()

	def init_props(self): # PROPS pad en OD pad EN het od pad is te vinden in de props pickle
		self._props_path = Mainroad.get_props_path()
		self._props = Pickles.read(self._props_path)
		if self._props is None:
			sys.exit(f'Kon geen settingsfile make of lezen op locatie: {self._props_path}')

	def odpad(self):
		Mainroad.get_od_path()

	def set_window_title(self, title: str):
		self._title = title

	def alias(self):
		return self._alias

	def magda(self, rol: list, alias: str=None) -> bool:
		# alias is de alias van het ding
		if 'admin' in self._rollen:
			return True
		damag = len(list(set(rol) & set(self._rollen))) > 0
		if not alias is None:
			damag = damag and alias.strip() == self.alias()

		return damag

	def is_new(self):
		return self._started

	def get_prop(self, key: str, default=None):
		try:
			return self._props[key]
		except:
			return default

	def set_prop(self, key: str, val):
		self._props[key] = val # update or create
		Pickles.write(self._props_path, self._props)
		self.init_props()

	def force_refresh(self):
		Pickles.delete(self._props_path)
		self._props = dict()

class Sysls:
	_systempath = ''
	_sysls = [
		's_gender',

		's_origin',
		's_uni',
		's_program',

		's_year',
		's_term',
		's_lang',
		's_ec',
		's_course',
		's_stream',

		's_grading',
		's_group',
		's_status',
		's_circular',
		# 's_user',
	]
	_sysmem = dict()

	def __init__(self):
		self.init()

	def init(self):
		self._systempath = os.path.join(Mainroad.get_od_path(), '_DATABASE', 'system')
		self._sysmem = dict()
		for syslname in self._sysls:
			d = Pickles.read(os.path.join(self._systempath, f"{syslname}.pickle"))
			if not d is None:
				self._sysmem[syslname] = self.sorteer_by_ordering(d) # OrderedDict

	def sorteer_by_ordering(self, d: dict) -> OrderedDict:
		ll = list(d.values())
		ll = ListDicts.sortlistofdicts(ll, 'ordering')
		# back to id-based dict
		d = OrderedDict()
		for l in ll:
			d[l['id']] = l
		return d

	def nice_name(self, key: str):
		ss= self._sysls.copy()
		if not key in ss:
			return ''
		return key.replace('s_', '').capitalize()

	def get_lijsten_nicename(self) -> dict:
		eruit = dict()
		for sys in self._sysls.copy():
			eruit[sys] = self.nice_name(sys)
		return eruit

	def get(self):
		return deepcopy(self._sysmem)

	def get_sysl(self, syslname: str, other=False) -> OrderedDict|None:
		# gets dict with id:int as key
		if syslname in self._sysmem:
			return deepcopy(self._sysmem[syslname])

		elif other is True:
			try:
				return Pickles.read(os.path.join(self._systempath, f"{syslname}.pickle"))
			except:
				return None
		return None

	def get_sysl_as_list(self, syslname: str) -> list|None:
		if not syslname in self._sysmem:
			return None
		sd = deepcopy(self._sysmem[syslname])
		return list(sd.values())

	def get_sysl_item(self, syslname: str, id) -> any:
		try:
			id = int(id)
			return self._sysmem[syslname][id]
		except:
			return None

	def get_sysl_item_first_active(self, syslname: str) -> dict|None:
		d = self.get_sysl(syslname)
		for item in d.values():
			if item['status'] == 1:
				return item
		return None

	def set_sysl_item(self, syslname: str, id: int, value) -> bool:
		try:
			self._sysmem[syslname][id] = value
		except:
			return False
		return self.save_sysl(syslname)

	def del_sysl_item(self, syslname: str, id: int) -> bool:
		try:
			del(self._sysmem[syslname][id])
		except:
			return False
		return self.save_sysl(syslname)

	def save_sysl(self, syslname: str) -> bool:
		d = self.get_sysl(syslname)
		if d is None:
			return False
		if Pickles.write(os.path.join(self._systempath, f"{syslname}.pickle"), d):
			self.init()
			return True
		return False

	def make_sysl(self, syslname: str, d, other=False) -> bool:
		if not other and syslname not in self._sysls:
			return False
		pad = os.path.join(self._systempath, f"{syslname}.pickle")
		if Pickles.write(pad, d):
			self.init()
			return True
		return False

	def get_model(self) -> dict:
		model = dict(
			id = {'default': 0},
			name = {'default': ''},
			color = {'default': ''},
			extra = {'default': ''},
			status = {'default': 'actief'},
			ordering = {'default': 0},
		)
		return model

	def get_fields(self) -> list:
		return list(self.get_model().keys())

	def get_empty(self) -> dict:
		m = self.get_model()
		d = dict()
		for field, val in m.items():
			d[field] = val['default']
		return d

class Emails:
	_emailspath = ''
	_sysmem = dict()

	def __init__(self):
		self.init()

	def init(self):
		self._emailspath = os.path.join(Mainroad.get_od_path(), '_DATABASE', 'emails')
		self._sysmem = dict()
		if not os.path.isdir(self._emailspath):
			os.mkdir(self._emailspath)
		for fname in os.listdir(self._emailspath):
			if fname.startswith('.'):
				continue
			if not fname.endswith('.pickle'):
				continue
			d = Pickles.read(os.path.join(self._emailspath, fname))
			try:
				self._sysmem[d['name']] = d
			except:
				continue

	def make_email(self, d: dict) -> bool:
		naam = Casting.name_safe(d['name'], True)
		pad = os.path.join(self._emailspath, f"{naam}.pickle")
		if Pickles.write(pad, d):
			self.init()
			return True
		return False

	def get_single(self, naam: str) -> dict|None:
		try:
			return deepcopy(self._sysmem[naam])
		except:
			return None

	def get(self):
		return deepcopy(self._sysmem)

class Views:
	_viewspath = ''
	_defaultname = 'default'
	_sysmem = dict()

	def __init__(self):
		self.init()

	def empty_view(self):
		return dict(
			name=self._defaultname,
			created_ts=Timetools.now_secs(),
			alias=current_app.config['Props'].alias(),
			color='#ffffff',
			status=1,
			fields=['id', 'firstname', 'lastname'],
			groups=[],
		)

	def init(self):
		self._viewspath = os.path.join(Mainroad.get_od_path(), '_DATABASE', 'views')
		self._sysmem = dict()
		if not os.path.isdir(self._viewspath):
			os.mkdir(self._viewspath)
		for fname in os.listdir(self._viewspath):
			if fname.startswith('.'):
				continue
			if not fname.endswith('.pickle'):
				continue
			d = Pickles.read(os.path.join(self._viewspath, fname))
			try:
				self._sysmem[d['name']] = d
			except:
				continue
		if not self._defaultname in self._sysmem:
			# nog geen standaard view 'min' in systeem:
			d = self.empty_view()
			self.make_view(d)

	def make_view(self, d) -> bool:
		naam = Casting.name_safe(d['name'], True)
		pad = os.path.join(self._viewspath, f"{naam}.pickle")
		if Pickles.write(pad, d):
			self.init()
			return True
		return False

	def get(self) -> OrderedDict:
		dc = OrderedDict(deepcopy(self._sysmem))
		dc = OrderedDict(sorted(dc.items()))
		return dc

	def get_single(self, name):
		try:
			return deepcopy(self._sysmem[name])
		except:
			return None

	def delete(self, name: str):
		if name in self._sysmem and name != self._defaultname:
			del(self._sysmem[name])
			pad = os.path.join(self._viewspath, f"{name}.pickle")
			Pickles.delete(pad)
			self.init()

	def mijn_views(self):
		all = self._sysmem
		mijnviews = list()
		for key, val in all.items():
			if val['alias'] == current_app.config['Props'].alias():
				mijnviews.append(key)
		return mijnviews

	def mijn_groepen(self, all=None):
		# groepen waarbij ik een view heb
		all = self._sysmem
		mijngroepen = list()
		for key, val in all.items():
			if val['alias'] == current_app.config['Props'].alias():
				for g in val['groups']:
					if not g in mijngroepen:
						mijngroepen.append(g)

		return mijngroepen

class Students:
	_stud_p_path = ''
	_stud_dir_path = ''
	_sysmem = dict()

	def __init__(self):
		self.init()

	def init(self):
		self._stud_p_path = os.path.join(Mainroad.get_od_path(), '_DATABASE', 'students')
		self._stud_dir_path = os.path.join(Mainroad.get_od_path(), 'JAREN')
		self._sysmem = dict()
		for fname in os.listdir(self._stud_p_path):
			if fname.startswith('.'):
				continue
			if not fname.endswith('.pickle'):
				continue
			d = Pickles.read(os.path.join(self._stud_p_path, fname))
			try:
				id = d['id']
				self._sysmem[id] = d
			except:
				continue

	def all(self):
		return deepcopy(self._sysmem)

	def all_as_lod(self):
		all = self.all()
		return list(all.values())

	def get_by_id(self, id: int) -> dict | None:
		try:
			return deepcopy(self._sysmem[id])
		except:
			return None

	def id_from_safename(self, fname: str) -> int | None:
		# sdirname = f"{lang}-{d['id']}-{first}-{last}.pickle"
		try:
			id = int(fname.split('-')[0])
			return id
		except:
			return None

	def generate_safename(self, id: int) -> str:
		return f"{id}"

	def generate_safename_full(self, id: int) -> str | None:
		d = self.get_by_id(id)
		if d is None:
			return None
		return self.generate_safename_full_from_d(d)

	def generate_safename_full_from_d(self, d: dict) -> str:
		first = Casting.name_safe(d['firstname'], False)
		last = Casting.name_safe(d['lastname'], False)
		return f"{d['id']}-{first}-{last}"

	def make_student_pickle(self, id: int, d) -> bool:
		try:
			ppath = os.path.join(self._stud_p_path, f"{self.generate_safename(id)}.pickle")
			Pickles.write(ppath, d)
			self.init()
		except Exception as e:
			return False
		return True

	def delete_student_pickle(self, id: int) -> bool:
		try:
			ppath = os.path.join(self._stud_p_path, f"{self.generate_safename(id)}.pickle")
			Pickles.delete(ppath)
		except Exception as e:
			return False
		self.init()
		return True

	def make_student_folder_path(self, id):
		d = self.get_by_id(id)
		if d is None:
			return None
		return self.make_studend_folder_path_from_d(d)

	def make_studend_folder_path_from_d(self, d):
		sysls_o = current_app.config['Sysls']
		if d['s_year'] < 2020:
			return None
		if not d['s_term'] in [1, 2, 3, 4, 5, 6]:
			return None
		jaar = sysls_o.get_sysl_item('s_year', d['s_year'])['name']
		term = sysls_o.get_sysl_item('s_term', d['s_term'])['name']
		safename = self.generate_safename_full_from_d(d)
		studpath = os.path.join(self._stud_dir_path, jaar, term, safename)
		return studpath

	def make_student_folder(self, id: int) -> bool:
		d = self.get_by_id(id)
		try:
			studpath = self.make_student_folder_path(id)
			if studpath is None:
				return False
		except:
			print('NO STUDENT DIR', d)
			return False
		if not os.path.isdir(studpath):
			try:
				os.makedirs(studpath, exist_ok=True)
			except Exception as e:
				return False
		return True

	def move_student_folder(self, oldpath, curpath):
		shutil.move(oldpath, curpath)

	def new_password(self, id):
		x = ''.join(random.choices(string.ascii_lowercase, k=6))
		return f"{id}-{x}"

	def new_student_id(self):
		newid = 0
		for i in self._sysmem:
			if newid < i:
				newid = i
		return newid + 1

	def as_html(self, id):
		sysls_o = current_app.config['Sysls']
		# print(sys._getframe(1).f_code.co_name)
		d = self.get_by_id(id)
		studfields = list(d.keys())
		circfields = sysls_o.get_sysl('s_circular')

		def ccolor(val: int):
			try:
				return circfields[val]['color']
			except:
				return '#eeeeee'

		def make_li(htm, label: str, waarde: str, direct=False):
			try:
				if direct:
					waarde = waarde
				else:
					waarde = d[waarde]
			except:
				waarde = ''
			return f"{htm}\n\t\t\t<li><span>{label}</span>{waarde}</li>"

		def from_list(thing):
			try:
				return sysls_o.get_sysl_item(thing, d[thing])['name']
			except:
				return ''

		def make_note(htm, note):
			try:
				notitie = note['note']
				alias = note['alias']
				dd = Timetools.ts_2_td(note['created_ts'], rev=True)
				return f"{htm}\n\t\t\t<p><span>{alias} op {dd}</span><br>{notitie}</p>"
			except:
				return f"{htm}\n\t\t\t<p><span></span></p>"

		def make_circular(html, circ):
			views_o = current_app.config['Views']
			# creates one line for one circular
			view = views_o.get_single(circ)

			html = f'{html}\n\t\t\t<table class="circular">'
			html = f'{html}\n\t\t\t\t<tr><th></th>'
			for field in view['fields']:
				if field in studfields:
					continue
				html = f'{html}\n\t\t\t\t\t<th>{field}</th>'
			html = f'{html}\n\t\t\t\t</tr>'

			html = f'{html}\n\t\t\t\t<tr><td style="width: 100px;">{circ}</td>'
			for field in view['fields']:
				if field in studfields:
					continue
				if field in d['circulars'][circ]:
					val = d['circulars'][circ][field]
				else:
					val = 0
				kleur = ccolor(val)
				html = f'{html}\n\t\t\t\t\t<td style="background-color: {kleur}"></td>'

			html = f'{html}\n\t\t\t\t</tr>'
			html = f'{html}\n\t\t\t</table>'
			return html

		# ======= main van de html def =======
		if d is None:
			return
		if d['s_status'] in [39]:  # passed
			kleur = 'dodgerblue'
		elif d['s_status'] in [10, 11, 12]:  # ingeschreven
			kleur = 'rgb(254, 232, 86)'  # geel
		elif d['s_status'] in [20, 21, 22]:  # bezig
			kleur = 'darkgreen'
		elif d['s_status'] in [30, 31, 38]:  # gezakt oid
			kleur = 'rgb(221, 53, 110)'  # signaal
		else:
			kleur = "#eee"

		html = basic_student_html() % (d['firstname'], d['lastname'], kleur, kleur, id, d['firstname'], d['lastname'])

		# velden
		html = make_li(html, 'Voornaam', 'firstname')
		html = make_li(html, 'Achternaam', 'lastname')
		html = make_li(html, 'Groep', from_list('s_group'), direct=True)
		html = make_li(html, 'Email', 'email')
		html = make_li(html, 'MVO', from_list('s_gender'), direct=True)

		try:
			url = d["pf_url"]
			link = f'<a href="{url}">{url}</a>'
		except:
			url = ''
			link = ''
		html = make_li(html, 'portfolio', link, direct=True)

		html = make_li(html, 'Wachtwoord', 'password')
		html = make_li(html, 'Cijfer', 'grade')

		if d['grade'] < 1:
			datum = ''
		else:
			try:
				datum = Timetools.ts_2_td(d['grade_ts'], rev=True)
			except:
				datum = ''
		html = make_li(html, 'Cijferdatum', datum, direct=True)

		html = make_li(html, 'Status', from_list('s_status'), direct=True)
		html = make_li(html, 'Herkomst', from_list('s_origin'), direct=True)
		html = make_li(html, 'Uni', from_list('s_uni'), direct=True)
		html = make_li(html, 'Programma', from_list('s_program'), direct=True)
		html = make_li(html, 'Jaar', from_list('s_year'), direct=True)
		html = make_li(html, 'Periode', from_list('s_term'), direct=True)
		html = make_li(html, 'Minor', from_list('s_course'), direct=True)
		html = make_li(html, 'ECs', from_list('s_ec'), direct=True)
		html = make_li(html, 'Taal', from_list('s_lang'), direct=True)

		html = make_li(html, 'KOM-code', 'kom_code')
		html = make_li(html, 'NHLS-code', 'nhls_code')

		html = f'{html}\n\t\t</ul>\n\t\t<h2>Checks</h2>\n\t\t<div class="circulars">'
		if 'circulars' in d:
			for circ in d['circulars']:
				html = make_circular(html, circ)

		html = f'{html}\n\t\t</div>\n\t\t<h2>Notities</h2>\n\t\t<div class="notes">'
		if 'notes' in d:
			for note in d['notes']:
				html = make_note(html, note)

		html = f'{html}\n\t\t</div>\n\t</body>\n</html>'
		filename = self.generate_safename_full_from_d(d) + '.html'
		dirpath = self.make_studend_folder_path_from_d(d)
		filepath = os.path.join(dirpath, filename)
		with open(filepath, 'w') as f:
			f.write(html)


def basic_student_html():
	return '''<!DOCTYPE html>
<html lang="en">
	<head>
		<title>%s %s</title>
		<style>
			*{
				font-family: Arial, Helvetica, sans-serif;
				font-size: 14px;
				border-radius: 3px;
			}
			body{
				padding: 1em;
			}
			ul{
				list-style: inside;
                list-style-type: none;
                margin: 0;
                border: 2px solid %s;
				padding: 1em;
            }
            li{
                margin: 0 0 0.5em 0;
                padding: 0;
                border-bottom: 1px solid #ddd;
            }
            li span{
                display: inline-block;
                width: 10em;
                font-size: 0.8em;
            }
            div.notes,
            div.circulars{
                margin: 1em 0 0 0;
                border: 2px solid %s;
				padding: 1em;
            }
            p span{
                border-bottom: 1px solid #ddd;
                font-size: 0.8em;
            }
            .circular{
                overflow: hidden;
				white-space: nowrap;
            }
            .circular td,
            .circular th{
                font-size: 0.8em;
                padding: 0.25em 0.5em;
            }

		</style>
	</head>
	<body>
		<h1>%s %s %s</h1>
		<ul>
'''