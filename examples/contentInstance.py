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

	# get the <CSEBase> resource
	cse = CSEBase(session, 'mn-cse')

	# create an <AE> resource
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName, instantly=True)

	# create a <container> and add it to the <AE>
	cnt = Container(ae, instantly=True)

	# add a <contentInstance> to the <container>, with labels
	cin = ContentInstance(cnt, content='Some value', labels=['label1/example', 'label2/anotherExample'], instantly=True)

	# retrieve the <contentInstance> via the <container>.latest and print it
	cin2 = cnt.latestContentInstance()
	print(cin2)

	# delete the <AE> to clean up everything
	ae.deleteFromCSE()

