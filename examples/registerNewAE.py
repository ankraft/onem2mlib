#
#	createAE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create an <AE> resource in an CSE.
#

import uuid, sys, logging
sys.path.append('..')
from onem2mlib import *
import onem2mlib.constants as CON
import conf


if __name__ == '__main__':
	logging.basicConfig(level=conf.LOGGINGLEVEL)
	logging.getLogger('urllib3').setLevel(logging.CRITICAL)

	# Create session w/o originator
	session = Session(conf.CSEURL)


	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(session=session, resourceName=aeName, originator='C' + aeName, instantly=False)
	ae.createInCSE()
	print(ae)
	print(session)
	ae.deleteFromCSE()
	print(session)
	print('---')


	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(session=session, resourceName=aeName, originator='C' + aeName)
	print(ae)
	print(session)
	ae.deleteFromCSE()
	print(session)
	print('---')


	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(session=session, resourceName=aeName) # no originator
	print(ae)
	print(session)
	ae.deleteFromCSE()
	print(session)

 