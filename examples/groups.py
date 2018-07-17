#
#	groups.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create a <group> resource and how to use the fanOutPoint.jjjkkk
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
	ae = AE(cse, resourceName=aeName)

	# create two <container>'s' and add them to the <AE>
	cnt1 = Container(ae, resourceName='container1')
	cnt2 = Container(ae, resourceName='container2')

	# create a <group> reosurce that contains both containers, and add it to the <ae>
	grp = Group(ae, resourceName='myGroup', resources=[cnt1, cnt2])
	
	# print the group
	print(grp)

	# add a <contentInstance> to each <container> via the <group> resource's fanOutPoint
	# Note, that we just create a <contentInstance, but we don't set a parent for this
	# <contentInstance>, or send it to the CSE (yet). This is done when assigning it
	# to the whole group.
	cin = ContentInstance(content='Some value', instantly=False)
	grp.createGroupResources(cin)

	# Check whether the <contentIntsance>'s do actually contain the same value
	cin1 = cnt1.latestContentInstance()
	cin2 = cnt2.latestContentInstance()
	if cin1.content == cin2.content:
		print('okay!')
	else:
		print('OH NO!')

	# delete the <AE> to clean up everything
	ae.deleteFromCSE()

