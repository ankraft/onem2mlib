#
#	contentInstance.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create a <container> resource and <contentInstance>'s to it'.
#	Everything is deleted in the end.
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

	# get the <CSEBase> resource.
	cse = CSEBase(session, conf.CSEID)

	# create an <AE> resource
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName)

	# create a <container> and add it to the <AE>
	cnt = Container(ae)
	print(cnt)

	# add a <contentInstance> to the <container>, with labels
	cin = ContentInstance(cnt, content='Some value', labels=['label1/example', 'label2/anotherExample'])

	# or do the same a bit more conventient
	cnt.addContent('Some other Value', ['label1/example', 'label2/anotherExample'])
	print('ContentInstances in the Container: ' + str([cin.resourceID for cin in cnt.contentInstances()]))

	# retrieve the <contentInstance> via the <container>.latest and print it
	print('Latest ' + str(cnt.latestContentInstance()))

	# The same, but only the <contentInstance>'s value.
	print(cnt.latestContent())

	# Get the time series content in a list
	print(cnt.contents())

	# delete the <AE> to clean up everything
	ae.deleteFromCSE()

