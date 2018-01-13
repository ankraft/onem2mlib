#
#	contentInstance.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create a <container> resource and <contentInstance>'s to it'.
#	Everything is deleted in the end.
#

import uuid, sys
sys.path.append('..')
from onem2mlib import *


if __name__ == '__main__':
	# create session 
	session = Session('http://localhost:8282', 'admin:admin')

	# get the <CSEBase> resource.
	# This time we *don't* retrieve the CSEBase resource, but only hold the
	cse = CSEBase(session, 'mn-cse', resourceName='mn-name', instantly=False)

	# create an <AE> resource
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName)

	# create a <container> and add it to the <AE>
	cnt = Container(ae)

	# add a <contentInstance> to the <container>, with labels
	cin = ContentInstance(cnt, content='Some value', labels=['label1/example', 'label2/anotherExample'])

	# or do the same a bit more conventient
	cnt.addContent('Some other Value', ['label1/example', 'label2/anotherExample'])
	print('ContentInstances in the Container: ' + str([cnt.resourceID for cnt in cnt.contentInstances()]))

	# retrieve the <contentInstance> via the <container>.latest and print it
	print('Latest ' + str(cnt.latestContentInstance()))

	# The same, but only the <contentInstance>'s value.
	print(cnt.latestContent())

	# Get the time series content in a list
	print(cnt.contents())

	# delete the <AE> to clean up everything
	ae.deleteFromCSE()

