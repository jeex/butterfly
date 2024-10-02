from  helpers.general import Pickles
import os
from pprint import pprint as ppp
pad = "/Users/jeex/Library/CloudStorage/OneDrive-SharedLibraries-NHLStenden/Group - CPNITS - docenten - docenten/_BUTTERFLY/views"

lijst = os.listdir(pad)
for l in lijst:
	if not l.endswith(".pickle"):
		continue
	d = Pickles.read(os.path.join(pad, l))
	'''if d['name'] == 'default':
		d['fields'] = ['id', 'assessment', 'firstname', 'lastname']
	else:
		d['fields'].insert(1, 'assessment')'''
	ppp(d)
	# Pickles.write(os.path.join(pad, l), d)

