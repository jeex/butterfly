from  helpers.general import Pickles
import os
from pprint import pprint as ppp


'''
# adding a standard field to view
pad = "/Users/jeex/Library/CloudStorage/OneDrive-SharedLibraries-NHLStenden/Group - CPNITS - docenten - docenten/_BUTTERFLY/views"
lijst = os.listdir(pad)
for l in lijst:
	if not l.endswith(".pickle"):
		continue
	d = Pickles.read(os.path.join(pad, l))
	if d['name'] == 'default':
		d['fields'] = ['id', 'assessment', 'firstname', 'lastname']
	else:
		if not 'assessment' in d['fields']:
			d['fields'].insert(1, 'assessment')
	ppp(d)
	# Pickles.write(os.path.join(pad, l), d)
'''


'''
# give all students a new password
from helpers.singletons import Students
students = Students()
all = students.all_as_lod()
for a in all:
	pw = students.new_password(a['id'])
	a['password'] = pw
	students.make_student_pickle(a['id'], a)
	print(a['id'], a['password'])
'''
