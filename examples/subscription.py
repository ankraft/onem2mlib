#
#	subscription.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to susbcribe to resources and receive notifications.
#

import uuid, sys, time
sys.path.append('..')
from onem2mlib import *
import onem2mlib.constants as CON
import onem2mlib.notifications as NOT



# This is the callback function that is called for the notifications.
# The parameter is the changed resource
def callback(resource):
	if resource.type == CON.Type_ContentInstance:
		print(resource.content)
	else:
		print(resource)


if __name__ == '__main__':

	# Setup the notification sub-system
	print('Setting up notifications...')
	NOT.setupNotifications(callback)

	# Create session
	session = Session('http://localhost:8282', 'admin:admin')

	# Get the <CSEBase> resource
	cse = CSEBase(session, 'mn-cse')

	# create an <AE> resource
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, aeName)

	# create a <container> and add it to the <AE>
	cnt = Container(ae)
	cnt.subscribe()

	# Change the <container> to trigger a notification for that resource
	cnt.maxNrOfInstances = 10
	cnt.updateInCSE()

	# Add a <contentInstance> to the <Container> to trigger a notification
	cnt.addContent('Some value')

	# Give the cse a moment to process the notification before shutting down the notification
	# sub-system
	time.sleep(2)

	# Shutdown the notification sub-system (actually not really necessary)
	print('Shutting down notifications...')
	NOT.shutdownNotifications()

	# Cleanup
	ae.deleteFromCSE()


