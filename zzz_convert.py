from zzz_class_sqlite import Sqlite
from datetime import date, datetime
from helpers.general import Casting
def get_status_model():
	return {
		0: '--',
		10: 'listed',
		11: 'confirmed',
		12: 'invited',
		14: 'cancelled',
		16: 'no response',
		18: 'no-show',
		20: 'student',
		21: 'resit',
		22: 'extra',
		30: 'quit',
		31: 'na',
		38: 'failed',
		39: 'passed',
		40: 'other',
	}

def get_student_model() -> dict:
	return dict(
		id=0,
		firstname='',
		lastname='',
		email='',
		created_ts=0,
		todo=0,
		pf_url='',
		grade=0,
		grade_ts=0,
		s_course=0,
		s_ec=0,
		s_gender=3,
		s_grading=4,
		s_lang=3,
		s_origin=5,
		s_program=0,
		s_status=0,
		s_stream=1,
		s_term=7,
		s_uni=9,
		s_year=2024,
		g_group=0,
	)

def get_groep_model() -> dict:
	return dict(
		id = 0,
		name = '',
		color = '#ffffff',
		s_status = 0,
		s_year = 2024,
		s_term = 7,
		s_teacher = 6,
	)

def create_status_table():
	sql = '''
	CREATE TABLE IF NOT EXISTS nw_status (
	    id     INTEGER       PRIMARY KEY,
	    name   VARCHAR (255),
	    color  VARCHAR (255),
	    extra  VARCHAR (255),
	    status BOOLEAN       DEFAULT (true) 
	)
	WITHOUT ROWID;
'''
	# db connection
	sqlite = Sqlite()
	sqlite.create(sql)

	sql = '''
	INSERT INTO
		nw_status
	VALUES 
		(?, ?, '#ffffff', '', 1)	
'''
	for k, v in get_status_model().items():
		sqlite.create(sql, (k, v))

def autofill_year_table():
	sqlite = Sqlite()
	sql = '''
		INSERT INTO
			nw_year
		VALUES 
			(?, ?, '#ffffff', '', ?)	
	'''
	for y in range(2020, 2031):
		if y in range(2024, 2027):
			status = 1
		else:
			status = 0
		sqlite.create(sql, (y, str(y), status))

def make_student_table():
	sql = '''
CREATE TABLE IF NOT EXISTS nw_student (
    id              INTEGER PRIMARY KEY,
    firstname       VARCHAR (255),
    lastname        VARCHAR (255),
    email           VARCHAR (255),
    created_ts      BIGINT,
    todo            BOOLEAN DEFAULT 0,
    pf_url          VARCHAR (255),
    grade           INTEGER,
    grade_ts        BIGINT,
    s_course        INTEGER,
    s_ec            INTEGER,
    s_gender        INTEGER,
    s_grading       INTEGER,
    s_lang          INTEGER,
    s_origin        INTEGER,
    s_program       INTEGER,
    s_status        INTEGER,
    s_stream        INTEGER,
    s_term          INTEGER,
    s_uni           INTEGER,
    s_year          INTEGER,
    g_group         INTEGER);
'''
	sqlite = Sqlite()
	sqlite.create(sql)

# -------- conversie studenten ------------
def jaar_periode_2_ts(year: int, periode: int, plus4: bool) -> int:
	year = 2015
	if periode == 1:
		wnr = 46
	elif periode == 2:
		wnr = 5
	elif periode == 3:
		wnr = 16
	else:
		wnr = 28
	if plus4:
		wnr += 4
	d = date.fromisocalendar(year, wnr, 6)  # (year, week, day of week)
	dt = datetime(
		year=d.year,
		month=d.month,
		day=d.day,
		hour=12,
		minute=0,
		second=0
	)
	ts = int(dt.timestamp())
	return ts

def conversie_lang(lang: str) -> int:
	if lang == 'en':
		return 2
	else:
		return 1

def conversie_mvo(gender: str) -> int:
	if gender == 'm':
		return 1
	elif gender == 'v':
		return 2
	else:
		return 3

def conversie_grade(grade_oud):
	return int(grade_oud)

def conversie_grade_moment(moment_oud: str) -> (int, int):
	gremo = moment_oud.split('_')
	if len(gremo) != 3:
		return 4, -1

	year = int(gremo[0])
	period = int((gremo[1]).replace('p', ''))

	if 'first' in gremo[2]:
		gm = 1
	elif 'resit' in gremo[2]:
		gm = 2
	else:
		return 4, -1
	gts = jaar_periode_2_ts(year, period, gm==2)
	return gm, gts

def conversie_stu_sta(status_oud: int):
	convertlijst = {
		0: 0, # nothing yet

		121: 10, # listed
		125: 11, # confirmed
		128: 12,  # invited

		304: 14,  # cancelled
		305: 16,  # no response
		999: 18, # no-show after first week

		1: 20,  # student
		201: 21, # grading
		202: 22, # resit

		301: 30, # quit_notified

		203: 31, # NA
		399: 38, # failed
		402: 39, # passed

		120: 40,  # other
		306: 31,  # NA
	}
	if not status_oud in convertlijst.keys():
		return 40
	else:
		return convertlijst[status_oud]

def conversie_eentwee(eentwee: int) -> (int, int): # ec stream
	if eentwee in [6]:
		ec = 1
		stream = 1
	elif eentwee in [1, 2, 10]:
		ec = 15
		stream = 1
	elif eentwee in [3, 9]:
		ec = 30
		stream = 1
	elif eentwee in [12]:
		ec = 30
		stream = 2
	elif eentwee in [13]:
		ec = 30
		stream = 3
	else:
		ec = 1
		stream = 1
	return ec, stream

def conversie_startperiode(startperiode: str, eentwee: int) -> int:
	if eentwee in [1, 2, 10]:
		# 15 ec
		if int(startperiode) in [1, 2, 3, 4]:
			return int(startperiode) + 2
	elif eentwee in [3, 9, 12, 13]:
		# 30 ec
		if int(startperiode) in [1, 2]:
			# er zijn in het begin studenten in p2 en p4 gestart met 30 ec
			return 1
		elif int(startperiode) in [3, 4]:
			return 2
	return 7

def conversie_naam(naam) -> (str, str):
	nd = naam.split(' ')
	vn = nd[0]
	an = ' '.join(nd[1:])
	return vn, an

def db_datetime_2_ts(dt: str) -> int:
	dts = "%Y-%m-%d %H:%M:%S"
	try:
		return int(datetime.strptime(dt, dts).timestamp())
	except:
		return -1

def converteer_notes_per_student(dbcon: Sqlite, id: int) -> list:
	# called when making the pickle
	sql = """
	SELECT * FROM notes
	WHERE studenten_ID = ?
	ORDER BY aanmaak ASC
		"""
	notes = dbcon.read(sql, [id])
	newnotes = list()
	for n in notes:
		newnote = dict(
			note = n['note'],
			user_id = n['users_ID'],
			done = Casting.int_(n['done'], default=1),
			created_ts = db_datetime_2_ts(n['aanmaak']),
		)
		newnotes.append(newnote)
	return newnotes

def converteer_student(dbcon: Sqlite, student: dict):
	fnaam, anaam = conversie_naam(student['naam'])
	s_grade, grade_ts = conversie_grade_moment(student['grademomenten_ID'])
	ec, stream = conversie_eentwee(student['eentwee_ID'])

	news = dict(
		id = student['ID'],
		firstname = fnaam,
		lastname = anaam,
		email = student['email'],
		created_ts = db_datetime_2_ts(student['aanmaak']),
		todo = student['todo'],
		pf_url = student['portfolio_URL'],
		grade = student['grade'],
		grade_ts = grade_ts,
		s_course = student['eentwee_ID'],
		s_ec = ec,
		s_gender = conversie_mvo(student['mvo']),
		s_grading = s_grade,
		s_lang = conversie_lang(student['lang']),
		s_origin = student['herkomst_ID'],
		s_program = student['opleidingen_ID'],
		s_status = conversie_stu_sta(student['studentstatussen_ID']),
		s_stream = stream,
		s_term = conversie_startperiode(student['startperiode'], student['eentwee_ID']),
		s_uni = student['instituten_ID'],
		s_year = student['startjaar'],
		g_group = student['groepen_ID'],
	)
	sql = """
	INSERT INTO nw_student 
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	"""
	vals = [news[sub] for sub in news]
	dbcon.create(sql, vals)

def converteer_studenten():
	sqlite = Sqlite()
	alle = sqlite.read("SELECT * FROM studenten")
	for a in alle:
		converteer_student(sqlite, a)
# converteer_studenten()

def converteer_groep(dbcon: Sqlite, groep: dict):
	if groep['startperiode'] in [1, 2, 3, 4]:
		term = groep['startperiode'] + 2
	else:
		term = 0
	if '-nl' in groep['naam'].lower() or 'nl-' in groep['naam'].lower() :
		lang = 1
	elif '-en' in groep['naam'].lower() or 'en-' in groep['naam'].lower() :
		lang = 2
	else:
		lang = 3

	if int(groep['startjaar']) == 2023:
		if term == 5:
			sstatus = 20
			status = 0
		elif term == 6:
			sstatus = 20
			status = 0
		else:
			sstatus = 0
			status = 1
	elif int(groep['startjaar']) > 2024:
		sstatus = 10
		status = 0
	else:
		sstatus = 0
		status = 1

	newg = dict(
		id = groep['ID'],
		name = groep['naam'],
		color = groep['kleur'],
		s_status = sstatus,
		s_year = groep['startjaar'],
		s_term = term,
		s_lang = lang,
		s_user = 6,
		status = status,
	)
	sql = """
	INSERT INTO nw_groep
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
	"""
	vals = [newg[sub] for sub in newg]
	dbcon.create(sql, vals)

def converteer_groepen():
	sqlite = Sqlite()
	alle = sqlite.read("SELECT * FROM groepen")
	for a in alle:
		converteer_groep(sqlite, a)

# converteer_groepen()

# NU IS DE _DATABASE OMGEZET VAN OUDE NAAR NIEUWE STRUCTUUR
# VANAF HIER KAN DIT WORDEN OMGEZET IN PICKLES

from helpers.globalclasses import Sysls, Groups, Students

def nw_db_2_systempickles():
	sqlite = Sqlite()
	slijst = Sysls._sysls

	for syslname in slijst:
		nw = syslname.replace('s_', 'nw_')
		sql = f"SELECT * FROM {nw}"
		alle = sqlite.read(sql)
		ad = dict()
		for a in alle:
			ad[a['id']] = a

		Sysls.make_sysl(syslname, ad)

# nw_db_2_systempickles()

def nw_db_2_groepen():
	sqlite = Sqlite()
	alle = sqlite.read("SELECT * FROM nw_groep")
	for a in alle:
		id = int(a['id'])
		Groups.make_group(id, a)

# nw_db_2_groepen()





def nw_db_2_students():
	sqlite = Sqlite()
	studenten = sqlite.read("SELECT * FROM nw_student")
	for s in studenten:
		id = s['id']
		try:
			s['notes'] = converteer_notes_per_student(sqlite, id)
		except:
			s['notes'] = []
		Students.make_student_pickle(id, s)
		Students.make_student_folder(id, s)

# nw_db_2_students()


# ======== HET ENIGE WAT MOET GEBEUREN BIJ
# ======== LAATSTE RUN MET NIEUWE STUDENTEN ======
# mits groepen e.d. niet zijn aangepast

# verwijderen van nw_student
'''
make_student_table() # nieuwe studenttabel maken
converteer_studenten() # gebeurt binnen sqlite
nw_db_2_students()
'''


