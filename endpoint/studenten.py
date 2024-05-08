from flask import session, redirect, request, Blueprint, render_template

from helpers.general import Casting, Timetools, IOstuff, ListDicts, JINJAstuff

class StudentBaseClass:
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

# handles one student
class Student(StudentBaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			# about the student - per enrollment. So enroll twice, twice in database
			id = {'default': 0},
			firstname = {'default': ''},
			lastname = {'default': ''},
			email = {'default': ''},
			created_ts = {'default': 0},
			todo = {'default': 0},
			pf_url = {'default': ''},
			kom_code = {'default': ''}, # student code for KOM students (other school)
			nhls_code = {'default': 0}, # student code at nhlstenden also for KOM
			password={'default': ''},
			s_gender={'default': 0, 'from': 's_gender'},

			# about the students current situation
			s_origin = {'default': 0, 'from': 's_origin'},
			s_uni = {'default': 0, 'from': 's_uni'},
			s_program = {'default': 0, 'from': 's_program'},

			# about the students minor course
			s_year={'default': 0, 'from': 's_year'},
			s_term={'default': 0, 'from': 's_term'},
			s_lang={'default': 0, 'from': 's_lang'},
			s_ec={'default': 0, 'from': 's_ec'},
			s_course={'default': 0, 'from': 's_course'},
			s_stream={'default': 0, 'from': 's_stream'},

			# list of notes models
			m_notes = {'default': [], 'model': 'm_note'},

			# list of grading models moments, grades en timestamps
			m_gradings = {'default': [], 'model': 'm_grading'},

			# list of group models, groups, checks, timestamps
			m_groups = {'default': [], 'model': 'm_group'},

			# list of status models
			m_statusses = {'default': [], 'model': 'm_studentstatus'},

			# list of checks on this student
			circulars = {'default': [], 'model': 'm_setofcirculars'},
		)

# handles a note for a student
class Note(StudentBaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			note = {'default': ''},
			alias = {'default': ''}, # teacher
			created_ts = {'default': 0},
			todo = {'default': True},
			handeled_ts = {'default': 0},
		)

# handles one moment of grading for one student
class Grading(StudentBaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			s_grading = {'default': 0, 'from': 's_grading'},
			created_ts = {'default': 0},
			grade = {'default': 0},
			progress_ts = {'default': 0},
			alias = {'default': ''},
		)

# handles assignment of one student to a group
class Group(StudentBaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			s_group = {'default': 0, 'from': 's_group'},
			addedto_ts = {'default': 0}, # student placed in group
			alias = {'default': ''}, # by
		)

# handles single of many studentstatusses
class Studentstatus(StudentBaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			s_student = {'default': 0, 'from': 's_status'},
			addedto_ts = {'default': 0}, # status for student
			alias = {'default': ''}, # by
		)

# handles single check of many on student = one single field in a set of circulars
class Circular(StudentBaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			name = {'default': ''}, # description of the circular
			created_ts = {'default': 0},
			circular = {'default': 0, 'from': 's_circular'}, # one of the click colors: red orange green gray
			updated_ts = {'default': 0},
			alias = {''}, # teacher filling this
		)

class SetOfCirculars(StudentBaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			setname = {'default': ''},
			created_ts = {'default': 0},
			circulars = {'default': list()},
			updated_ts = {'default': 0},
			alias={''},  # teacher creating this
		)

class  StudendJinja(JINJAstuff):
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

