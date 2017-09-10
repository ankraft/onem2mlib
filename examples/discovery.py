#
#	discover.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to discover resources.
#

import uuid, sys
sys.path.append('..')
import onem2mlib.session as SE
import onem2mlib.constants as CON
from onem2mlib.resources import *
from onem2mlib.utilities import *


if __name__ == '__main__':

	# Create session & get CSE
	session = SE.Session('http://localhost:8282', 'admin:admin')
	cse = CSEBase(session, 'mn-cse')

	#
	# Create an AE, a container, and a couple of contentInstances first
	#
	ae = AE(cse, resourceName='exampleAE_'+str(uuid.uuid4().hex), instantly=True)
	cnt = Container(ae, instantly=True)
	ContentInstance(cnt, resourceName='Label1', content='value1', labels=['label1/label', 'label2/anotherLabel'], instantly=True)	# both labels
	ContentInstance(cnt, resourceName='Label2', content='value2', labels=['label1/label'], instantly=True)						# only label 1
	ContentInstance(cnt, resourceName='Label3', content='value3', labels=['label2/anotherLabel'], instantly=True)					# only label 2
	ContentInstance(cnt, resourceName='Label4', content='value4', instantly=True) 													# no label at all


	# First, find all containers in the AE. This should only be one
	print('*** Find container')
	for cnt in ae.discover( [newTypeFilterCriteria(CON.Type_Container)] ):
		print(cnt)

	# find all contentInstances with "label1/label"
	print('*** Contains: label1/label')
	for cin in ae.discover( [newLabelFilterCriteria('label1/label')] ):
		print(cin)

	# find all contentInstances with both labels set
	print('*** Contains: Either one of both labels')
	for cin in ae.discover( [newLabelFilterCriteria('label1/label'), newLabelFilterCriteria('label2/anotherLabel')] ):
		print(cin)

	# delete the <AE> to clean up everything
	#ae.deleteFromCSE()



