from flask import Blueprint, render_template

from helpers.singletons import UserSettings, Students

from endpoint.studenten import (
	StudentJinja,
	Student
)
# =============== endpoints =====================
ep_home = Blueprint(
	'ep_home', __name__,
	url_prefix="/home",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

menuitem = 'home'

@ep_home.get('/')
def home():

	students_o = Students()
	jus = UserSettings()

	todos = list()
	mijntodos = list()
	huntodos = list()
	studenten = students_o.all()
	for s in studenten.values():
		for n in s['notes']:
			if n['done'] == 0:
				if n['alias'] == jus.alias():
					mijntodos.append(StudentJinja(s, Student.get_model()))
				elif jus.magda(['admin']):
					s['hun'] = n['alias']
					huntodos.append(StudentJinja(s, Student.get_model()))
				break

	return render_template(
		'home.html',
		menuitem='home',
		props=jus,
		mijntodos=mijntodos,
		huntodos=huntodos,
	)
