# groepen
from flask import current_app, redirect, request, Blueprint, render_template

from helpers.general import Casting, Timetools, IOstuff, ListDicts

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
	sta, fil, tel, act = filter_stuff()
	filter = ''

	# groepen
	sysls_o = current_app.config['Sysls']
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
		students_o = current_app.config['Students']
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
	views_o = current_app.config['Views']
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
		props=current_app.config['Props'],
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
def studenten_groep_post(groepnr, viewname):
	if not IOstuff.check_required_keys(request.form, ['what', 'field-name', 'field-value', 'student-id']):
		return redirect(f"/groepen/{groepnr}/{viewname}")

	print(request.form)

	cc = 'circulars' #avoid typoos
	id = Casting.int_(request.form['student-id'], 0)
	field = Casting.str_(request.form['field-name'], '')
	what = Casting.str_(request.form['what'], '')

	students_o = current_app.config['Students']
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
		cirval = Casting.int_(request.form['field-value'], 0)
		if cirval < 3:
			cirval += 1
		else:
			cirval = 0
		cirname = field

		print(viewname, cirname, cirval)

		if not cc in student:
			student[cc] = {viewname: {cirname: cirval}}
		if not viewname in student[cc]:
			student[cc][viewname] = {cirname: cirval}
		if not cirname in student[cc][viewname]:
			student[cc][viewname][cirname] = cirval
		else:
			student[cc][viewname][cirname] = cirval
		print(student[cc])

	students_o.make_student_pickle(id, student)
	# eventualy fix student dir issues
	# fix_student_dir(id, student, student)
	return redirect(f"/groepen/{groepnr}/{viewname}")




