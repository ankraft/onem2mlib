#!/usr/local/bin/python3

#
#	test_notification.py
#
#	(c) 2018 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <subscription> reource implementation.
#

import unittest
import os, sys, time
sys.path.append('..')

from onem2mlib import *
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC
import onem2mlib.notifications as NOT
from conf import *


class TestNotification(unittest.TestCase):
	session = None
	cse = None
	ae = None
	cnt = None
	sub = None
	cin = None

	callbackResource = None


	@classmethod
	def setUpClass(cls):
		TestNotification.session = Session(host, originator, encoding)
		TestNotification.cse = CSEBase(TestNotification.session, CSE_ID)
		if TestNotification.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		TestNotification.ae = AE(TestNotification.cse, resourceName=AE_NAME)
		TestNotification.cnt = Container(TestNotification.ae, resourceName=CNT_NAME)
		if not NOT.setupNotifications(None, NOT_HOST, NOT_PORT):	# simple notification setup
			print('*** Cannot setup notification server at "' + NOT_HOST + ':' + NOT_PORT)
			exit()


	@classmethod
	def tearDownClass(cls):
		if TestNotification.ae:
			TestNotification.ae.deleteFromCSE()
			TestNotification.ae = None
		NOT.shutdownNotifications()


	def test_init(self):
		self.assertIsNotNone(TestNotification.session)
		self.assertIsNotNone(TestNotification.cse)
		self.assertIsNotNone(TestNotification.cse.resourceID)
		self.assertIsNotNone(TestNotification.ae)
		self.assertIsNotNone(TestNotification.ae.resourceID)
		self.assertIsNotNone(TestNotification.cnt)
		self.assertIsNotNone(TestNotification.cnt.resourceID)


	def test_enableDisable(self):
		self.assertTrue(NOT.isNotificationEnabled())
		NOT.disableNotifications()
		self.assertFalse(NOT.isNotificationEnabled())
		NOT.enableNotifications()
		self.assertTrue(NOT.isNotificationEnabled())


	# define a callback function
	def callback(self, resource):
		global callbackResource
		callbackResource = resource


	def test_addSubscription(self):
		# add a subscription and add content
		self.assertIsNotNone(TestNotification.cnt)
		self.assertTrue(TestNotification.cnt.subscribe(self.callback))


	def test_notify(self):
		# create a new contentInstance to trigger the notification
		TestNotification.cin = TestNotification.cnt.addContent(CIN_CONTENT)
		self.assertIsNotNone(TestNotification.cin)
		# Wait a moment
		time.sleep(delayInSec)
		# and check whether the callback happened
		self.assertIsNotNone(callbackResource)
		self.assertEqual(callbackResource.resourceID, TestNotification.cin.resourceID)
		self.assertEqual(callbackResource.content, CIN_CONTENT)


	def test_notifyFail(self):
		global callbackResource
		callbackResource = None
		# create a new contentInstance to try to trigger the notification
		TestNotification.cin = TestNotification.cnt.addContent(CIN_CONTENT)
		self.assertIsNotNone(TestNotification.cin)
		# Wait a moment
		time.sleep(delayInSec)
		# and check whether the callback didn't happened
		self.assertIsNone(callbackResource)


	def test_hasSubscription(self):
		self.assertTrue(NOT.hasSubscription(TestNotification.cnt))


	def test_removeSubscription(self):
		self.assertIsNotNone(TestNotification.cnt)
		self.assertTrue(NOT.removeSubscription(TestNotification.cnt))


	def test_finit(self):
		self.assertIsNotNone(TestNotification.ae)
		self.assertTrue(TestNotification.ae.deleteFromCSE())
		TestNotification.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestNotification('test_init'))
	suite.addTest(TestNotification('test_enableDisable'))
	suite.addTest(TestNotification('test_addSubscription'))
	suite.addTest(TestNotification('test_hasSubscription'))
	suite.addTest(TestNotification('test_notify'))
	suite.addTest(TestNotification('test_removeSubscription'))
	suite.addTest(TestNotification('test_notifyFail')) 
	suite.addTest(TestNotification('test_finit'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
