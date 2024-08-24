# groepen
from flask import redirect, request, Blueprint, render_template
from pprint import pprint as ppp
from helpers.general import Casting, Timetools, IOstuff, ListDicts, JINJAstuff
from helpers.singletons import UserSettings, Sysls, Students, Views

from endpoint.studenten import (
	Student,
	StudentJinja,
	filter_stuff,
	get_student_filter
)

# =============== ENDPOINTS =====================
ep_groepen = Blueprint(
	'ep_groepen', __name__,
	url_prefix="/groepen",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

menuitem = 'groepen'

@ep_groepen.get('/<int:groepnr>/<int:viewid>')
@ep_groepen.get('/<int:groepnr>')
@ep_groepen.get('')
def studenten_groep(groepnr=0, viewid=0):
	jus = UserSettings()
	sta, fil, tel, act = filter_stuff()
	filter = ''

	# groepnr
	sysls_o = Sysls()
	views_o = Views()
	mijngroepen = views_o.mijn_groepen()
	all = sysls_o.get_sysl('s_group')
	allegroepen = ListDicts.sortlistofdicts(list(all.values()), 'ordering')

	# groepen
	groepen = list()
	groep = None
	for g in allegroepen:
		if groepnr == 0:
			if g['id'] in mijngroepen:
				groepnr = g['id']
		if g['id'] == groepnr:
			groep = g
		groepen.append(g)

	# studenten
	students = list()
	if groep is None:
		pass
	else:
		students_o = Students()
		all = students_o.all_as_lod()
		for s in all:
			# filter on this group
			if not s['s_group'] == groepnr:
				continue
			s['filter'] = get_student_filter(s, sta)
			s['todo'] = 0
			for n in s['notes']:
				if n['done'] == 0:
					s['todo'] = 1
					break
			students.append(StudentJinja(s, Student.get_model()))
		del (all)

	allfieldnames = list(Student.get_empty().keys())

	# alle views bij deze groep
	view = views_o.get_single_by_key(viewid)
	allviews = views_o.get()
	selectprimary = viewid == 0
	for key in list(allviews.keys()):
		if key == views_o.get_defaultkey():
			del(allviews[key])
			continue

		if not groepnr in allviews[key]['groups']:
			del(allviews[key])
			continue

		if allviews[key]['status'] == 2 and selectprimary:
			viewid = key
			view = allviews[key]
			selectprimary = False

		if viewid == 0:
			viewid = key
			view = allviews[key]

		allviews[key] = JINJAstuff(allviews[key], {})

	if view is None:
		# make view empty with all fields
		view = views_o.empty_view()
		view['fields'] = allfieldnames
	else:
		# chosen view
		view['fields'].append('id')
	# append nice names to view
	view['nicenames'] = dict()
	for f in view['fields']:
		view['nicenames'][f] = Student.get_nicename(f)

	circular = sysls_o.get_sysl('s_circular')

	return render_template(
		'groep-studenten.html',
		menuitem=menuitem,
		props=jus,
		students=students,
		groepen=groepen,
		groep=groep,
		filter=filter,
		filters=fil,
		tellers=tel,
		actiefstats=act,
		sysls=sysls_o.get(),
		allviews=allviews,
		view=view,
		mijngroepen=mijngroepen,
		viewid=viewid,
		afns=allfieldnames,
		circular=circular,
	)

@ep_groepen.post('/<int:groepnr>/<int:viewid>')
@ep_groepen.post('/<int:groepnr>')
def studenten_groep_post(groepnr, viewid=0):
	if not IOstuff.check_required_keys(request.form, ['what', 'field-name', 'field-value', 'student-id']):
		return redirect(f"/groepen/{groepnr}/{viewid}")

	cc = 'circulars' #avoid typoos
	cu = 'customs'

	id = Casting.int_(request.form['student-id'], 0)
	field = Casting.str_(request.form['field-name'], '')
	what = Casting.str_(request.form['what'], '')

	students_o = Students()
	student = students_o.get_by_id(id)

	if student is None:
		return redirect(f"/groepen/{groepnr}/{viewid}")

	if what == 'portfolio':
		fieldval = Casting.str_(request.form['field-value'], '')
		student['pf_url'] = fieldval

	if what == 'grade':
		fieldval = Casting.int_(request.form['field-value'], 0)
		student['grade'] = fieldval
		if fieldval > 0:
			student['grade_ts'] = Timetools.now_secs()
		else:
			student['grade_ts'] = 0

	elif what == cc:
		# click on circular field
		cirval = Casting.int_(request.form['field-value'], 0)
		if cirval < 3:
			cirval += 1
		else:
			cirval = 0

		if not cc in student:
			student[cc] = {viewid: {field: cirval}}
		if not viewid in student[cc]:
			student[cc][viewid] = {field: cirval}
		if not field in student[cc][viewid]:
			student[cc][viewid][field] = cirval
		else:
			student[cc][viewid][field] = cirval

	elif what == cu:
		# edit in custom text fiel
		cusval = Casting.str_(request.form['field-value'], '')
		if not cu in student:
			student[cu] = {viewid: {field: cusval}}
		if not viewid in student[cu]:
			student[cu][viewid] = {field: cusval}
		if not field in student[cu][viewid]:
			student[cu][viewid][field] = cusval
		else:
			student[cu][viewid][field] = cusval

	students_o.make_student_pickle(id, student)
	# eventualy fix student dir issues
	# fix_student_dir(id, student, student)
	return redirect(f"/groepen/{groepnr}/{viewid}")




