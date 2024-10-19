# groepen
from flask import redirect, request, Blueprint, render_template
from pprint import pprint as ppp
from helpers.general import Casting, Timetools, IOstuff, ListDicts, JINJAstuff
from helpers.singletons import UserSettings, Sysls, Students, Views

from endpoint.studenten import (
	Student,
	Note,
	StudentJinja,
	filter_stuff,
	get_student_filter,
	is_active_in_group,
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
	dezegroep = None
	for g in allegroepen:
		if g['status'] != 1:
			# active groups only
			continue
		if groepnr == 0:
			if g['id'] in mijngroepen:
				# redirect to first of my groups
				return redirect(f'/groepen/{g["id"]}')
		if g['id'] == groepnr:
			dezegroep = g
		groepen.append(g)

	if dezegroep is None:
		return redirect(f'/home')

	# views
	# get / set current viewid in usersettings
	# view other group, same setting.
	allfieldnames = list(Student.get_empty().keys())
	groupviews = views_o.get_views_by_groupid(groepnr, activeonly=True) # views_o.get()
	selectprimary = False

	# get view if current or previous
	previous_viewid = 0
	if viewid == 0:
		viewid = previous_viewid = jus.get_prop('viewid', default=0)
		view = views_o.get_single_by_key(viewid)
	else:
		view = views_o.get_single_by_key(viewid)

	# check if groep in view, gives False if viewid == 0
	if not views_o.is_group_in_view(groepnr, viewid):
		selectprimary = True
		viewid = 0
		view = None

	# if not preselected viewid yet
	if selectprimary:
		# first look for similar view
		if previous_viewid != 0:
			viewid = views_o.get_by_similar_viewname(groepnr, previous_viewid)
			if viewid > 0:
				# if found, redirect
				return redirect(f'/groepen/{groepnr}/{viewid}')

	# if not preselected viewid,
	if selectprimary:
		# redirect to first active or all
		for k, v in groupviews.items():
			if v['status'] == 1:
				return redirect(f'/groepen/{groepnr}/{k}')
		return redirect(f'/groepen/{groepnr}/1')

	# set current viewid if not ALL
	if viewid > 1:
		jus.set_prop('viewid', viewid)

	# get the view, if 1
	if view is None:
		# make view empty with all fields
		view = views_o.empty_view()
		view['fields'] = allfieldnames
	view['fields'].append('id')

	# normalize view
	views_o.void_normalize(view)

	# jinjafy
	for key in list(groupviews.keys()):
		# del default view, not to be shown or used
		if key == views_o.get_defaultkey():
			del (groupviews[key])
			continue
		groupviews[key] = JINJAstuff(groupviews[key], {})

	# append nice names to view
	view['nicenames'] = dict()
	for f in view['fields']:
		view['nicenames'][f] = Student.get_nicename(f)

	# studenten
	students = list()
	students_o = Students()
	students_o.init()
	all = students_o.all_as_lod()
	for s in all:
		# filter on this group
		if not s['s_group'] == groepnr:
			continue
		# alleen als registratie, student of grading
		if not is_active_in_group(s, sta):
			continue
		s['filter'] = get_student_filter(s, sta)
		s['todo'] = 0
		for n in s['notes']:
			if n['done'] == 0:
				s['todo'] = 1
				break
		students.append(StudentJinja(s, Student.get_model()))
	del (all)

	if 'notes' in dezegroep:
		dezegroep['notes'].reverse()
	circular = sysls_o.get_sysl('s_circular')

	return render_template(
		'groep-studenten.html',
		menuitem=menuitem,
		props=jus,
		students=students,
		groepen=groepen,
		groep=dezegroep,
		filter=filter,
		filters=fil,
		tellers=tel,
		actiefstats=act,
		sysls=sysls_o.get(),
		allviews=groupviews,
		view=view,
		mijngroepen=mijngroepen,
		viewid=viewid,
		afns=allfieldnames,
		circular=circular,
	)

'''
@ep_groepen.post('/<int:groepnr>/<int:viewid>')
@ep_groepen.post('/<int:groepnr>')
def studenten_groep_post(groepnr, viewid=0):
	camefrom = request.referrer.split('?')[0]
	if 'sort-field' in request.form and 'sort-dir' in request.form:
		sf = request.form['sort-field']
		sd = request.form['sort-dir']
	else:
		sf = 'firstname'
		sd = 'asc'
	camefrom = f"{camefrom}?sort-field={sf}&sort-dir={sd}"

	if not IOstuff.check_required_keys(request.form, ['what', 'field-name', 'field-value', 'student-id']):
		return redirect(f"/groepen/{groepnr}/{viewid}")

	cc = 'circulars' #avoid typoos
	cu = 'customs'

	id = Casting.int_(request.form['student-id'], 0)
	field = Casting.str_(request.form['field-name'], '')
	what = Casting.str_(request.form['what'], '')

	students_o = Students()
	students_o.init()
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
	return redirect(camefrom)
'''

@ep_groepen.post('/noajax')
def noajax_post():
	camefrom = request.referrer.split('?')[0]
	if 'sort-field' in request.form and 'sort-dir' in request.form:
		sf = request.form['sort-field']
		sd = request.form['sort-dir']
	else:
		sf = 'firstname'
		sd = 'asc'
	camefrom = f"{camefrom}?sort-field={sf}&sort-dir={sd}"

	if not IOstuff.check_required_keys(request.form, ['what', 'field-name', 'field-value', 'student-id', 'view-id']):
		return redirect(camefrom)

	try:
		studid = Casting.int_(request.form['student-id'], default=None)
		fieldname = Casting.str_(request.form['field-name'], None)
		viewid = Casting.int_(request.form['view-id'], None)
		what = Casting.str_(request.form['what'], None)
	except:
		return redirect(camefrom)

	if studid is None or fieldname is None or viewid is None or what is None:
		return redirect(camefrom)

	cc = 'circulars'  # avoid typoos
	cu = 'customs'

	students_o = Students()
	students_o.init()
	student = students_o.get_by_id(studid)

	if student is None:
		return redirect(camefrom)

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
			student[cc] = {viewid: {fieldname: cirval}}
		if not viewid in student[cc]:
			student[cc][viewid] = {fieldname: cirval}
		if not fieldname in student[cc][viewid]:
			student[cc][viewid][fieldname] = cirval
		else:
			student[cc][viewid][fieldname] = cirval

	elif what == cu:
		# edit in custom text field
		cusval = Casting.str_(request.form['field-value'], '')
		if not cu in student:
			student[cu] = {viewid: {fieldname: cusval}}
		if not viewid in student[cu]:
			student[cu][viewid] = {fieldname: cusval}
		if not fieldname in student[cu][viewid]:
			student[cu][viewid][fieldname] = cusval
		else:
			student[cu][viewid][fieldname] = cusval

	students_o.make_student_pickle(studid, student)
	# eventualy fix student dir issues
	# fix_student_dir(id, student, student)
	return redirect(camefrom)

@ep_groepen.post('/asshole')
def asshole_post():
	camefrom = request.referrer.split('?')[0]
	if 'sort-field' in request.form and 'sort-dir' in request.form:
		sf = request.form['sort-field']
		sd = request.form['sort-dir']
	else:
		sf = 'firstname'
		sd = 'asc'
	camefrom = f"{camefrom}?sort-field={sf}&sort-dir={sd}"

	try:
		studid = Casting.int_(request.form['student-id'], default=None)
		asshole = Casting.int_(request.form['asshole-field'], default=None)
	except:
		return redirect(camefrom)

	if studid is None or asshole is None:
		return redirect(camefrom)

	students_o = Students()
	student = students_o.get_by_id(studid)

	if student is None:
		return redirect(camefrom)

	student['assessment'] = asshole
	students_o.make_student_pickle(studid, student)
	return redirect(camefrom)

@ep_groepen.post('/group-new-note/<int:groepnr>')
def group_new_note_post(groepnr):
	if not ('make-note' in request.form and 'new-note' in request.form):
		return redirect(request.referrer)

	note = Casting.str_(request.form['new-note'], '')
	if note == '':
		return redirect(request.referrer)

	sysl_o = Sysls()
	group = sysl_o.get_sysl_item('s_group', groepnr)
	if group is None:
		return redirect(request.referrer)

	jus = UserSettings()
	newnote = Note.get_empty()
	newnote['note'] = note
	newnote['alias'] = jus.alias()
	newnote['created_ts'] = Timetools.now_secs()
	newnote['done'] = 1
	# print(group)
	# print(newnote)
	if not 'notes' in group:
		group['notes'] = list()
	group['notes'].append(newnote)
	sysl_o.set_sysl_item('s_group', groepnr, group)
	return redirect(request.referrer)

@ep_groepen.post('/group-note/<int:groepnr>/<int:notenr>')
def groep_note_delete(groepnr, notenr):
	if not 'group-note-delete' in request.form:
		return redirect(request.referrer)

	sysl_o = Sysls()
	group = sysl_o.get_sysl_item('s_group', groepnr)
	if group is None:
		return redirect(request.referrer)
	if not 'notes' in group:
		return redirect(request.referrer)

	for note in list(group['notes']):
		if note['created_ts'] == notenr:
			group['notes'].remove(note)

	sysl_o.set_sysl_item('s_group', groepnr, group)
	return redirect(request.referrer)
