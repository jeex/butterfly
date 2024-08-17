from copy import deepcopy
from pprint import pprint as ppp
from flask import redirect, request, Blueprint, render_template

from helpers.general import Timetools, JINJAstuff, IOstuff, Casting
from helpers.singletons import UserSettings, Sysls, Hunts

def jinja_object(ding):
	sysls_o = Sysls()
	return JINJAstuff(ding, sysls_o.get_model())

# =============== endpoints =====================
ep_hunts = Blueprint(
	'ep_hunts', __name__,
	url_prefix="/hunts",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)
menuitem = 'hunts'

@ep_hunts.get('/<int:id>')
@ep_hunts.get('/')
def bak_met_vragen(id = 1):
	hunts_o = Hunts()
	sysls_o = Sysls()

	# get single assignment
	single = hunts_o.get_single_question(id)
	if single is None:
		return redirect('/hunts')
	answers = deepcopy(single['answers'])
	for i in range(len(answers)):
		answers[i] = jinja_object(answers[i])
	single = jinja_object(single)

	# get all assignments
	all_questions = hunts_o.get_questions()
	all = dict()
	for a in all_questions.values():
		all[a['id']] = jinja_object(a)

	return render_template(
		'hunts_vragen.html',
		menuitem=menuitem,
		submenu='vragen',
		props=UserSettings(),
		all=all,
		single=single,
		answers=answers,
		kopie=None,
	)

@ep_hunts.post('/<int:id>')
def bak_met_vragen_post(id):
	hunts_o = Hunts()

	d = hunts_o.get_single_question(id)
	if d is None:
		return redirect('/hunts')

	if 'save' in request.form:
		d['name'] = IOstuff.sanitize(request.form.get('name'))
		d['status'] = Casting.int_(request.form.get('status'), default=1)
		d['color'] = request.form.get('color')
		d['html'] = Casting.str_(request.form.get('html'))

		antwoorden = list()
		for a in request.form:
			if not a.startswith('antwoord_'):
				continue
			ant = hunts_o.empty_answer()
			print(a, request.form[a])
			ant['id'] = Casting.int_(a.split('_')[1])
			ant['answer'] = IOstuff.sanitize(request.form[a])
			ant['good'] = request.form.get(f"goed_{ant['id']}") == '1'
			print(ant)
			antwoorden.append(ant)
		d['answers'] = antwoorden
		hunts_o.make_question(d)

	elif 'delete' in request.form:
		hunts_o.delete_question(id)

	return redirect(f"/hunts/{id}")

@ep_hunts.get('/kopie/<int:kopie_id>')
def kopie_vraag(kopie_id):
	hunts_o = Hunts()

	# get single assignment
	single = hunts_o.get_single_question(kopie_id)
	if single is None:
		return redirect('/hunts')
	answers = deepcopy(single['answers'])
	for i in range(len(answers)):
		answers[i] = jinja_object(answers[i])
	single = jinja_object(single)

	# get all assignments
	all_questions = hunts_o.get_questions()
	all = dict()
	for a in all_questions.values():
		all[a['id']] = jinja_object(a)

	return render_template(
		'hunts_vragen.html',
		menuitem=menuitem,
		submenu='vragen',
		props=UserSettings(),
		all=all,
		single=single,
		answers=answers,
		kopie=kopie_id,
	)

@ep_hunts.post('/kopie/<int:kopie_id>')
def kopie_vraag_post(kopie_id):
	hunts_o = Hunts()

	# get single assignment
	single = hunts_o.get_single_question(kopie_id)
	if single is None:
		return redirect('/hunts')
	newid = hunts_o.get_new_question_id()
	single['id'] = newid
	single['name'] = IOstuff.sanitize(request.form.get('newname'))
	hunts_o.make_question(single)
	return redirect(f'/hunts/{newid}')

@ep_hunts.get('/hunt/<int:id>')
@ep_hunts.get('/hunt')
def hunt_get(id=1):
	hunts_o = Hunts()
	sysls_o = Sysls()

	# get all questions
	all_questions = hunts_o.get_questions()
	all = dict()
	for a in all_questions.values():
		all[a['id']] = jinja_object(a)

	return render_template(
		'hunts_hunts.html',
		menuitem=menuitem,
		submenu='vragen',
		props=UserSettings(),
		all=all,
		single=None,
		kopie=None,
	)