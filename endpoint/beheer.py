from flask import session, redirect, request, Blueprint, render_template

from helpers import Casting, Timetools, IOstuff, Lijsten, ListDicts
from auth import Auth

model_std = dict(
	id = {'default': 0},
	naam = {'default': ''},
	kleur = {'default': ''},
	status = {'default': 'actief'},
)
def get_std_model():
	return model_std.copy()
class StdIo(IOstuff):
	@staticmethod
	def deleteItem(lijstnaam, itemid):
		lijst = Lijsten.get_lijst(lijstnaam)
		for k in list(lijst.keys()):
			if str(k) == str(itemid):
				del lijst[k]
		Lijsten.save_lijst(lijstnaam, lijst)

def get_std_io(record=None):
	return StdIo(record, get_std_model())

model_user = model_std.copy()
model_user.update(dict(
	email = {'default': ''},
	password = {'default': ''},
	magda = {'default': []}, # list of strings, names of places in the software
))
def get_user_model():
	return model_user.copy()
class UserIo(IOstuff):
	pass
def get_user_io(record=None):
	return UserIo(record, get_user_model())
	# def start with _ is jinja def

model_group = model_std.copy()
model_group.update(dict(
	startjaar={'default': [0, ''], 'from': 'sys_year'},
	startperiode={'default': [0, ''], 'from': 'sys_period'},
	status = {'default': [0, ''], 'from': 'sys_status'},
))

def get_group_model():
	return model_group.copy()
class GroupIo(IOstuff):
	pass
def get_group_io(record=None):
	return GroupIo(record, get_group_model())








# =============== endpoints =====================


ep_beheer = Blueprint(
	'ep_beheer', __name__,
	url_prefix="/beheer",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

@ep_beheer.get('/<path:pickle>')
@ep_beheer.get('/')
def beheer(pickle='groups'):

	if pickle == 'users':
		io_class = get_user_io
		io_model = get_user_model()
	elif pickle == 'groups':
		io_class = get_group_io
		io_model = get_group_model()
	else:
		pickle = f'sys_{pickle}'
		io_class = get_std_io
		io_model = get_std_model()

	plist = Lijsten.pickle2list(Lijsten.get_lijst(pickle))
	if len(plist) == 0:
		return f'Pickle {pickle} is leeg'

	for i in range(len(plist)):
		plist[i] = io_class(plist[i])

	if pickle == 'groups':
		statussen = Lijsten.pickle2list(Lijsten.get_lijst('sys_status'))
		fewstatussen = list()
		for s in statussen:
			if s['id'] in [12, 20, 21, 22, 40]:
				fewstatussen.append(s)
	else:
		fewstatussen = []

	lijsten = ['gender', 'grade', 'language', 'module', 'origin', 'period', 'program', 'status', 'uni', 'variant', 'year', 'users', 'groups']
	keys = list(io_model.keys())

	return render_template(
		'beheer.html',
		auth=Auth,
		menu='beheer',
		pickle=pickle.replace('sys_', ''), # submenu items
		items=plist,
		fields=keys, # nu de names nog
		lijsten=lijsten,
		statussen=fewstatussen,
		filter=pickle,
	)

@ep_beheer.post('/')
def beheer_post():
	required = ['pickle', 'action', 'id']
	if not StdIo.check_required_keys(request.form, required):
		return redirect('/')
	pickle = StdIo.sanitize(request.form['pickle'])
	action = StdIo.sanitize(request.form['action'])
	id = StdIo.sanitize(request.form['id'])

	if pickle == '':
		return redirect('/')
	if id == '':
		return redirect(f'/beheer?pickle={pickle}')

	if action == 'Delete':
		StdIo.deleteItem(pickle, id)
		return redirect(f'/beheer?pickle={pickle}')

	if pickle == 'groups':
		groupio = get_group_io(None)
		d = groupio.normalize(request.form)
		print(request.form, '\n\t', d)
		d['id'] = Casting.int_(d['id'])
		d['startjaar'] = Casting.int_(d['startjaar'])
		d['startperiode'] = Casting.int_(d['startperiode'])

	elif pickle == 'users':
		userio = get_user_io(None)
		d = userio.normalize(request.form)
		d['id'] = Casting.int_(d['id'])

	else:
		stdio = get_std_io(None)
		d = stdio.normalize(request.form)
		if not pickle in ['gender', 'grade', 'language']:
			d['id'] = Casting.int_(d['id'])

	Lijsten.upsert_item(pickle, d)
	return redirect(f'/beheer?pickle={pickle}')