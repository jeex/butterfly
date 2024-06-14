
import pickle
import os, sys
import userpaths as Up
import appdirs
from PyQt6.QtWidgets import QApplication, QFileDialog

# https://pywebview.flowrl.com/examples/resize.html
from helpers.general import Casting, Timetools, ListDicts

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

	@classmethod
	def delete(cls, path: str) -> bool:
		try:
			os.remove(path)
			return True
		except:
			return False

class Props:
	_props_dir = str(os.path.join(appdirs.user_config_dir(), 'JeexButterfly'))
	_props_path = str(os.path.join(_props_dir, 'butterfly_props.pickle'))
	_props = dict()
	_od_path = ''
	_started = True
	_rollen = ['administratie', 'docent', 'beheer', 'admin']
	_alias = 'Victor'
	_title = ''

	@classmethod
	def set_window_title(cls, title: str):
		cls._title = title

	@classmethod
	def odpad(cls):
		return cls._od_path

	@classmethod
	def alias(cls):
		return cls._alias

	@classmethod
	def magda(cls, rol: list, alias: str=None) -> bool:
		# alias is de alias van het ding
		if 'admin' in cls._rollen:
			return True
		damag = len(list(set(rol) & set(cls._rollen))) > 0
		if not alias is None:
			damag = damag and alias.strip() == cls.alias()

		return damag

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
		cls.init_props()

	@classmethod
	def force_refresh(cls):
		Pickles.delete(cls._props_path)
		cls._props = dict()

	@classmethod
	def init_props(cls):
		if not os.path.isdir(cls._props_dir):
			os.makedirs(cls._props_dir)
		if not os.path.isfile(cls._props_path):
			Pickles.write(cls._props_path, dict())
			cls.init_props()
		cls._props = Pickles.read(cls._props_path)

		'''print()
		ppp(cls._props)'''

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

'''
class Sysls:
	_systempath = os.path.join(Props.get_od_path(), '_DATABASE', 'system')
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

	@classmethod
	def init(cls):
		cls._sysmem = dict()
		for syslname in cls._sysls:
			d = Pickles.read(os.path.join(cls._systempath, f"{syslname}.pickle"))
			if not d is None:
				cls._sysmem[syslname] = cls.sorteer_by_ordering(d) # OrderedDict

	@classmethod
	def sorteer_by_ordering(cls, d: dict) -> OrderedDict:
		ll = list(d.values())
		ll = ListDicts.sortlistofdicts(ll, 'ordering')
		# back to id-based dict
		d = OrderedDict()
		for l in ll:
			d[l['id']] = l
		return d

	@classmethod
	def nice_name(cls, key: str):
		ss= cls._sysls.copy()
		if not key in ss:
			return ''
		return key.replace('s_', '').capitalize()

	@classmethod
	def get_lijsten_nicename(cls) -> dict:
		eruit = dict()
		for sys in cls._sysls.copy():
			eruit[sys] = cls.nice_name(sys)
		return eruit

	@classmethod
	def get(cls):
		return deepcopy(cls._sysmem)

	@classmethod
	def get_sysl(cls, syslname: str, other=False) -> OrderedDict|None:
		# gets dict with id:int as key
		if syslname in cls._sysmem:
			return deepcopy(cls._sysmem[syslname])

		elif other is True:
			try:
				return Pickles.read(os.path.join(cls._systempath, f"{syslname}.pickle"))
			except:
				return None
		return None

	@classmethod
	def get_sysl_as_list(cls, syslname: str) -> list|None:
		if not syslname in cls._sysmem:
			return None
		sd = deepcopy(cls._sysmem[syslname])
		return list(sd.values())

	@classmethod
	def get_sysl_item(cls, syslname: str, id) -> any:
		try:
			id = int(id)
			return cls._sysmem[syslname][id]
		except:
			return None

	@classmethod
	def get_sysl_item_first_active(cls, syslname: str) -> dict|None:
		d = cls.get_sysl(syslname)
		for item in d.values():
			if item['status'] == 1:
				return item
		return None

	@classmethod
	def set_sysl_item(cls, syslname: str, id: int, value) -> bool:
		try:
			cls._sysmem[syslname][id] = value
		except:
			return False
		return cls.save_sysl(syslname)

	@classmethod
	def del_sysl_item(cls, syslname: str, id: int) -> bool:
		try:
			del(cls._sysmem[syslname][id])
		except:
			return False
		return cls.save_sysl(syslname)

	@classmethod
	def save_sysl(cls, syslname: str) -> bool:
		d = cls.get_sysl(syslname)
		if d is None:
			return False
		if Pickles.write(os.path.join(cls._systempath, f"{syslname}.pickle"), d):
			cls.init()
			return True
		return False

	@classmethod
	def make_sysl(cls, syslname: str, d, other=False) -> bool:
		if not other and syslname not in cls._sysls:
			return False
		pad = os.path.join(cls._systempath, f"{syslname}.pickle")
		if Pickles.write(pad, d):
			cls.init()
			return True
		return False

	@classmethod
	def get_model(cls) -> dict:
		model = dict(
			id = {'default': 0},
			name = {'default': ''},
			color = {'default': ''},
			extra = {'default': ''},
			status = {'default': 'actief'},
			ordering = {'default': 0},
		)
		return model

	@classmethod
	def get_fields(cls) -> list:
		return list(cls.get_model().keys())

	@classmethod
	def get_empty(cls) -> dict:
		m = cls.get_model()
		d = dict()
		for field, val in m.items():
			d[field] = val['default']
		return d

Sysls.init()
'''

'''
class Views:
	_viewspath = os.path.join(Props.get_od_path(), '_DATABASE', 'views')
	_defaultname = 'default'
	_sysmem = dict()

	@classmethod
	def empty_view(cls):
		return dict(
			name=cls._defaultname,
			created_ts=Timetools.now_secs(),
			alias=Props.alias(),
			color='#ffffff',
			status=1,
			fields=['id', 'firstname', 'lastname'],
			groups=[],
		)
	@classmethod
	def init(cls):
		cls._sysmem = dict()
		if not os.path.isdir(cls._viewspath):
			os.mkdir(cls._viewspath)
		for fname in os.listdir(cls._viewspath):
			if fname.startswith('.'):
				continue
			if not fname.endswith('.pickle'):
				continue
			d = Pickles.read(os.path.join(cls._viewspath, fname))
			try:
				cls._sysmem[d['name']] = d
			except:
				continue
		if not cls._defaultname in cls._sysmem:
			# nog geen standaard view 'min' in systeem:
			d = cls.empty_view()
			cls.make_view(d)

	@classmethod
	def make_view(cls, d) -> bool:
		naam = Casting.name_safe(d['name'], True)
		pad = os.path.join(cls._viewspath, f"{naam}.pickle")
		if Pickles.write(pad, d):
			cls.init()
			return True
		return False

	@classmethod
	def get(cls) -> OrderedDict:
		dc = OrderedDict(deepcopy(cls._sysmem))
		dc = OrderedDict(sorted(dc.items()))
		return dc

	@classmethod
	def get_single(cls, name):
		try:
			return deepcopy(cls._sysmem[name])
		except:
			return None

	@classmethod
	def delete(cls, name: str):
		if name in cls._sysmem and name != cls._defaultname:
			del(cls._sysmem[name])
			pad = os.path.join(cls._viewspath, f"{name}.pickle")
			Pickles.delete(pad)
			cls.init()

	@classmethod
	def mijn_views(cls):
		all = cls._sysmem
		mijnviews = list()
		for key, val in all.items():
			if val['alias'] == Props.alias():
				mijnviews.append(key)
		return mijnviews

	@classmethod
	def mijn_groepen(cls, all=None):
		# groepen waarbij ik een view heb
		all = cls._sysmem
		mijngroepen = list()
		for key, val in all.items():
			if val['alias'] == Props.alias():
				for g in val['groups']:
					if not g in mijngroepen:
						mijngroepen.append(g)

		return mijngroepen

Views.init()
'''

'''
class Groups:
	_groupspath = os.path.join(Props.get_od_path(), '_DATABASE', 'groups')
	_sysmem = dict()

	@classmethod
	def init(cls):
		cls._sysmem = dict()
		if not os.path.isdir(cls._groupspath):
			os.mkdir(cls._groupspath)
		for fname in os.listdir(cls._groupspath):
			if fname.startswith('.'):
				continue
			if not fname.endswith('.pickle'):
				continue
			d = Pickles.read(os.path.join(cls._groupspath, fname))
			try:
				id = int(d['id'])
				cls._sysmem[id] = d
			except:
				continue

	@classmethod
	def make_group(cls, id: int, d) -> bool:
		naam = Casting.name_safe(d['name'], True)
		pad = os.path.join(cls._groupspath, f"{id}-{naam}.pickle")
		if Pickles.write(pad, d):
			cls.init()
			return True
		return False

	@classmethod
	def get_active(cls):
		uit = list()
		for groep in cls._sysmem.values():
			print(groep)
			if groep['status'] != 1:
				continue
			uit.append(groep)
		return uit

Groups.init()
'''

'''
class Students:
	_stud_p_path = os.path.join(Props.get_od_path(), '_DATABASE', 'students')
	_stud_dir_path = os.path.join(Props.get_od_path(), 'JAREN')
	_sysmem = dict()

	@classmethod
	def init(cls):
		cls._sysmem = dict()
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
		return deepcopy(cls._sysmem)

	@classmethod
	def all_as_lod(cls):
		all = cls.all()
		return list(all.values())

	@classmethod
	def get_by_id(cls, id: int) -> dict|None:
		try:
			return deepcopy(cls._sysmem[id])
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
	def generate_safename(cls, id: int) -> str:
		return f"{id}"

	@classmethod
	def generate_safename_full(cls, id: int) -> str|None:
		d = cls.get_by_id(id)
		if d is None:
			return None
		return cls.generate_safename_full_from_d(d)

	@classmethod
	def generate_safename_full_from_d(cls, d: dict) -> str:
		first = Casting.name_safe(d['firstname'], False)
		last = Casting.name_safe(d['lastname'], False)
		return f"{d['id']}-{first}-{last}"

	@classmethod
	def make_student_pickle(cls, id: int, d) -> bool:
		try:
			ppath = os.path.join(cls._stud_p_path, f"{cls.generate_safename(id)}.pickle")
			Pickles.write(ppath, d)
			cls.init()
		except Exception as e:
			return False
		return True

	@classmethod
	def delete_student_pickle(cls, id: int) -> bool:
		try:
			ppath = os.path.join(cls._stud_p_path, f"{cls.generate_safename(id)}.pickle")
			Pickles.delete(ppath)
		except Exception as e:
			return False
		cls.init()
		return True

	@classmethod
	def make_student_folder_path(cls, id):
		d = cls.get_by_id(id)
		if d is None:
			return None
		return cls.make_studend_folder_path_from_d(d)

	@classmethod
	def make_studend_folder_path_from_d(cls, d):
		if d['s_year'] < 2020:
			return None
		if not d['s_term'] in [1, 2, 3, 4, 5, 6]:
			return None
		jaar = Sysls.get_sysl_item('s_year', d['s_year'])['name']
		term = Sysls.get_sysl_item('s_term', d['s_term'])['name']
		safename = cls.generate_safename_full_from_d(d)
		studpath = os.path.join(cls._stud_dir_path, jaar, term, safename)
		return studpath

	@classmethod
	def make_student_folder(cls, id: int) -> bool:
		d = cls.get_by_id(id)
		try:
			studpath = cls.make_student_folder_path(id)
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

	@classmethod
	def move_student_folder(cls, oldpath, curpath):
		shutil.move(oldpath, curpath)

	@classmethod
	def new_password(cls, id):
		x = ''.join(random.choices(string.ascii_lowercase, k=6))
		return f"{id}-{x}"

	@classmethod
	def new_student_id(cls):
		newid = 0
		for i in cls._sysmem:
			if newid < i:
				newid = i
		return newid + 1

	@classmethod
	def as_html(cls, id):
		# print(sys._getframe(1).f_code.co_name)
		d = cls.get_by_id(id)
		studfields = list(d.keys())
		circfields = Sysls.get_sysl('s_circular')

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
				return Sysls.get_sysl_item(thing, d[thing])['name']
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
		if d['s_status'] in [39]: # passed
			kleur = 'dodgerblue'
		elif d['s_status'] in [10, 11, 12]: # ingeschreven
			kleur = 'rgb(254, 232, 86)' # geel
		elif d['s_status'] in [20, 21, 22]: # bezig
			kleur = 'darkgreen'
		elif d['s_status'] in [30, 31, 38]: # gezakt oid
			kleur = 'rgb(221, 53, 110)' # signaal
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
		filename = cls.generate_safename_full_from_d(d)+'.html'
		dirpath = cls.make_studend_folder_path_from_d(d)
		filepath = os.path.join(dirpath, filename)
		with open(filepath, 'w') as f:
			f.write(html)

Students.init()
'''

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