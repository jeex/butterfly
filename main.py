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
app.config['SESSION_COOKIE_NAME'] = 'cookieboogle'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['PERMANENT_SESSION_LIFETIME'] = 24 * 60 * 60
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_DOMAIN'] = None
app.url_map.strict_slashes = False

@app.errorhandler(Exception)
def handle_error(e):
	# redirect
	return redirect('/')

@app.before_request
def before_request():
	# handling the first request, restarting where we left of
	if Props.is_new():
		Props._started = False
		lasturl = Props.get_prop('last_url', default='/')
		if not lasturl in ['', '/', '/?']:
			return redirect(lasturl)
	else:
		Props.set_prop('last_url', request.full_path)

@app.get('/')
def home():
	Props.set_prop('window_title', 'Home')
	options = ''
	for student in Students._sysmem.values():
		options += f'<option value="{student["id"]}">{student["firstname"]} {student["lastname"]}</option>\n'
	return f'''<!doctype html>
<html>
	<body style="background-color: pink;">
		<p>{str(Props._props)}</p>
		<form method="get" action="/student">
			<select name="studid">
				{options}
			</select>
			<input type="submit" name="" value="go">
		</form>
		<p><a target="_blank" href="https://cpnits.nl">Huidige cpnits &rarr;</a></p>
	</body>
</html>
'''

@app.get('/student')
def studid():
	try:
		studid = Casting.int_(request.args.get('studid'), default=None)
		if studid is None:
			return redirect('/')
		student = Students.get(studid)
	except:
		return redirect('/')

	Props.set_prop('window_title', f'{student["firstname"]} {student["lastname"]}' )
	return f'''<!doctype html>
<html>
	<body style="background-color: lightskyblue;">
		<p>{student}</p>
		<p><a href="/">home</a></p>
	</body>
</html>
'''

ww = Window(app)
# pyinstaller -F -w --icon=cpnits-picto.ico --name Butterfly main.py
