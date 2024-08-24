from flask import Blueprint, render_template, redirect, request, templating
import os
from pprint import pprint as ppp
import sys
from helpers.singletons import UserSettings, Students, Sysls
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
	pergroep = dict()
	studenten = students_o.all()
	sysls_o = Sysls()
	groepen = dict(sysls_o.get_sysl('s_group'))
	for s in studenten.values():
		for n in s['notes']:
			if n['done'] == 0:
				if not s['s_group'] in pergroep:
					pergroep[s['s_group']] = list()
				pergroep[s['s_group']].append(StudentJinja(s, Student.get_model()))

	bericht = Mainroad.get_message()
	if bericht == '':
		bericht = None

	return render_template(
		'home.html',
		menuitem='home',
		props=jus,
		pergroep=pergroep,
		groepen=groepen,
		bericht=bericht,
	)
