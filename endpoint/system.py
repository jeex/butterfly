from flask import session, redirect, request, Blueprint, render_template

from helpers.general import Casting, Timetools, IOstuff, ListDicts, JINJAstuff
from helpers.globalclasses import Sysls, Props

def jinja_object(ding):
	return JINJAstuff(ding, Sysls.get_model())

# =============== endpoints =====================
ep_system = Blueprint(
	'ep_system', __name__,
	url_prefix="/system",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

menuitem = 'beheer'
Props.set_prop('window_title', 'beheer')

@ep_system.get('/')
@ep_system.get('/<path:sysl>')
@ep_system.get('/<path:sysl>/<int:id>')
def kiezen(sysl='', id=0):
	if not Props.magda('beheer'):
		return redirect('/')

	# system lijsten
	lijsten = Sysls.get_lijsten()
	if sysl != '':
		allitems = Sysls.get_sysl_as_list(sysl)
		allitems = ListDicts.sortlistofdicts(allitems, 'ordering')
		for i in range(len(allitems)):
			allitems[i] = jinja_object(allitems[i])
	else:
		allitems = dict() # alle items van deze sysl
	fields = Sysls.get_fields()
	return render_template(
		'beheer.html',
		menuitem=menuitem,
		props=Props,
		lijsten=lijsten,
		syslname=sysl,
		fields=fields,
		allitems=allitems,
		id=id,
	)

@ep_system.post('/<path:sysl>')
@ep_system.post('/<path:sysl>/<int:id>')
def ep_system_post(sysl, id=0):
	if not Props.magda('beheer'):
		return redirect('/')

	sysl = sysl.strip()
	if sysl == '':
		return redirect(f'/system')

	required = ['id', 'name', 'color', 'extra', 'status', 'action', 'ordering']
	if not IOstuff.check_required_keys(request.form, required):
		return redirect(f'/system/{sysl}')
	required.remove('action')
	d = IOstuff.crunch_singles(request.form, required)
	d['id'] = Casting.int_(d['id'], default=0)
	d['status'] = Casting.int_(d['status'], default=0)
	d['ordering'] = Casting.int_(d['ordering'], default=0)
	if d['id'] == 0:
		return redirect(f'/system/{sysl}')
	current = Sysls.get_sysl_item(sysl, d['id'])
	if not current is None:
		if d['id'] != current['id']:
			# hier gaat iets mis
			print('deze')
			return redirect(f'/system/{sysl}')

	if current is None and request.form.get('action') == 'Save':
		# new
		Sysls.set_sysl_item(sysl, d['id'], d)

	elif request.form.get('action') == 'Delete':
		Sysls.del_sysl_item(sysl, d['id'])

	elif request.form.get('action') == 'Save':
		# update
		Sysls.set_sysl_item(sysl, d['id'], d)
	else:
		return redirect(f'/system')

	return redirect(f'/system/{sysl}/{d["id"]}')

@ep_system.post('/ordering/<path:sysl>')
def post_ordering(sysl):
	if not Props.magda('beheer'):
		return redirect('/')

	required = ['ordering', 'order']
	if not IOstuff.check_required_keys(request.form, required):
		return redirect(f'/system/{sysl}')
	try:
		ordering = request.form.get('ordering').split(',')
	except:
		print(f"ordering mislukt {request.form.get('ordering')}")
		return redirect(f'/system/{sysl}')

	alle = Sysls.get_sysl(sysl)
	oo = 1
	for id in ordering:
		id = int(id)
		# ordering contains id's in requested order
		if not id in alle.keys():
			# print(f"ontbrekende key {id} in {alle}")
			return redirect(f'/system/{sysl}')
		alle[id]['ordering'] = oo
		# alle[id]['status'] = 1
		oo += 1
	Sysls.make_sysl(sysl, alle)
	return redirect(f'/system/{sysl}')