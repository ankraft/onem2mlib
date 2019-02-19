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
import conf


if __name__ == '__main__':
	logging.basicConfig(level=conf.LOGGINGLEVEL)
	logging.getLogger('urllib3').setLevel(logging.CRITICAL)

	# create session 
	session = Session(conf.CSEURL, conf.ORIGINATOR)


	# get the <CSEBase> resource
	cse = CSEBase(session, conf.CSEID)
	print(cse)


	# get and print a list of all <AE> resources
	aes = cse.aes()
	for ae in aes: 
		print(ae)
