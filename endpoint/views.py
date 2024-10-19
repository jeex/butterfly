# views
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
ep_views = Blueprint(
	'ep_views', __name__,
	url_prefix="/views",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

menuitem = 'views'

@ep_views.get('<int:viewid>')
@ep_views.get('')
def view_get(viewid=0):
	jus = UserSettings()
	sta, fil, tel, act = filter_stuff()

	sysls_o = Sysls()
	views_o = Views()

	# get all active views
	active_views = views_o.active_views()

	# get and check current view
	current_view = None
	if viewid > 0:
		current_view = views_o.get_single_by_key(viewid)
	# if no view_id get first own, or others
	if viewid == 0 or current_view is None:
		for v in active_views:
			if jus.alias() == v['alias']:
				current_view = v
				break
		if current_view is None:
			for v in active_views:
				current_view = v
				break
		if current_view is None:
			return redirect('/home')
		else:
			return redirect(f"/views/{current_view['created_ts']}")

	# at this point we have an active existing current_view
	views_o.void_normalize(current_view)

	# append nice names to view
	current_view['nicenames'] = dict()
	for f in current_view['fields']:
		current_view['nicenames'][f] = Student.get_nicename(f)

	# ppp(current_view)
	# get all groups in this view
	groupids = current_view['groups']
	groups = dict()
	for id in groupids:
		groups[id] = JINJAstuff(sysls_o.get_sysl_item('s_group', id), dict())

	# ppp(groups)
	# get all students in these groups
	students = list()
	students_o = Students()
	students_o.init()
	all = students_o.all_as_lod()
	for s in all:
		if not s['s_group'] in groupids:
			continue
		if not s['s_status'] in act:
			continue
		students.append(StudentJinja(s, Student.get_model()))
	del (all)

	default_fieldnames = list(Student.get_empty().keys())

	return render_template(
		'view-studenten.html',
		menuitem=menuitem,
		props=jus,
		students=students,
		groups=groups,
		allviews=active_views,
		view=current_view,
		viewid=viewid,
		sysls=sysls_o.get(),
		dfns=default_fieldnames,
		circular=sysls_o.get_sysl('s_circular'),
		filter='',
		actiefstats=act,
	)