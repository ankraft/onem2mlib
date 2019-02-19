#
#	remoteCSE.py
#
#	(c) 2018 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how retrieve and work with a remoteCSE resource
#
#	PLEASE NOTE, that this example only works when the CSE is registered
#	with another CSE..
#

import sys, logging
sys.path.append('..')
from onem2mlib import *
import conf


if __name__ == '__main__':
	logging.basicConfig(level=conf.LOGGINGLEVEL)
	logging.getLogger('urllib3').setLevel(logging.CRITICAL)

	# Create session
	session = Session(conf.CSEURL, conf.ORIGINATOR)

	# Get the <CSEBase> resource
	cse = CSEBase(session, conf.CSEID)

	# Get a list of all <remoteCSE> resource
	remoteCSEs = cse.remoteCSEs()

	# For simplicity, only process the first one in the list
	if len(remoteCSEs):
		rCSE = remoteCSEs[0]

		# Print the remote CSE
		print(rCSE)

		# Get the CSE for local access
		localrCSE = rCSE.cseFromLocalCSE()
		print(localrCSE)

		# Get the CSE for remote access
		remoterCSE = rCSE.cseFromRemoteCSE()
		print(remoterCSE)
		
		# Create an AE through the local CSE resrource
		ae = AE(localrCSE, 'testAE')
		print(ae)

		# Fetch that AE via the remote CSE resource
		aer = remoterCSE.findAE('testAE')
		print(ae)

		# And delete the AE via the remote CSE
		aer.deleteFromCSE()


