#
#	getAllAEs.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to retrieve a list of all <AE> resources from an CSE.
#

import uuid, sys
sys.path.append('..')
from onem2mlib import *


if __name__ == '__main__':
	# create session 
	session = Session('http://localhost:8282', 'admin:admin')

	# get the <CSEBase> resource
	cse = CSEBase(session, 'mn-cse')

	# get and print a list of all <AE> resources
	aes = cse.aes()
	for ae in aes: 
		print(ae)
