import re
import os
from copy import deepcopy
import webbrowser
from pprint import pprint as ppp
from flask import redirect, request, Blueprint, render_template

from helpers.general import Casting, Timetools, IOstuff, ListDicts, JINJAstuff, BaseClass
from helpers.singletons import UserSettings, Sysls, Students, Emails

# handles one student
class Student(BaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			# about the student - per enrollment. So enroll twice, twice in database
			id = {'default': 0},
			firstname = {'default': ''},
			lastname = {'default': ''},
			s_gender={'default': 0, 'from': 's_gender'},
			email = {'default': ''},
			created_ts = {'default': 0},
			pf_url = {'default': ''},
			kom_code = {'default': ''}, # student code for KOM students (other school)
			nhls_code = {'default': 0}, # student code at nhlstenden also for KOM
			password = {'default': ''},
			grade = {'default': 0},
			grade_ts = {'default': 0},

			s_group = {'default': 0, 'from': 's_group'},
			s_status = {'default': 0, 'from': 's_status'},

			# about the students current situation
			s_origin = {'default': 0, 'from': 's_origin'},
			s_uni = {'default': 0, 'from': 's_uni'},
			s_program = {'default': 0, 'from': 's_program'},

			# about the students minor course
			s_year = {'default': 0, 'from': 's_year'},
			s_term = {'default': 0, 'from': 's_term'},
			s_lang = {'default': 0, 'from': 's_lang'},
			s_ec = {'default': 0, 'from': 's_ec'},
			s_course = {'default': 0, 'from': 's_course'},
			s_stream = {'default': 0, 'from': 's_stream'},
			# see also
			samestudent={'default': []},  # llist with ids of same student

			# list of notes models
			notes = {'default': [], 'model': 'm_note'},

			# list of soc's on this student
			circulars = {'default': {}, 'model': 'm_setofcirculars'},

			# list of custom text fields
			customs = {'default': {}, 'model': 'm_custom'},
		)

	@classmethod
	def get_nicename(cls, key: str) -> str:
		nicenames = dict(
			s_group='group',
			s_status='status',
			s_year='year',
			s_term='period',
			s_ec='ecs',
			s_lang='lang',
			s_course='minor',
			s_stream='stream',
			s_origin='origin',
			s_uni='institute',
			s_program='program',
			created_ts='created',
			grade_ts='dd',
			s_gender='mfo',
		)
		if key in nicenames:
			return nicenames[key]
		return key

# handles a note for a student
class Note(BaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			note = {'default': ''},
			alias = {'default': ''}, # teacher
			created_ts = {'default': 0},
			done = {'default': 0},
		)

class  StudentJinja(JINJAstuff):
	def _s_item(self, lijstnaam: str) -> dict:
		sysls_o = Sysls()
		empty: dict = sysls_o.get_empty()
		key = self._try(lijstnaam, default=None)
		if key is None:
			return empty

		# get item from s_lijsten
		item = sysls_o.get_sysl_item(lijstnaam, key)
		if item is None:
			return empty

		# and normalize
		for thing in item:
			if thing in empty:
				empty[thing] = item[thing]
		return empty

	def _try_l(self, key, default: any = '', field='naam') -> any:
		# tries to get value from connected Lijst, if not, default or fallback
		val = self._try(key, default=None)
		if self.model is None or val is None:
			return default

		try:
			sysl = self.model[key]['from']
		except:
			return default

		if isinstance(sysl, list):
			# from is a list in the model, so single value in r
			return val
		if not isinstance(val, list):
			# single value, should be list
			return val

		if field == 'naam':
			try:
				return val[1]  # fallback
			except:
				return default

		return default


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

	def _circular(self, vname: str, cname: str) -> int:
		try:
			circ = self.record['circulars'][vname][cname]
			return circ
		except:
			return 0

	def _custom(self, vname: str, cname: str) -> str:
		try:
			custom = self.record['customs'][vname][cname]
			return custom
		except:
			return ''

	def _same(self) -> str:
		ss = self._try('samestudent', default=[])
		sss = ', '.join(map(str, ss))
		return sss


# =============== ENDPOINTS =====================
ep_studenten = Blueprint(
	'ep_studenten', __name__,
	url_prefix="/studenten",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

menuitem = 'studenten'

@ep_studenten.get('/<path:filter>')
@ep_studenten.get('/')
def studenten(filter='studenten'):
	students_o = Students()
	# get and set filter
	sta, fil, tel, act = filter_stuff()
	if not filter in sta:
		return redirect('/studenten/studenten')

	all = students_o.all_as_lod()

	students = list()
	tellers = dict()
	for s in all:
		if not s['s_status'] in sta[filter]:
			continue
		s['filter'] = get_student_filter(s, sta)
		s['todo'] = 0
		for n in s['notes']:
			if n['done'] == 0:
				s['todo'] = 1
				break
		students.append(StudentJinja(s, Student.get_model()))
	del(all)

	groepmenu = filter in ['registratie', 'studenten', 'beoordelen']
	sysls_o = Sysls()

	return render_template(
		'studenten.html',
		menuitem=menuitem,
		groepmenu=groepmenu,
		props=UserSettings(),
		students=students,
		filter=filter,
		filters=fil,
		tellers=tel,
		actiefstats=act,
		zoekterm=None,
		sysls=sysls_o.get(),
	)

@ep_studenten.get('/zoek')
def studenten_zoek():
	jus = UserSettings()
	try:
		zoekterm = Casting.str_(request.args.get('s'), '')
	except:
		zoekterm = ''
	if zoekterm == '':
		return redirect(jus.get_prop('last_url', default='/home'))

	students_o = Students()
	all = students_o.all_as_lod()
	gevonden = list()
	for a in all:
		if re.search(zoekterm, f"{a['firstname']} {a['lastname']} {a['email']}", re.IGNORECASE):
			gevonden.append(a)

	if len(gevonden) == 0:
		return redirect(jus.get_prop('last_url', default='/home'))

	sta, fil, tel, act = filter_stuff()
	groepmenu = filter in ['registratie', 'studenten', 'beoordelen']

	students = list()
	for s in gevonden:
		s['filter'] = get_student_filter(s, sta)
		s['todo'] = 0
		for n in s['notes']:
			if n['done'] == 0:
				s['todo'] = 1
				break
		students.append(StudentJinja(s, Student.get_model()))

	sysls_o = Sysls()

	if len(students) > 0:
		searchterms = jus.add_searchterm(zoekterm)
		# we have search results. add search term to user settings.

	return render_template(
		'studenten.html',
		menuitem=menuitem,
		groepmenu=groepmenu,
		props=jus,
		students=students,
		filter='alle',
		filters=fil,
		tellers=tel,
		actiefstats=act,
		zoekterm=zoekterm,
		sysls=sysls_o.get(),
	)

@ep_studenten.post('/collectief')
def collectief_post():
	jus = UserSettings()
	if not IOstuff.check_required_keys(request.form, ['col-ids', 'to-group', 'to-status', 'save']):
		return redirect(jus.get_prop('last_url', default='/home'))

	try:
		ids = list(request.form.get('col-ids').split(','))
		for i in range(len(ids)):
			ids[i] = Casting.int_(ids[i], 0)
	except:
		return redirect(jus.get_prop('last_url', default='/home'))

	s_group = Casting.int_(request.form.get('to-group'), 0)
	s_status = Casting.int_(request.form.get('to-status'), 0)

	students_o = Students()
	for id in ids:
		student = students_o.get_by_id(id)
		if student is None:
			continue
		newstudent = deepcopy(student)
		if s_status > 0:
			newstudent['s_status'] = s_status
		if s_group > 0:
			newstudent['s_group'] = s_group
		students_o.make_student_pickle(id, newstudent)
		fix_student_dir(id, student, newstudent)

	return redirect(jus.get_prop('last_url', default='/home'))

@ep_studenten.get('/single/<int:id>')
def single_get(id):
	students_o = Students()
	statussen = get_statussen()
	student = students_o.get_by_id(id)
	if student is None:
		return redirect('/studenten/studenten')

	student['filter'] = get_student_filter(student, statussen)
	student['notes'] = ListDicts.sortlistofdicts(student['notes'], 'created_ts', reverse=True)

	invite = None
	if student['s_status'] == 10: # listed
		invite = create_mail(student, 'confirm')

	grade = None
	if student['s_status'] == 21:
		grade = create_mail(student, 'grade')

	pad = students_o.make_student_folder_path(id)
	sysls_o = Sysls()

	return render_template(
		'student.html',
		menuitem=menuitem,
		props=UserSettings(),
		lijsten=sysls_o.get_lijsten_nicename(),
		sysls=sysls_o.get(),
		student=StudentJinja(student, Student.get_model()),
		nieuw=False,
		invite=invite,
		grade=grade,
		studmappad=pad,
	)

@ep_studenten.get('/new')
def single_new_get():
	students_o = Students()
	id = students_o.new_student_id()
	statussen = get_statussen()
	student = Student.get_empty()
	student['filter'] = 'registratie'
	student['id'] = id
	student['s_status'] = 10

	# TODO zelfde als bij vorige
	student['s_origin'] = 2
	sysls_o = Sysls()

	return render_template(
		'student.html',
		menuitem=menuitem,
		props=UserSettings(),
		lijsten=sysls_o.get_lijsten_nicename(),
		sysls=sysls_o.get(),
		student=StudentJinja(student, Student.get_model()),
		nieuw=True,
	)

@ep_studenten.post('/new/<int:id>')
def single_new_post(id):
	students_o = Students()
	newstudent = crunch_student(Student.get_empty(), request.form)

	# prefil
	newstudent['id'] = id
	newstudent['created_ts'] = Timetools.now_secs()
	newstudent['password'] = students_o.new_password(newstudent['created_ts'])
	if newstudent['s_origin'] == 1:
		newstudent['s_uni'] = 1
	# opslaan
	students_o.make_student_pickle(id, newstudent)
	# make student dir
	fix_student_dir(id, None, newstudent)
	# show student dir
	students_o.open_student_dir(id)
	return redirect(f"/studenten/single/{id}")

@ep_studenten.post('/single/<int:id>')
def single_edit_post(id):
	students_o = Students()
	student = students_o.get_by_id(id)
	if student is None:
		return redirect('/studenten/new')

	if 'save' in request.form:
		edited = crunch_student(deepcopy(student), request.form)
		students_o.make_student_pickle(id, edited)

		# eventualy fix student dir issues
		fix_student_dir(id, student, edited)
		return redirect(f"/studenten/single/{id}")

	elif 'delete' in request.form:
		# on delete show student folder
		students_o.open_student_dir(id)
		students_o.delete_student_pickle(id)

	elif 'kopieer' in request.form:
		# make empty copy of student
		kopie = Student.get_empty()
		kopie['created_ts'] = Timetools.now_secs()
		kopie['email'] = student['email']
		kopie['firstname'] = student['firstname']
		kopie['lastname'] = student['lastname']
		kopie['s_gender'] = student['s_gender']
		kopie['s_lang'] = student['s_lang']
		kopie['s_origin'] = student['s_origin']
		kopie['s_program'] = student['s_program']
		kopie['s_uni'] = student['s_uni']
		# dit moet worden aangepast door user
		kopie['s_year'] = student['s_year']
		kopie['s_term'] = student['s_term']
		kopie['password'] = students_o.new_password(kopie['created_ts'])
		kopie['id'] = students_o.new_student_id()
		# this is same student
		kopie['samestudent'] = student['samestudent']
		kopie['samestudent'].append(id)
		# get current year
		print('kopieer')
		# opslaan
		students_o.make_student_pickle(kopie['id'], kopie)
		# make dir
		fix_student_dir(kopie['id'], None, kopie)
		# show student dir
		students_o.open_student_dir(kopie['id'])
		return redirect(f"/studenten/single/{kopie['id']}")

	return redirect(f"/studenten/registratie")

@ep_studenten.post('/note/<int:id>')
def note_new_post(id):
	jus = UserSettings()
	students_o = Students()

	note = request.form.get('note').replace('\r\n', '<br>')
	if note == '':
		return redirect(f"/studenten/single/{id}")

	nu = Timetools.now_secs()
	student = students_o.get_by_id(id)
	student['notes'] = ListDicts.sortlistofdicts(student['notes'], 'created_ts', reverse=True)
	d = dict(
		note=note,
		created_ts=nu,
		alias=jus.alias(),
		done=0,
	)
	student['notes'].insert(0, d)
	students_o.make_student_pickle(id, student)
	return redirect(f"/studenten/single/{id}")

@ep_studenten.post('/note/<int:id>/<int:noteid>')
def note_post_done(id, noteid):
	students_o = Students()
	student = students_o.get_by_id(id)
	index = -1
	for i in range(len(student['notes'])):
		if noteid == student['notes'][i]['created_ts']:
			index = i
			break
	if index == -1:
		return redirect(f"/studenten/single/{id}")

	if 'delete' in request.form:
		student['notes'].pop(index)
	else:
		if 'done' in request.form:
			student['notes'][index]['done'] = 0
		else:
			student['notes'][index]['done'] = 1
	students_o.make_student_pickle(id, student)
	return redirect(f"/studenten/single/{id}")

@ep_studenten.get('/opendir/<int:id>')
def single_opendir(id):
	students_o = Students()
	students_o.open_student_dir(id)
	return redirect(f"/studenten/single/{id}")

@ep_studenten.get('/import')
def import_get():
	sysls_o = Sysls()
	preset = dict(
		s_status = 10,
		s_origin = 1,
		s_year = sysls_o.get_sysl_item_first_active('s_year')['id'],
		s_term = sysls_o.get_sysl_item_first_active('s_term')['id'],
		s_course = sysls_o.get_sysl_item_first_active('s_course')['id'],
		s_uni = 1,
		s_program = 0,
		sep = 'komma',
		volgorde = ['nhls_code', 'lastname', 'firstname', 'email'],
		csv = '',
	)
	seps = dict(
		puntkomma = ';',
		tab = '\t',
	)
	return render_template(
		'studenten-import.html',
		menuitem=menuitem,
		props=UserSettings(),
		sysls=sysls_o.get(),
		preset=preset,
		seps=list(seps.keys()),
		rows=None,
	)

@ep_studenten.post('/import')
def import_post():
	# this function translates form input into
	# a correct import list of dicts
	seps = dict(
		puntkomma = ';',
		tab = '\t',
	)
	try:
		d = dict(
			s_status = Casting.int_(request.form.get('s_status'), 0),
			s_origin = Casting.int_(request.form.get('s_origin'), 0),
			s_year = Casting.int_(request.form.get('s_year'), 0),
			s_term = Casting.int_(request.form.get('s_term'), 0),
			s_course = Casting.int_(request.form.get('s_course'), 0),
			volgorde = request.form.get('placeholders').split(','),
		)
	except Exception as e:
		print(e)
		return redirect('/studenten/import')

	if 's_uni' in request.form:
		d['s_uni'] = Casting.int_(request.form.get('s_uni'), 0)

	if 's_program' in request.form:
		d['s_program'] = Casting.int_(request.form.get('s_program'), 0)

	if d['s_course'] == 3:
		d['s_ec'] = 30
	else:
		d['s_ec'] = 15
	if 'sep' in request.form and 'sep' in seps.keys():
		d['sep'] = request.form.get('sep').strip()
	else:
		d['sep'] = 'puntkomma'
	d['sep'] = seps[d['sep']]

	try:
		d['csv'] = request.form.get('csv')
		d['csv_lines'] = d['csv'].split('\r\n')
	except Exception as e:
		print(e)
		return redirect('/studenten/import')

	rows = list()
	for row in d['csv_lines']:
		student = dict()
		csv = row.split(d['sep'])

		i = 0
		for key in d['volgorde']:
			try:
				student[key] = csv[i].strip()
			except:
				student[key] = ''
			if key == 'lastname':
				student['lastname'] = student['lastname'].split(',')[0].strip()
			i += 1

		for key in d:
			if not key.startswith('s_'):
				continue
			student[key] = d[key]

		if 'import' in request.form:
			rows.append(student)
		else:
			rows.append(StudentJinja(student, Student.get_model()))

	students_o = Students()
	if 'import' in request.form:
		# importeren en door naar registraties
		for newstudent in rows:
			id = students_o.new_student_id()
			newstudent['id'] = id
			newstudent['created_ts'] = Timetools.now_secs()
			newstudent['password'] = students_o.new_password(newstudent['created_ts'])

			newstudent = crunch_student({}, newstudent)
			# opslaan
			students_o.make_student_pickle(id, newstudent)
			# make student dir
			fix_student_dir(id, None, newstudent)
		return redirect(f"/studenten/registratie")

	sysls_o = Sysls()

	return render_template(
		'studenten-import.html',
		menuitem=menuitem,
		props=UserSettings(),
		sysls=sysls_o.get(),
		seps=list(seps.keys()),
		rows=rows,
		preset=d,
	)

@ep_studenten.get('/invite-mail/<int:id>')
def invite_mail(id):
	students_o = Students()
	statussen = get_statussen()
	student = students_o.get_by_id(id)
	if student is None:
		return redirect('/studenten/studenten')

	if student['s_status'] != 10: # listed
		return redirect(f'/studenten/single/{id}')

	invite = create_mail(student, 'confirm')
	body = invite['text']
	body = body.replace('<br>', "\n")
	urimail = f"mailto:{student['email']}?subject={invite['subject']}&body={body}";
	webbrowser.open(urimail)
	student['s_status'] = 11
	students_o.make_student_pickle(id, student)
	return redirect(f'/studenten/single/{id}')

@ep_studenten.get('/graded-mail/<int:id>')
def graded_mail(id):
	students_o = Students()
	statussen = get_statussen()
	student = students_o.get_by_id(id)
	if student is None:
		return redirect('/studenten/studenten')

	if student['s_status'] == 21:
		return redirect(f'/studenten/single/{id}')

	graded = create_mail(student, 'grade')
	body = graded['text']
	body = body.replace('<br>', "\n")
	urimail = f"mailto:{student['email']}?subject={graded['subject']}&body={body}";
	webbrowser.open(urimail)
	if student['grade'] >= 55:
		student['s_status'] = 39
	else:
		student['s_status'] = 38
	students_o.make_student_pickle(id, student)
	return redirect(f'/studenten/single/{id}')

# =========== helpers ========
def fix_student_dir(id: int, old: dict|None, current: dict):
	students_o = Students()
	# fixes problems with dirs, not delete = manual
	if current is None:
		return

	if old is None:
		oldpath = None
	else:
		oldpath = students_o.make_studend_folder_path_from_d(old)
	curpath = students_o.make_studend_folder_path_from_d(current)
	if curpath is None:
		return

	if oldpath is None:
		# new dir
		students_o.make_student_folder(id)
		students_o.as_html(id)
		return

	# if name not changed
	elif oldpath == curpath:
		# check if dir exists
		if os.path.isdir(curpath):
			students_o.as_html(id)
		else:
			students_o.make_student_folder(id)
			students_o.as_html(id)
			students_o.open_student_dir(id)
		return

	else:
		# cur path changed from old path, so rename or move
		students_o.move_student_folder(oldpath, curpath)
		students_o.as_html(id)
		return

def get_student_filter(s, sta):
	for st in sta:
		if s['s_status'] in sta[st]:
			return st
	return ''

def from_sysl(veld, d: dict):
	sysls_o = Sysls()
	try:
		return sysls_o.get_sysl_item(veld, d[veld])['name']
	except:
		return ''

def from_student(veld, d: dict):
	try:
		return d[veld]
	except:
		return ''

def create_mail(student, welk) -> dict:
	# create confirm text
	emails_o = Emails()
	mail = emails_o.get_single(welk)
	lang = from_sysl('s_lang', student)
	if lang == 'nl':
		text = mail['nl_text'].replace('\n', '<br>')
		subject = mail['nl_subject']
	elif lang == 'en':
		text = mail['en_text'].replace('\n', '<br>')
		subject = mail['en_subject']
	else:
		return dict()
	email = dict(
		naam=f"{from_student('firstname', student)} {from_student('lastname', student)}",
		minor=from_sysl('s_course', student),
		periode=from_sysl('s_term', student),
		jaar=from_sysl('s_year', student),
		ec=from_sysl('s_ec', student),
		cijfer=from_student('grade', student),
		wachtwoord=from_student('password', student),
		subject=subject,
	)
	email['text'] = text.format(
		name=email['naam'],
		minor=email['minor'],
		period=email['periode'],
		year=email['jaar'],
		ec=email['ec'],
		grade=round(email['cijfer'] / 10.0, 0),
		password=email['wachtwoord']
	)
	return email

def get_statussen():
	return dict(
		registratie=[0, 10, 11, 12],
		studenten=[20],
		beoordelen=[21, 22],
		alumni=[39],
		niet=[30, 31, 38],
		noshow=[14, 16, 18],
		alle=list(range(0, 100)),
	)

def filter_stuff():
	students_o = Students()
	statussen = get_statussen()
	filters = ['registratie', 'studenten', 'beoordelen', 'alumni', 'niet', 'noshow', 'alle']
	# behoort bij het main filter filternames()
	tellers = dict()
	all = students_o.all_as_lod()
	for s in all:
		for f in statussen:
			if s['s_status'] in statussen[f]:
				if not f in tellers:
					tellers[f] = 1
				else:
					tellers[f] += 1
	actiefstats = [0, 10, 11, 12, 20, 21, 22]
	return statussen, filters, tellers, actiefstats

def crunch_student(s, req):
	empty = Student.get_empty()
	newstudent = dict()

	# only keys in model are welcome
	for key in req:
		if not key in empty.keys():
			continue
		if key == 'samestudent':
			ids = req[key].split(',')
			newstudent[key] = list()
			for iid in list(ids):
				iid = Casting.int_(iid, default=None)
				if iid is None:
					continue
				if iid < 1:
					continue
				newstudent[key].append(iid)
			newstudent[key] = sorted(newstudent[key])

		elif type(empty[key]) == str:
			newstudent[key] = Casting.str_(req[key], '')
		elif type(empty[key]) == int:
			newstudent[key] = Casting.int_(req[key], 0)
		else:
			newstudent[key] = req[key]

	if 'grade' in newstudent:
		if 'grade' in s:
			if newstudent['grade'] != s['grade']:
				# new grade
				if newstudent['grade'] == 0:
					newstudent['grade_ts'] = 0
				else:
					newstudent['grade_ts'] = Timetools.now_secs()
			else:
				newstudent['grade'] = s['grade']
		else:
			newstudent['grade'] = 0

	if 's_course' in newstudent:
		if newstudent['s_course'] == 1:
			newstudent['s_ec'] = 15
			newstudent['s_stream'] = 0
		elif newstudent['s_course'] == 3:
			newstudent['s_ec'] = 30

	# add current values
	for key in s.keys():
		if key in newstudent.keys():
			continue
		newstudent[key] = s[key]

	# add empty fields if not in form
	for key in empty.keys():
		if key in newstudent.keys():
			continue
		newstudent[key] = empty[key]

	# merged and normalized
	return newstudent


# en verder