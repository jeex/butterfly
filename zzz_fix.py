import os
import shutil
from helpers.globalclasses import Sysls, Groups, Students
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
for sysname in activeren:
	sys = Sysls.get_sysl(sysname)
	for key, val in sys.items():
		val['status'] = 1
	Sysls.make_sysl(sysname, sys)
	ppp(sys)
'''
'''
old = '/Users/jeex/Desktop/2023/s1/563-alex-raven'
new = '/Users/jeex/Desktop/2023/s2/563-alexia-kraaien'
r = shutil.move(old, new)
print(r)
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