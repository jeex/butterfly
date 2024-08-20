from flask import Blueprint, render_template, redirect, request, templating
import os
import sys
from helpers.singletons import UserSettings, Students
from helpers.general import Casting, Mainroad

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
	jus = UserSettings()
	if not jus._is():
		Mainroad.loglog('Iets mis met login')
		sys.exit(1)

	students_o = Students()
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
