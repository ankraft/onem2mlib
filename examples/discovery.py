#
#	discover.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to discover resources.
#

import uuid, sys, logging
sys.path.append('..')
from onem2mlib import *
import onem2mlib.constants as CON
from onem2mlib.utilities import *
import conf

if __name__ == '__main__':
	logging.basicConfig(level=conf.LOGGINGLEVEL)
	logging.getLogger('urllib3').setLevel(logging.CRITICAL)

	# Create session & get CSE
	session = Session(conf.CSEURL, conf.ORIGINATOR)
	cse = session.getCSEBase()

	#
	# Create an AE, a container, and a couple of contentInstances first
	#
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)
	ae = AE(parent=cse, resourceName=aeName, originator='C' + aeName, instantly=True)
	
	cnt = Container(parent=ae, instantly=True)
    
	# REFACTOR: parent=cnt
	ContentInstance(parent=cnt, resourceName='Label1', content='value1', labels=['label1/label', 'label2/anotherLabel'], instantly=True)
	ContentInstance(parent=cnt, resourceName='Label2', content='value2', labels=['label1/label'], instantly=True)
	ContentInstance(parent=cnt, resourceName='Label3', content='value3', labels=['label2/anotherLabel'], instantly=True)
	ContentInstance(parent=cnt, resourceName='Label4', content='value4', instantly=True) 

	# First, find all containers in the AE. This should only be one
	print('*** Find container')
	for found_cnt in ae.discover( [newTypeFilterCriteria(CON.Type_Container)] ):
		print(found_cnt)
  
	# find all contentInstances with "label1/label"
	print('*** Contains: label1/label')
	for cin in ae.discover( [newLabelFilterCriteria('label1/label')] ):
		print(cin)

	# find all contentInstances with both labels set
	print('*** Contains: Either one of both labels')
	for cin in ae.discover( [newLabelFilterCriteria('label1/label'), newLabelFilterCriteria('label2/anotherLabel')] ):
		print(cin)