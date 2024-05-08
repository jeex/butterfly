from hashlib import sha512, md5
from flask import request, session

class Auth:
	zout = 'hee3#lingewi6kkeldFe-code' #os.environ['ZOUT']
	ccodelength = 40
	admins = []

	# for jinja use
	@classmethod
	def _is(cls) -> bool:
		# is logged in
		try:
			return 'user' in session
		except:
			return False

	@classmethod
	def _isadmin(cls) -> bool:
		pass

	@classmethod
	def get_user(cls, key=None) -> any:
		try:
			return session['user'][key]
		except:
			return None

	@classmethod
	def get_hashedpw(cls, pw: str):
		return pw
		pw = pw + cls.zout
		pw = pw.encode()
		sha = sha512()
		sha.update(pw)
		return sha.hexdigest()

	@classmethod
	def logoff(cls):
		session.clear()

	@classmethod
	# ----- db methods that require self
	def get_session_user(cls) -> dict|None:
		# returns user-dict or None
		try:
			return session['user']
		except:
			return None

	@classmethod
	def get_alias(cls) -> str|None:
		try:
			return session['user']['naam']
		except:
			return None

	@classmethod
	def login(cls, email: str, pw: str) -> bool:
		users: dict = Context.get('users')
		user = None
		for nr in users:
			if email == users[nr]['email'] and cls.get_hashedpw(pw) == users[nr]['password']:
				user = users[nr]
				break
		if user is None:
			try:
				del(session['user'])
			except:
				pass
			return False
		# success
		session['user'] = user
		return True
