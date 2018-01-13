#!/usr/local/bin/python3

#
#	test_subscription.py
#
#	(c) 2017 by Andreas Kraft
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


class TestSubscription(unittest.TestCase):
	session = None
	cse = None
	ae = None
	cnt = None
	sub = None

	@classmethod
	def setUpClass(self):
		TestSubscription.session = Session(host, originator, encoding)
		TestSubscription.cse = CSEBase(TestSubscription.session, CSE_ID)
		if TestSubscription.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		TestSubscription.ae = AE(TestSubscription.cse, resourceName=AE_NAME)
		TestSubscription.cnt = Container(TestSubscription.ae, resourceName=CNT_NAME)
		if not NOT.setupNotifications(None, NOT_HOST, NOT_PORT):	# simple notification setup
			print('*** Cannot setup notification server at "' + NOT_HOST + ':' + NOT_PORT)
			exit()


	@classmethod
	def tearDownClass(self):
		if TestSubscription.ae:
			TestSubscription.ae.deleteFromCSE()
			TestSubscription.ae = None
		NOT.shutdownNotifications()


	def test_init(self):
		self.assertIsNotNone(TestSubscription.session)
		self.assertIsNotNone(TestSubscription.cse)
		self.assertIsNotNone(TestSubscription.cse.resourceID)
		self.assertIsNotNone(TestSubscription.ae)
		self.assertIsNotNone(TestSubscription.ae.resourceID)
		self.assertIsNotNone(TestSubscription.cnt)
		self.assertIsNotNone(TestSubscription.cnt.resourceID)


	def test_createSubscriptionContainer(self):
		TestSubscription.sub = Subscription(TestSubscription.cnt, resourceName=SUB_NAME, notificationURI=[NOT_NU], instantly=False)
		self.assertEqual(TestSubscription.sub.type, CON.Type_Subscription)
		self.assertTrue(TestSubscription.sub.createInCSE())
		self.assertEqual(TestSubscription.sub.resourceName, SUB_NAME)
		self.assertEqual(TestSubscription.sub.notificationURI[0], NOT_NU)


	def test_retrieveSubscriptionContainer(self):
		self.assertIsNotNone(TestSubscription.sub)
		self.assertIsNotNone(TestSubscription.sub.resourceID)
		sub = Subscription(TestSubscription.cse, resourceID=TestSubscription.sub.resourceID)
		self.assertIsNotNone(sub)
		self.assertEqual(TestSubscription.sub.resourceID, sub.resourceID)
		self.assertEqual(TestSubscription.sub.notificationURI[0], sub.notificationURI[0])
		self.assertEqual(TestSubscription.sub.resourceName, sub.resourceName)


	def test_updateSubscriptionContainer(self):
		self.assertIsNotNone(TestSubscription.sub)
		TestSubscription.sub.expirationCounter = 10
		self.assertTrue(TestSubscription.sub.updateInCSE())
		self.assertEqual(TestSubscription.sub.expirationCounter, 10)


	def test_findSubscriptionContainer(self):
		self.assertIsNotNone(TestSubscription.cnt)
		self.assertIsNotNone(TestSubscription.sub)

		# Test finding all resources
		subs = TestSubscription.cnt.subscriptions()
		self.assertEqual(len(subs), 1)
		self.assertEqual(TestSubscription.sub.resourceID, subs[0].resourceID)

		# test finding a specific resource by the resourceName
		sub = TestSubscription.cnt.findSubscription(SUB_NAME)
		self.assertIsNotNone(sub)
		self.assertEqual(TestSubscription.sub.resourceID, sub.resourceID)


	def test_deleteSubscriptionContainer(self):
		self.assertIsNotNone(TestSubscription.sub)
		self.assertTrue(TestSubscription.sub.deleteFromCSE())

		# try to find it (should fail)
		sub = TestSubscription.cnt.findSubscription(SUB_NAME)
		self.assertIsNone(sub)


	def test_subscriptionCSE(self):
		sub = Subscription(TestSubscription.cse, notificationURI=[NOT_NU])
		self.assertIsNotNone(sub)
		self.assertTrue(sub.deleteFromCSE())


	def test_subscriptionAE(self):
		sub = Subscription(TestSubscription.ae, notificationURI=[NOT_NU])
		self.assertIsNotNone(sub)
		self.assertTrue(sub.deleteFromCSE())


	def test_subscriptionGroup(self):
		grp = Group(TestSubscription.ae, resources=[TestSubscription.cnt])
		self.assertIsNotNone(grp)
		sub = Subscription(grp, notificationURI=[NOT_NU])
		self.assertIsNotNone(sub)
		self.assertTrue(sub.deleteFromCSE())
		self.assertTrue(grp.deleteFromCSE())


	def test_subscriptionContentInstance(self):
		self.assertIsNotNone(TestSubscription.cnt.addContent(CIN_CONTENT))
		cin = TestSubscription.cnt.latestContentInstance()
		self.assertIsNotNone(cin)
		with self.assertRaises(EXC.CSEOperationError):
			sub = Subscription(cin, notificationURI=[NOT_NU])	# This should fail


	def test_finit(self):
		self.assertIsNotNone(TestSubscription.ae)
		self.assertTrue(TestSubscription.ae.deleteFromCSE())
		TestSubscription.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestSubscription('test_init'))
	suite.addTest(TestSubscription('test_createSubscriptionContainer'))
	suite.addTest(TestSubscription('test_retrieveSubscriptionContainer'))
	suite.addTest(TestSubscription('test_updateSubscriptionContainer'))
	suite.addTest(TestSubscription('test_findSubscriptionContainer'))
	suite.addTest(TestSubscription('test_deleteSubscriptionContainer'))
	suite.addTest(TestSubscription('test_subscriptionCSE'))
	suite.addTest(TestSubscription('test_subscriptionAE'))
	suite.addTest(TestSubscription('test_subscriptionGroup'))
	suite.addTest(TestSubscription('test_subscriptionContentInstance'))
	suite.addTest(TestSubscription('test_finit'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
