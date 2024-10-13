from flask import redirect, request, Blueprint, render_template

from helpers.general import IOstuff, JINJAstuff, BaseClass
from helpers.singletons import UserSettings, Emails

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

	@classmethod
	def alle_emails(cls):
		return ['confirm', 'grade', 'password', 'hunt']

	@classmethod
	def placeholders(cls):
		return ['name', 'minor', 'period', 'year', 'ec', 'grade', 'password']

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



@ep_email.get('/<path:name>')
@ep_email.get('/')
def single_confirm(name: str = 'confirm'):
	jus = UserSettings()
	emails_o = Emails()
	mail = emails_o.get_single(name)
	if mail is None:
		mail = EmailBaseClass.get_empty()
		mail['name'] = name

	return render_template(
		'email-single.html',
		menuitem='emails',
		props=jus,
		alle=EmailBaseClass.alle_emails(),
		placeholders=EmailBaseClass.placeholders(),
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
	emails_o = Emails()
	emails_o.make_email(d)
	return redirect(f"/emails/{name}")


