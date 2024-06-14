
from flask import current_app, redirect, request, Blueprint, render_template

from helpers.general import IOstuff, JINJAstuff, BaseClass

class EmailBaseClass(BaseClass):
	@classmethod
	def get_model(cls) -> dict:
		return dict(
			name={'default': ''},
			en_text={'default': ''},
			en_subject={'default': ''},
			nl_text={'default': ''},
			nl_subject={'default': ''},
		)

class EmailJinja(JINJAstuff):
	pass

# =============== endpoints =====================
ep_email = Blueprint(
	'ep_email', __name__,
	url_prefix="/emails",
	template_folder='templates',
    static_folder='static',
	static_url_path='static',
)

alle_emails = ['confirm', 'grade'] #, 'hunt']
placeholders = ['naam', 'minor', 'periode', 'jaar', 'ec', 'cijfer', 'wachtwoord']

@ep_email.get('/')
def emails():
	return redirect('/emails/confirm')

@ep_email.get('/<path:name>')
def single_confirm(name: str):
	emails_o = current_app.config['Emails']
	mail = emails_o.get_single(name)
	if mail is None:
		mail = EmailBaseClass.get_empty()
		mail['name'] = name

	return render_template(
		'email-single.html',
		menuitem='emails',
		props=current_app.config['Props'],
		alle=alle_emails,
		placeholders=placeholders,
		mail=EmailJinja(mail, EmailBaseClass.get_model()),
	)

@ep_email.post('/<path:name>')
def single_post(name: str):
	d = dict()
	try:
		d['nl_text'] = IOstuff.sanitize(request.form['nl_text'].strip())
		d['nl_subject'] = IOstuff.sanitize(request.form['nl_subject'].strip())
		d['en_text'] = IOstuff.sanitize(request.form['en_text'].strip())
		d['en_subject'] = IOstuff.sanitize(request.form['en_subject'].strip())

	except Exception as e:
		return redirect(f"/emails/{name}")
	d['name'] = name
	emails_o = current_app.config['Emails']
	emails_o.make_email(d)
	return redirect(f"/emails/{name}")


