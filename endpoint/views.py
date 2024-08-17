from pprint import pprint as ppp
from flask import redirect, request, Blueprint, render_template
from helpers.general import Casting, Timetools, JINJAstuff, BaseClass
from endpoint.studenten import Student

from helpers.singletons import UserSettings, Sysls, Views

# VIEWS WORDEN ALLEEN LOSGELATEN OP GROEPEN, NIET OP STUDENTEN!!!
def jinja_object(ding):
	sysls_o = Sysls()
	return JINJAstuff(ding, sysls_o.get_model())

# =============== endpoints =====================
ep_views = Blueprint(
	'ep_views', __name__,
	url_prefix="/views",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

menuitem = 'views'

# handles one student
class View(BaseClass):
	@classmethod
	def get_model(cls) -> dict:
		views_o = Views()
		basic = views_o.empty_view()
		d = dict()
		for b in basic:
			d[b] = {'default': basic[b]}
		d['name'] = ''
		return d

@ep_views.get('/')
def index():
	return redirect('/views/default')

@ep_views.get('/<path:singlename>')
def view(singlename):
	views_o = Views()
	all = views_o.get()
	mijnviews = views_o.mijn_views()
	single = None
	for key, val in all.items():
		if key == singlename:
			single = jinja_object(val)
		all[key] = jinja_object(val)

	# fieldnames are standard db field names
	fieldnames = list(Student.get_empty().keys())
	# eruit are fieldnames that cannot be used in a view, or that are always included
	eruit = ['id', 'firstname', 'lastname', 's_gender', 'grade_ts', 'kom_code', 'notes', 'circulars', 'customs']

	fields = dict()
	for s in fieldnames:
		if s in eruit:
			continue
		fields[s] = Student.get_nicename(s)
	# fields now contains all the standard available fields for a view

	# single._try(fields) contains the fields in this single view
	for s in single._try('fields', default=[]):
		if s in fieldnames:
			fields[s] = Student.get_nicename(s)
		else:
			# these are the circulars fields
			fields[s] = s

	sysls_o = Sysls()
	# these are the available groups
	groepen = sysls_o.get_sysl('s_group')
	for g in list(groepen.keys()):
		if groepen[g]['status'] != 1:
			del(groepen[g])
	# ppp(groepen)

	return render_template(
		'views.html',
		menuitem=menuitem,
		props=UserSettings(),
		all=all,
		single=single,
		kopie=None,
		fields=fields,
		fixedfields=fieldnames,
		groepen=groepen,
		mijnviews=mijnviews,
	)

@ep_views.post('/<path:singlename>')
def views_post(singlename):
	try:
		color = Casting.str_(request.form['color'], '#ffffff')
		status = Casting.int_(request.form['status'], 1)
	except:
		return redirect(f'/views/{singlename}')

	views_o = Views()
	single = views_o.get_single(singlename)
	single['color'] = color
	single['status'] = status
	views_o.make_view(single)
	return redirect(f"/views/{singlename}")

@ep_views.post('/edit/<path:singlename>')
def view_post(singlename):
	views_o = Views()
	single = views_o.get_single(singlename)
	if single is None:
		return redirect('/views/default')

	if not ('fieldname' in request.form and 'fieldnamelist' in request.form):
		return redirect(f"/views/{singlename}")

	try:
		veldnamen = request.form['fieldnamelist'].split(',')
	except:
		return redirect(f"/views/{singlename}")
	veldnaam = Casting.str_(request.form['fieldname'], '')

	if veldnaam != '':
		if 'add-field' in request.form:
			veldnamen.append(veldnaam)

		elif 'delete-field' in request.form:
			veldnamen.remove(veldnaam)

		elif 'new-cycle-field' in request.form:
			if not veldnaam in veldnamen:
				veldnamen.append(f"c_{veldnaam}")

		elif 'new-text-field' in request.form:
			if not veldnaam in veldnamen:
				veldnamen.append(f"t_{veldnaam}")

	single['fields'] = veldnamen
	views_o.make_view(single)
	return redirect(f"/views/{singlename}")

@ep_views.post('/delete/<path:singlename>')
def delete_post(singlename):
	views_o = Views()
	if not singlename in ['default', '']:
		views_o.delete(singlename)
	return redirect('/views/default')

@ep_views.get('/kopie/<path:copyname>')
def kopie(copyname):
	views_o = Views()
	all = views_o.get()
	single = None
	for key, val in all.items():
		if key == copyname:
			single = jinja_object(val)
		all[key] = jinja_object(val)

	return render_template(
		'views.html',
		menuitem=menuitem,
		props=UserSettings(),
		all=all,
		single=single,
		kopie=copyname,
		fields=None,
	)

@ep_views.post('/kopie/<path:copyname>')
def kopie_post(copyname):
	jus = UserSettings()
	views_o = Views()
	try:
		newname = Casting.name_safe(request.form['newname'], True)
		if newname == '':
			return redirect('/views/default')
		if newname in views_o.get():
			return redirect('/views/default')
	except:
		return redirect('/views/default')

	# make new views with newname
	newview = views_o.get_single(copyname)
	newview['name'] = newname
	newview['alias'] = jus.alias()
	newview['created_ts'] = Timetools.now_secs()
	newview['groups'] = list()
	newview['color'] = '#ffffff'
	views_o.make_view(newview)
	return redirect(f"/views/{newname}")

@ep_views.post('/group/<path:singlename>')
def group_post(singlename):
	views_o = Views()
	view = views_o.get_single(singlename)
	if view is None:
		return redirect('/views/default')

	if not 'groups' in view:
		view['groups'] = list()

	groep_id = 0
	for item in request.form:
		if item in ['add-group', 'delete-group']:
			continue
		groep_id = Casting.int_(item, default=0)
	if groep_id == 0:
		return redirect(f"/views/{singlename}")

	if 'add-group' in request.form:
		view['groups'].append(groep_id)
	elif 'delete-group' in request.form:
		view['groups'].remove(groep_id)

	views_o.make_view(view)
	return redirect(f"/views/{singlename}")

