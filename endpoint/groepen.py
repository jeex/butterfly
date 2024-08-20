# groepen
from flask import redirect, request, Blueprint, render_template

from helpers.general import Casting, Timetools, IOstuff, ListDicts
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

@ep_groepen.get('')
def tofilter():
	return redirect('/groepen/1010')

@ep_groepen.get('/<int:groepnr>/<path:viewname>')
@ep_groepen.get('/<int:groepnr>')
def studenten_groep(groepnr, viewname=''):
	jus = UserSettings()

	sta, fil, tel, act = filter_stuff()
	filter = ''

	# groepen
	sysls_o = Sysls()
	all = sysls_o.get_sysl('s_group')
	groepen = list()
	groep = None
	for g in ListDicts.sortlistofdicts(list(all.values()), 'ordering'):
		if g['id'] == groepnr:
			groep = g
		groepen.append(g)

	# studenten
	students = list()
	if not groep is None:
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
	else:
		pass

	allfieldnames = list(Student.get_empty().keys())

	# alle views bij deze groep
	views_o = Views()
	allviews = views_o.get()
	for v in list(allviews.keys()):
		if v == 'default':
			del(allviews[v])
			continue
		if not groepnr in allviews[v]['groups']:
			del(allviews[v])
			continue
		if viewname == '':
			viewname = v

	# deze view
	view = views_o.get_single(viewname)

	if view is None:
		view = views_o.empty_view()
		view['fields'] = allfieldnames
		view['color'] = '#000000'
	else:
		view['fields'].append('id')

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
		avs=allviews,
		view=view,
		mijngroepen=views_o.mijn_groepen(),
		viewname=viewname,
		afns=allfieldnames,
		circular=circular,
	)

@ep_groepen.post('/<int:groepnr>/<path:viewname>')
@ep_groepen.post('/<int:groepnr>')
def studenten_groep_post(groepnr, viewname=''):
	if not IOstuff.check_required_keys(request.form, ['what', 'field-name', 'field-value', 'student-id']):
		return redirect(f"/groepen/{groepnr}/{viewname}")

	cc = 'circulars' #avoid typoos
	cu = 'customs'

	id = Casting.int_(request.form['student-id'], 0)
	field = Casting.str_(request.form['field-name'], '')
	what = Casting.str_(request.form['what'], '')

	students_o = Students()
	student = students_o.get_by_id(id)

	if student is None:
		return redirect(f"/groepen/{groepnr}/{viewname}")

	if what == 'portfolio':
		fieldval = Casting.str_(request.form['field-value'], '')
		student['pf_url'] = fieldval

	if what == 'grade':
		fieldval = Casting.int_(request.form['field-value'], 0)
		student['grade'] = fieldval
		student['grade_ts'] = Timetools.now_secs()

	elif what == cc:
		# click on circular field
		cirval = Casting.int_(request.form['field-value'], 0)
		if cirval < 3:
			cirval += 1
		else:
			cirval = 0

		if not cc in student:
			student[cc] = {viewname: {field: cirval}}
		if not viewname in student[cc]:
			student[cc][viewname] = {field: cirval}
		if not field in student[cc][viewname]:
			student[cc][viewname][field] = cirval
		else:
			student[cc][viewname][field] = cirval

	elif what == cu:
		# edit in custom text fiel
		cusval = Casting.str_(request.form['field-value'], '')
		if not cu in student:
			student[cu] = {viewname: {field: cusval}}
		if not viewname in student[cu]:
			student[cu][viewname] = {field: cusval}
		if not field in student[cu][viewname]:
			student[cu][viewname][field] = cusval
		else:
			student[cu][viewname][field] = cusval

	students_o.make_student_pickle(id, student)
	# eventualy fix student dir issues
	# fix_student_dir(id, student, student)
	return redirect(f"/groepen/{groepnr}/{viewname}")




