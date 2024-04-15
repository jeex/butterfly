from flask import session, redirect, request, Blueprint, render_template

from helpers.helpers import Casting, Timetools, IOstuff, ListDicts

def get_student_model():
	return dict(
		id = {'default': 0},
		naam = {'default': ''},
		mvo = {'default': ['', ''], 'from': 'sys_gender'},
		email = {'default': ''},
		studentcode = {'default': ''},
		password = {'default': ''},
		aanmaakdatum = {'default': '0000-00-00 00:00:00'},
		studstatus = {'default': [0, ''], 'from': 'sys_status'},
		portfolio_url = {'default': ''},

		cijfer = {'default': ['', 0], 'from': 'sys_grade'}, # tweede vermelding is percentage oude grade
		cijferdatum = {'default': ['0000-00-00 00:00:00', '']}, # tweede vermelding is de oude grademoment_ID

		taal = {'default': ['', ''], 'from': 'sys_language'},
		startjaar = {'default': [0, ''], 'from': 'sys_year'},
		startperiode = {'default': [0, ''], 'from': 'sys_period'},
		credits = {'default': 0},

		instituut = {'default': [0, ''], 'from': 'sys_uni'},
		opleiding = {'default': [0, ''], 'from': 'sys_program'},
		module = {'default': [0, ''], 'from': 'sys_module'},
		variant = {'default': [0, ''], 'from': 'sys_variant'},
		herkomst = {'default': [0, ''], 'from': 'sys_origin'},
		groep = {'default': [0, ''], 'from': 'groups'},

		notities = {'default': [], 'model': 'model_notitie'},
		aanwezig = {'default': [], 'model': 'model_aanwezig'}, # aanwezigheid
		opdrachten = {'default': [], 'model': 'model_opdracht'}, # afvinken voltooide opdrachten
		controles = {'default': [], 'model': 'model_controle'}, # controles die docent uitvoert (portfolio en zo)
		toetsen = {'default': [], 'model': 'model_toets'}, # model_voortgangstoets met daarin model_antwoord
	)

def get_empty_student():
	m = get_student_model()
	newm = dict()
	for key, val in m.items():
		newm[key] = val['default']
	return newm

model_notitie = dict(
	notitie = {'default': ''},
	docent = {'default': [0, '']}, # user_ID en alias
	# student_id komt te vervallen want dict in student_dict
	# groepen_id vervallen
	afgehandeld = {'default': False},
	aanmaakdatum = {'default': '0000-00-00 00:00:00'},
)
def get_notitie_model():
	return model_notitie.copy()
def get_empty_notitie():
	m = model_notitie.copy()
	newm = dict()
	for key, val in m.items():
		newm[key] = val['default']
	return newm


model_toets = dict(
	start = {'default': '0000-00-00 00:00:00'},
	eind = {'default': '0000-00-00 00:00:00'},
	cijfer = {'default': '', 'from': ['o', 'v', 'u']},
	antwoorden = {'default': []},
)
def get_toets_model():
	return model_toets.copy()
def get_empty_toets():
	m = model_toets.copy()
	newm = dict()
	for key, val in m.items():
		newm[key] = val['default']
	return newm


model_opdracht  = dict(
	opdracht = {'default': 0}, # ID van de opdracht
	antwoord = {'default': ''}, # resultaat na uitvoeren van de opdracht
	cijfer = {'default': '', 'from': ['o', 'v']},
)
def get_opdracht_model():
	return model_opdracht.copy()
def get_empty_opdracht():
	m = model_opdracht.copy()
	newm = dict()
	for key, val in m.items():
		newm[key] = val['default']
	return newm


model_aanwezig = dict(
	datum = {'default': '0000-00-00 00:00:00'},
	present = {'default': 0, 'from': [0, 1, 2]}, # 0, 1, 2 = niet, afgemeld/half, wel
)
def get_aanwezig_model():
	return model_aanwezig.copy()
def get_empty_aanwezig():
	m = model_aanwezig.copy()
	newm = dict()
	for key, val in m.items():
		newm[key] = val['default']
	return newm


model_controle = dict(
	datum = {'default': '0000-00-00 00:00:00'},
	present = {'default': 0, 'from': [0, 1, 2]}, # 0, 1, 2 = niet, afgemeld/half, wel
)
def get_controle_model():
	return model_controle.copy()
def get_empty_controle():
	m = model_controle.copy()
	newm = dict()
	for key, val in m.items():
		newm[key] = val['default']
	return newm

class  StudendIo(IOstuff):
	def _grade(self):
		g = self._try('cijfer')
		try:
			if g[0] != '':
				return g[0]
			else:
				cijfer = g[1]
				if cijfer >= 10:
					return cijfer/10
				else:
					return f'{cijfer}'
		except:
			return g

	def _pfurl(self):
		g = self._try('portfolio_url').strip()
		if g == '':
			return ''
		else:
			return f'<a href="{g}" target="_blank">pf&rarr;</a>'










# =============== ENDPOINTS =====================
ep_studenten = Blueprint(
	'ep_studenten', __name__,
	url_prefix="/studenten",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

@ep_studenten.get('')
def home():
	return redirect('/studenten/stud')

@ep_studenten.get('/<filter>')
def studenten(filter='stud'):
	# get and set filter
	filters = dict(
		stud=[20, 22],
		reg=[0, 10, 11, 12],
		alumni=[29],
		failed=[24, 25, 27, 28],
		noshow=[14, 16, 18],
		all=list(range(0, 41)),
	)
	# f = ListDicts.get_from(request.args, 'filter')
	statussen = filters[filter]
	for arg in request.args:
		try:
			statussen = filters[arg]
			filter = arg
			break
		except:
			pass

	res = ContextStudent.find_students(filters={'studstatus.0': statussen})
	students = list()
	for s in res:
		ioo = StudendIo(s, get_student_model())
		students.append(ioo)
	del(res)

	return render_template(
		'studenten.html',
		auth=Auth,
		mainmenu='studenten',
		filter=filter,
		students=students,
	)

@ep_studenten.get('/groep/<int:groepnr>')
def studenten_groep(groepnr):
	statussen = [20, 22]
	res = ContextStudent.find_students(filters={'studstatus.0': statussen, 'groep.0': [groepnr]})
	students = list()
	for s in res:
		ioo = StudendIo(s, get_student_model())
		students.append(ioo)
	# del (m)

	return render_template(
		'studenten.html',
		auth=Auth,
		menu='studenten',
		filter=filter,
		students=students,
	)

@ep_studenten.get('/zoek')
def studenten_zoek():
	ioo = StudendIo(None, get_student_model())
	zoekterm = ioo.sanitize(request.args.get('student-zoek'))
	return zoekterm


@ep_studenten.get('/<int:id>')
def student(id=0):
	return f'studenten {id}'

@ep_studenten.get('/nieuw')
def student_nieuw():
	return f'nieuwe student'

