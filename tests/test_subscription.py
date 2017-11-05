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
from conf import *


class TestSubscription(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		TestSubscription.session = Session(host, originator, encoding)
		TestSubscription.cse = CSEBase(TestAE.session, CSE_ID)
		if not TestSubscription.session.connected:
			print('*** Not connected to CSE')
			exit()
		if TestSubscription.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()


	@classmethod
	def tearDownClass(self):
		if TestAE.ae:
			TestAE.ae.deleteFromCSE()
			TestAE.ae = None


	def test_init(self):
		self.assertTrue(TestSubscription.session.connected)
		self.assertIsNotNone(TestSubscription.session)
		self.assertIsNotNone(TestSubscription.cse)
		self.assertIsNotNone(TestSubscription.cse.resourceID)
		self.assertIsNotNone(TestSubscription.ae)
		self.assertIsNotNone(TestSubscription.ae.resourceID)
		self.assertIsNotNone(TestSubscription.cnt)
		self.assertIsNotNone(TestSubscription.cnt.resourceID)


# Test: Test to <contentInstance> should fail

	def test_finit(self):
		self.assertIsNotNone(TestSubscription.ae)
		self.assertTrue(TestSubscription.ae.deleteFromCSE())
		TestSubscription.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestSubscription('test_init'))

	suite.addTest(TestSubscription('test_finit'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
