from flask import Flask, redirect, request, session, Response, render_template, Blueprint

from helpers.general import Casting
from helpers.globalclasses import Props, Students
from helpers.window import Window

app = Flask(__name__)
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
app.url_map.strict_slashes = False

# ============= JINJA FILTERS =============
@app.template_filter('nonone')
def nonone(s):
	if s is None:
		return ''
	elif s in ['None', 'none']:
		return ''
	else:
		return s

'''
@app.errorhandler(Exception)
def handle_error(e):
	Props.set_prop('last_url', '')
	return redirect('/')
'''
@app.before_request
def before_request():
	print('Before request', request.path)
	# handling the first request, restarting where we left of
	rp = request.full_path
	if rp.endswith('?'):
		rp = rp[:-1]

	# print('Before request', Props.get_prop('last_url'))
	if 'static' in rp:
		return
	if Props.is_new():
		Props._started = False
		lasturl = Props.get_prop('last_url', default='/')
		if not lasturl in ['', '/']:
			return redirect(lasturl)
	else:
		Props.set_prop('last_url', rp)
	# print('After request', Props.get_prop('last_url'))


@app.after_request
def add_header(res):
	res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
	res.headers["Pragma"] = "no-cache"
	res.headers["Expires"] = "-1"
	res.headers['X-Content-Type-Options'] = ''
	res.headers['Access-Control-Allow-Origin'] = '*'
	res.headers['Access-Control-Allow-Methods'] = 'get, post'
	return res

@app.get('/')
def home():
	Props.set_prop('window_title', 'home')
	return render_template(
		'home.html',
		menuitem='home',
		props=Props,
	)

from endpoint.system import ep_system
app.register_blueprint(ep_system)

from endpoint.website import ep_website
app.register_blueprint(ep_website)

if __name__ == '__main__':
	app.run() # host="0.0.0.0"
'''
ww = Window(app)
'''
# pyinstaller -F -w --icon=cpnits-picto.ico --name Butterfly main.py
