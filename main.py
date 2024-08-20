from flask import Flask, redirect, request, render_template
import logging

from helpers.general import Casting, Timetools, Mainroad
from helpers.window import Window
from helpers.singletons import UserSettings, Sysls

app = Flask(__name__, template_folder='templates')
app.config['DEBUG'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'nq023489cnJGH#F!'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'cookieboogle'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['PERMANENT_SESSION_LIFETIME'] = 24 * 60 * 60
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
app.config['initialized'] = False

app.url_map.strict_slashes = False

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if not app.config['initialized']:
	Mainroad.initialize()
	app.config['initialized'] = True

# ============= JINJA FILTERS =============
@app.template_filter('filtername')
def filtername(name):
	fnames = {
		'registratie': 'register',
		'studenten': 'students',
		'beoordelen': 'grading',
		'alumni': 'alumni',
		'niet': 'not',
		'noshow': 'noshow',
		'alle': 'all'
	}
	if name in fnames.keys():
		return fnames[name]
	return name

@app.template_filter('gender')
def gender(name):
	if name.lower() in ['m']:
		return '&#9794;'
	elif name.lower() in ['v', 'f']:
		return '&#9792;'
	else:
		return '&#9893;'

@app.template_filter('initials')
def initials(name):
	name = name.split(' ')
	eruit = ''
	for n in name:
		eruit = f"{eruit}{n.upper()}"
	return eruit

@app.template_filter('circ')
def circular_color(val):
	val = Casting.int_(val, 0)
	sysls = Sysls()
	try:
		cees = sysls.get_sysl('s_circular')
		return cees[val]['color']
	except:
		return '#eeeeee'

@app.template_filter('nonone')
def nonone(s):
	if s is None:
		return ''
	elif s in ['None', 'none']:
		return ''
	else:
		return s

from urllib.parse import quote
@app.template_filter('urlsafe')
def urlsafe(s):
	try:
		return quote(str(s))
	except:
		return s

@app.template_filter('nbsp')
def nbsp(s):
	try:
		return s.replace(' ', '&nbsp;')
	except:
		return s

@app.template_filter('vier')
def vier(i):
	try:
		return f'{i:04d}'
	except:
		return i

@app.template_filter('date')
def asdate(i):
	try:
		if i < 1:
			return ''
		return Timetools.ts_2_td(i, rev=True, withtime=False)
	except:
		return i

@app.template_filter('datetime')
def asdatetime(i):
	try:
		if i < 1:
			return ''
		return Timetools.ts_2_td(i, rev=True, withtime=True)
	except:
		return i

@app.template_filter('datetimelocal')
def asdatetime(i):
	try:
		if i < 1:
			return ''
		return Timetools.ts_2_td(i, rev=True, local=True)
	except:
		return i

'''
@app.errorhandler(Exception)
def handle_error(e):
	Mainroad.loglog(f"error {e}")
	Mainroad.loglog(f"\t{request.full_path}")
	jus = UserSettings()
	jus.set_prop('last_url', '')
	return redirect('/home')
'''

@app.before_request
def before_request():
	rp = request.full_path
	if '/static/' in rp or '/favicon.ico' in rp:
		return
	jus = UserSettings()

	# print('Before request', request.path)
	# handling the first request, restarting where we left of
	rp = rp.rstrip('?')
	rp = rp.rstrip('/')

	if jus.is_new():
		jus._started = False
		lasturl = jus.get_prop('last_url', default='/home')
		if not lasturl in ['', '/']:
			return redirect(lasturl)
	else:
		# don't store paths with args
		if len(request.args) > 0:
			pass
		elif len(request.form) > 0:
			pass
		else:
			jus.set_prop('last_url', rp)


@app.after_request
def add_header(res):
	res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
	res.headers["Pragma"] = "no-cache"
	res.headers["Expires"] = "0"
	res.headers['X-Content-Type-Options'] = ''
	res.headers['Access-Control-Allow-Origin'] = '*'
	res.headers['Access-Control-Allow-Methods'] = 'get, post'
	res.cache_control.public = True
	res.cache_control.max_age = 0
	return res

@app.get('/')
def index():
	return redirect('home')

from endpoint.home import ep_home
app.register_blueprint(ep_home)

from endpoint.studenten import ep_studenten
app.register_blueprint(ep_studenten)

from endpoint.groepen import ep_groepen
app.register_blueprint(ep_groepen)

from endpoint.views import ep_views
app.register_blueprint(ep_views)

# from endpoint.hunts import ep_hunts
# app.register_blueprint(ep_hunts)

from endpoint.emails import ep_email
app.register_blueprint(ep_email)

from endpoint.beheer import ep_beheer
app.register_blueprint(ep_beheer)

from endpoint.website import ep_website
app.register_blueprint(ep_website)


if False:
	app.run(port=5000)
else:
	Window(app)


# pyinstaller -F -w --noconfirm --clean --add-data templates:templates --add-data static:static --icon=cpnits-picto.ico --name Butterfly main.py
