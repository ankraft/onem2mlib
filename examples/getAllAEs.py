#
#	getAllAEs.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to retrieve a list of all <AE> resources from an CSE.
#

import uuid, sys, logging
sys.path.append('..')
from onem2mlib import *

loggingLevel = logging.INFO
loggingLevel = logging.DEBUG


if __name__ == '__main__':
	logging.basicConfig(level=loggingLevel)
	logging.getLogger('urllib3').setLevel(logging.CRITICAL)

	# create session 
	session = Session('http://localhost:8282', 'admin:admin')
	session = Session('http://localhost:8080', 'admin:admin')
	#session = Session('http://localhost:7579', 'S')


	# get the <CSEBase> resource
	#cse = CSEBase(session, 'mn-cse')
	cse = CSEBase(session, '')
	#cse = CSEBase(session, 'Mobius')
	print(cse)


	# get and print a list of all <AE> resources
	aes = cse.aes()
	for ae in aes: 
		print(ae)
