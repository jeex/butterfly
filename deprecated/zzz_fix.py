import os
import shutil
from helpers.singletons import Sysls, Students
from pprint import pprint as ppp

'''
student = Students.get_by_id(590)
student['s_group'] = student['g_group']
del(student['g_group'])
Students.make_student_pickle(str(234), student)
ppp(student)
'''

'''
users = Sysls.get_sysl('s_user')
all = Students.all_as_lod()
for a in all:
	for i in range(len(a['notes'])):
		uid =a['notes'][i]['user_id']
		if not uid in users:
			continue
		a['notes'][i]['alias'] = users[uid]['name']
	Students.make_student_pickle(a['id'], a)
'''

'''
pad = '/Users/jeex/Desktop/students'
for l in os.listdir(pad):
	if not l.endswith('.pickle'):
		continue
	newname = f"{l.split('-')[0]}.pickle"
	print(l, newname)
	os.rename(os.path.join(pad, l), os.path.join(pad, newname))
'''

'''
activeren = ['s_origin', 's_uni', 's_program']
sy = Sysls()
for sysname in activeren:
	sys = sy.get_sysl(sysname)
	for key, val in sys.items():
		val['status'] = 1
	sy.make_sysl(sysname, sys)
	ppp(sys)
'''


'''
old = '/Users/jeex/Desktop/2023/s1/563-alex-raven'
new = '/Users/jeex/Desktop/2023/s2/563-alexia-kraaien'
r = shutil.move(old, new)
print(r)
'''

'''
all = Students.all_as_lod()
for a in all:
	if 'pf_url' in a:
		if not a['pf_url'] is None:
			a['pf_url'] = a['pf_url'].split('#')[0]
			a['pf_url'] = a['pf_url'].split('?')[0]
		else:
			pf = a['pf_url']
	else:
		a['pf_url'] = ''
	Students.make_student_pickle(a['id'], a)
'''

'''
# fix foute lang omzetting
sqlitepad = "cpnits27.sqlite"
from zzz_class_sqlite import Sqlite
sqlite = Sqlite(sqlitepad)

all_old = sqlite.read("SELECT ID, lang FROM studenten")
# ppp(all_old)
for student in all_old:
	id = student['ID']
	if student['lang'] in ['EN', 'en']:
		lang = 2
	else:
		lang = 1

	# adjust in sql table
	sql = f"UPDATE nw_student SET s_lang={lang} WHERE id={id}"
	sqlite.update(sql)

	# adjust in OneDrive db
	students = Students()
	student = students.get_by_id(id)
	if student is None:
		continue
	student['s_lang'] = lang
	students.make_student_pickle(id, student)
'''


'''
# fix https://docs.google.com/document/d/1sjriIP3OnZSwoQEjM_NRHvKeXq0CcFq24xVu3Ae7XLA
# REMOVE /edit#heading=h.3t5aa5xzo621
stuo = Students()
all = stuo.all()
for id, val in all.items():
	if not 'pf_url' in val:
		continue
	url = val['pf_url']
	if not isinstance(url, str):
		continue
	if url.strip() == '':
		continue
	head, sep, tail = url.partition('/edit')
	if sep == '/edit':
		val['pf_url'] = head
		stuo.make_student_pickle(id, val)
		print(id, sep)
		continue

	head, sep, tail = url.partition('?usp')
	if sep == '?usp':
		val['pf_url'] = head
		stuo.make_student_pickle(id, val)
		print(id, sep)
		continue

	print(url)
'''

'''
stuo = Students()
all = stuo.all()
for id, val in all.items():
	if not 's_program' in val:
		continue
	if val['s_program'] == 87:
		val['s_program'] = 32
		stuo.make_student_pickle(id, val)
		print()
		ppp(val)
'''
